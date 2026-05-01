from __future__ import annotations

from typing import Any

from contexts.admin.application.commands.moderate_report import (
    ModerateReportCommand,
)
from contexts.admin.application.commands.override_match import OverrideMatchCommand
from contexts.admin.application.queries.list_reports import (
    AdminAuditQuery,
    AdminListReportsQuery,
)
from contexts.admin.infrastructure.persistence.dynamo_audit_repository import (
    DynamoAuditRepository,
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
    require_admin,
    response,
)
from shared.domain.exceptions.domain_exception import InvalidInputError

_audit = DynamoAuditRepository(config.audit_table())
_items = DynamoItemReportRepository(config.items_table())
_matches = DynamoMatchRepository(config.matches_table())

_moderate = ModerateReportCommand(item_repo=_items, audit_repo=_audit)
_override = OverrideMatchCommand(item_repo=_items, match_repo=_matches, audit_repo=_audit)
_list_reports = AdminListReportsQuery(items_table_name=config.items_table())
_audit_query = AdminAuditQuery(audit_repo=_audit)


@handler
def list_reports_handler(event: dict[str, Any]) -> dict[str, Any]:
    require_admin(event)
    qs = event.get("queryStringParameters") or {}
    status = qs.get("status")
    limit = min(int(qs.get("limit", "50")), 200)
    cursor = qs.get("cursor")
    reports, next_cursor = _list_reports.execute(status=status, limit=limit, cursor=cursor)
    return response(200, {"reports": reports, "next_cursor": next_cursor})


@handler
def archive_item_handler(event: dict[str, Any]) -> dict[str, Any]:
    require_admin(event)
    actor = caller_user_id(event)
    item_id = (event.get("pathParameters") or {}).get("id")
    if not item_id:
        raise InvalidInputError("missing item id")
    body = parse_body(event)
    reason = body.get("reason", "")
    result = _moderate.archive(item_id=item_id, actor_user_id=actor, reason=reason)
    return response(200, result)


@handler
def override_match_handler(event: dict[str, Any]) -> dict[str, Any]:
    require_admin(event)
    actor = caller_user_id(event)
    item_id = (event.get("pathParameters") or {}).get("id")
    body = parse_body(event)
    reason = body.get("reason", "")
    counterpart_id = body.get("counterpart_id")
    direction = body.get("direction", "lost")
    if not item_id or not counterpart_id:
        raise InvalidInputError("item id and counterpart_id are required")
    if direction == "lost":
        result = _override.force(
            lost_item_id=item_id,
            found_item_id=counterpart_id,
            actor_user_id=actor,
            reason=reason,
        )
    else:
        result = _override.force(
            lost_item_id=counterpart_id,
            found_item_id=item_id,
            actor_user_id=actor,
            reason=reason,
        )
    return response(201, result)


@handler
def reject_match_handler(event: dict[str, Any]) -> dict[str, Any]:
    require_admin(event)
    actor = caller_user_id(event)
    match_id = (event.get("pathParameters") or {}).get("id")
    if not match_id:
        raise InvalidInputError("missing match id")
    body = parse_body(event)
    reason = body.get("reason", "")
    result = _override.delete(match_id=match_id, actor_user_id=actor, reason=reason)
    return response(200, result)


@handler
def audit_query_handler(event: dict[str, Any]) -> dict[str, Any]:
    require_admin(event)
    qs = event.get("queryStringParameters") or {}
    actor_filter = qs.get("actor")
    target_filter = qs.get("target")
    limit = min(int(qs.get("limit", "50")), 200)
    cursor = qs.get("cursor")
    entries, next_cursor = _audit_query.execute(
        actor_user_id=actor_filter,
        target_id=target_filter,
        limit=limit,
        cursor=cursor,
    )
    return response(200, {"entries": entries, "next_cursor": next_cursor})
