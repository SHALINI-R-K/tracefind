from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from contexts.notification.domain.repositories.notification_repository import (
    NotificationRepository,
)
from shared.domain.value_objects.identifier import UserId


@dataclass
class ListNotificationsQuery:
    repository: NotificationRepository

    def execute(
        self, user_id: str, *, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[dict[str, Any]], str | None]:
        notifications, next_cursor = self.repository.list_for_user(
            UserId(user_id), limit=limit, cursor=cursor
        )
        return [n.to_dict() for n in notifications], next_cursor
