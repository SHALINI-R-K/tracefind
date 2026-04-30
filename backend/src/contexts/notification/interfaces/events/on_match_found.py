from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from contexts.identity_access.infrastructure.cognito.cognito_user_directory import (
    CognitoUserDirectory,
)
from contexts.notification.application.commands.send_match_notification import (
    SendMatchNotificationCommand,
)
from contexts.notification.infrastructure.persistence.dynamo_notification_repository import (
    DynamoNotificationRepository,
)
from contexts.notification.infrastructure.ses.ses_email_sender import SesEmailSender
from shared.application import config
from shared.infrastructure.logging.structured_logger import get_logger, log

_logger = get_logger("notification.on_match_found")
def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    try:
        return _process_event(event)
    except Exception as exc:
        log(_logger, logging.CRITICAL, "lambda_initialization_failed", error=str(exc))
        return {"error": str(exc)}


def _process_event(event: dict[str, Any]) -> dict[str, Any]:
    sent = 0
    # Lazy init to avoid module-level crashes if env vars are missing
    repo = DynamoNotificationRepository(config.notifications_table())
    sender = SesEmailSender(
        from_email=config.ses_from_email(),
        user_directory=CognitoUserDirectory(),
    )
    command = SendMatchNotificationCommand(
        repository=repo,
        email_sender=sender,
        ttl_seconds=config.item_ttl_seconds(),
    )

    for record in event.get("Records", []):
        log(_logger, logging.INFO, "processing_record", event_name=record.get("eventName"))
        if record.get("eventName") not in ["INSERT", "MODIFY"]:
            continue
            
        new_image = record.get("dynamodb", {}).get("NewImage", {})
        match_id = (new_image.get("id") or {}).get("S")
        score_str = (new_image.get("score") or {}).get("N", "0")
        score = Decimal(score_str)
        lost_item_id = (new_image.get("lost_item_id") or {}).get("S")
        found_item_id = (new_image.get("found_item_id") or {}).get("S")
        
        log(_logger, logging.INFO, "parsed_match", 
            match_id=match_id, lost_id=lost_item_id, found_id=found_item_id)
        
        if not all([match_id, lost_item_id, found_item_id]):
            log(_logger, logging.WARNING, "missing_fields", match_id=match_id)
            continue

        # Fetch both reports
        lost_report, found_report = _get_reports(lost_item_id, found_item_id) # type: ignore
        if not lost_report or not found_report:
            log(_logger, logging.ERROR, "reports_missing", 
                match_id=match_id, lost_id=lost_item_id, found_id=found_item_id,
                lost_found=(bool(lost_report), bool(found_report)))
            continue

        user_dir = CognitoUserDirectory()
        lost_email = user_dir.email_for(str(lost_report.user_id))
        found_email = user_dir.email_for(str(found_report.user_id))

        # Notify participants
        participants = [
            (str(lost_report.user_id), found_email, found_report.description.value, "lost"),
            (str(found_report.user_id), lost_email, lost_report.description.value, "found")
        ]

        for user_id, other_email, other_desc, item_type in participants:
            try:
                command.execute(
                    user_id=user_id,
                    payload={
                        "match_id": match_id,
                        "score": score,
                        "other_party_email": other_email or "Contact via app",
                        "other_item_description": other_desc,
                        "item_type": item_type,
                    }
                )
                sent += 1
            except Exception as exc: # noqa: BLE001
                log(_logger, logging.ERROR, "notify_user_failed", 
                    match_id=match_id, user_id=user_id, error=str(exc))

    return {"sent": sent}


def _get_reports(lost_id: str, found_id: str) -> tuple[Any, Any]:
    from contexts.reporting.infrastructure.persistence.dynamo_item_report_repository import (
        DynamoItemReportRepository,
    )
    from shared.domain.value_objects.identifier import ItemId

    repo = DynamoItemReportRepository(config.items_table())
    try:
        lost = repo.get(ItemId(lost_id))
        found = repo.get(ItemId(found_id))
        return lost, found
    except Exception as exc:
        log(_logger, logging.ERROR, "get_reports_failed", error=str(exc))
        return None, None
