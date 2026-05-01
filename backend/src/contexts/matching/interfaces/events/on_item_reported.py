from __future__ import annotations

import logging
from typing import Any

from contexts.matching.application.commands.run_matching import RunMatchingCommand
from contexts.matching.domain.services.matching_service import MatchingService
from contexts.matching.domain.value_objects.similarity_score import MatchThreshold
from contexts.matching.infrastructure.persistence.dynamo_match_repository import (
    DynamoMatchRepository,
)
from contexts.reporting.infrastructure.persistence.dynamo_item_report_repository import (
    DynamoItemReportRepository,
)
from shared.application import config
from shared.infrastructure.event_bus.dynamodb_stream_event_bus import StreamEventBus
from shared.infrastructure.logging.structured_logger import get_logger, log

_logger = get_logger("matching.on_item_reported")
_item_repo = DynamoItemReportRepository(config.items_table())
_match_repo = DynamoMatchRepository(config.matches_table())
_command = RunMatchingCommand(
    item_repo=_item_repo,
    match_repo=_match_repo,
    matching_service=MatchingService(threshold=MatchThreshold(config.match_threshold())),
    event_bus=StreamEventBus(),
)


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    processed = 0
    failures: list[dict[str, str]] = []
    for record in event.get("Records", []):
        if record.get("eventName") != "INSERT":
            continue
        new_image = record.get("dynamodb", {}).get("NewImage", {})
        item_id = (new_image.get("id") or {}).get("S")
        status = (new_image.get("status") or {}).get("S")
        if not item_id or status != "active":
            continue
        try:
            matches = _command.execute(item_id)
            log(
                _logger,
                logging.INFO,
                "matching_complete",
                item_id=item_id,
                matches=len(matches),
            )
            processed += 1
        except Exception as exc:  # noqa: BLE001
            log(_logger, logging.ERROR, "matching_failed", item_id=item_id, error=str(exc))
            sequence_number = (record.get("dynamodb") or {}).get("SequenceNumber")
            if sequence_number:
                failures.append({"itemIdentifier": sequence_number})

    # Partial-batch response: failed records are retried (and ultimately go to DLQ
    # if the event source mapping is wired with onFailure → SQS). Successful
    # records are NOT retried, so a single bad item doesn't block the batch.
    if failures:
        return {"batchItemFailures": failures, "processed": processed}
    return {"processed": processed}
