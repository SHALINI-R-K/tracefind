from __future__ import annotations

from typing import Any

from contexts.matching.application.queries.list_matches_for_item import (
    ListMatchesForItemQuery,
)
from contexts.matching.infrastructure.persistence.dynamo_match_repository import (
    DynamoMatchRepository,
)
from contexts.reporting.infrastructure.persistence.dynamo_item_report_repository import (
    DynamoItemReportRepository,
)
from shared.application import config
from shared.application.http import (
    caller_groups,
    caller_user_id,
    handler,
    response,
)
from shared.domain.exceptions.domain_exception import InvalidInputError

_query = ListMatchesForItemQuery(
    match_repo=DynamoMatchRepository(config.matches_table()),
    item_repo=DynamoItemReportRepository(config.items_table()),
)


@handler
def lambda_handler(event: dict[str, Any]) -> dict[str, Any]:
    user_id = caller_user_id(event)
    is_admin = "admin" in caller_groups(event)
    item_id = (event.get("pathParameters") or {}).get("id")
    if not item_id:
        raise InvalidInputError("missing item id")
    qs = event.get("queryStringParameters") or {}
    min_score = float(qs.get("min_score", "0.0"))
    limit = min(int(qs.get("limit", "20")), 100)
    matches = _query.execute(
        item_id, user_id, is_admin, min_score=min_score, limit=limit
    )
    return response(200, {"matches": matches})
