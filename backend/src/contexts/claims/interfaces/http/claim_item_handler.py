from __future__ import annotations

from typing import Any

from contexts.claims.application.commands.confirm_claim import ConfirmClaimCommand
from contexts.claims.infrastructure.persistence.dynamo_claim_repository import (
    DynamoClaimRepository,
)
from contexts.matching.infrastructure.persistence.dynamo_match_repository import (
    DynamoMatchRepository,
)
from contexts.reporting.infrastructure.persistence.dynamo_item_report_repository import (
    DynamoItemReportRepository,
)
from shared.application import config
from shared.application.http import (
    caller_user_id,
    handler,
    parse_body,
    response,
)
from shared.domain.exceptions.domain_exception import InvalidInputError

_command = ConfirmClaimCommand(
    claim_repo=DynamoClaimRepository(config.claims_table()),
    match_repo=DynamoMatchRepository(config.matches_table()),
    item_repo=DynamoItemReportRepository(config.items_table()),
    items_table_name=config.items_table(),
)


@handler
def lambda_handler(event: dict[str, Any]) -> dict[str, Any]:
    user_id = caller_user_id(event)
    item_id = (event.get("pathParameters") or {}).get("id")
    if not item_id:
        raise InvalidInputError("missing item id")
    body = parse_body(event)
    match_id = body.get("match_id")
    decision = body.get("decision", "confirm")
    if not match_id:
        raise InvalidInputError("match_id is required")

    result = _command.execute(
        item_id=item_id,
        match_id=match_id,
        decision=decision,
        caller_user_id=user_id,
    )
    return response(200, result)
