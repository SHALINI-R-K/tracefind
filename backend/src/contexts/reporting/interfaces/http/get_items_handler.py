from __future__ import annotations

from dataclasses import asdict
from typing import Any

from contexts.reporting.application.queries.get_item_report import (
    GetItemReportQuery,
)
from contexts.reporting.application.queries.list_user_reports import (
    ListUserReportsQuery,
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

_repo = DynamoItemReportRepository(config.items_table())
_list_query = ListUserReportsQuery(repository=_repo)
_get_query = GetItemReportQuery(repository=_repo)


@handler
def lambda_handler(event: dict[str, Any]) -> dict[str, Any]:
    user_id = caller_user_id(event)
    is_admin = "admin" in caller_groups(event)
    path_params = event.get("pathParameters") or {}
    qs = event.get("queryStringParameters") or {}

    item_id = path_params.get("id")
    if item_id:
        view = _get_query.execute(item_id, user_id, is_admin)
        return response(200, asdict(view))

    limit = min(int(qs.get("limit", "20")), 100)
    cursor = qs.get("cursor")
    views, next_cursor = _list_query.execute(user_id, limit=limit, cursor=cursor)
    return response(
        200,
        {"items": [asdict(v) for v in views], "next_cursor": next_cursor},
    )
