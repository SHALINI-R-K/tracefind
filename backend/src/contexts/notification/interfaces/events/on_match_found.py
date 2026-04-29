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
_repo = DynamoNotificationRepository(config.notifications_table())
_sender = SesEmailSender(
    from_email=config.ses_from_email(),
    user_directory=CognitoUserDirectory(),
)
_command = SendMatchNotificationCommand(
    repository=_repo,
    email_sender=_sender,
    ttl_seconds=config.item_ttl_seconds(),
)


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    sent = 0
    for record in event.get("Records", []):
        if record.get("eventName") != "INSERT":
            continue
        new_image = record.get("dynamodb", {}).get("NewImage", {})
        match_id = (new_image.get("id") or {}).get("S")
        score = float((new_image.get("score") or {}).get("N", "0"))
        lost_item_id = (new_image.get("lost_item_id") or {}).get("S")
        found_item_id = (new_image.get("found_item_id") or {}).get("S")
        if not match_id:
            continue

        for user_id in _resolve_recipients(lost_item_id, found_item_id):
            try:
                _command.execute(
                    user_id=user_id,
                    payload={
                        "match_id": match_id,
                        "lost_item_id": lost_item_id,
                        "found_item_id": found_item_id,
                        "score": score,
                    },
                )
                sent += 1
            except Exception as exc:  # noqa: BLE001
                log(
                    _logger,
                    logging.ERROR,
                    "notification_failed",
                    match_id=match_id,
                    user_id=user_id,
                    error=str(exc),
                )
    return {"sent": sent}


def _resolve_recipients(lost_item_id: str | None, found_item_id: str | None) -> list[str]:
    from contexts.reporting.infrastructure.persistence.dynamo_item_report_repository import (
        DynamoItemReportRepository,
    )
    from shared.domain.value_objects.identifier import ItemId

    repo = DynamoItemReportRepository(config.items_table())
    recipients: set[str] = set()
    for iid in (lost_item_id, found_item_id):
        if not iid:
            continue
        try:
            r = repo.get(ItemId(iid))
            recipients.add(str(r.user_id))
        except Exception as exc:  # noqa: BLE001
            log(_logger, logging.WARNING, "recipient_lookup_failed", item_id=iid, error=str(exc))
    return list(recipients)
