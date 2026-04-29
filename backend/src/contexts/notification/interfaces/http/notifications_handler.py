from __future__ import annotations

from typing import Any

from contexts.notification.application.queries.list_notifications import (
    ListNotificationsQuery,
)
from contexts.notification.infrastructure.persistence.dynamo_notification_repository import (
    DynamoNotificationRepository,
)
from shared.application import config
from shared.application.http import (
    caller_user_id,
    handler,
    response,
)
from shared.domain.exceptions.domain_exception import InvalidInputError
from shared.domain.value_objects.identifier import NotificationId, UserId

_repo = DynamoNotificationRepository(config.notifications_table())
_list_query = ListNotificationsQuery(repository=_repo)


@handler
def list_handler(event: dict[str, Any]) -> dict[str, Any]:
    user_id = caller_user_id(event)
    qs = event.get("queryStringParameters") or {}
    limit = min(int(qs.get("limit", "20")), 100)
    cursor = qs.get("cursor")
    items, next_cursor = _list_query.execute(user_id, limit=limit, cursor=cursor)
    return response(200, {"notifications": items, "next_cursor": next_cursor})


@handler
def mark_read_handler(event: dict[str, Any]) -> dict[str, Any]:
    user_id = caller_user_id(event)
    nid = (event.get("pathParameters") or {}).get("id")
    if not nid:
        raise InvalidInputError("missing notification id")
    _repo.mark_read(NotificationId(nid), UserId(user_id))
    return response(200, {"id": nid, "read": True})
