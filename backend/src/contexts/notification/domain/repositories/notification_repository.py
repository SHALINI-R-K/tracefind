from __future__ import annotations

from typing import Protocol

from contexts.notification.domain.entities.notification import Notification
from shared.domain.value_objects.identifier import NotificationId, UserId


class NotificationRepository(Protocol):
    def save(self, notification: Notification) -> None: ...

    def get(self, notification_id: NotificationId) -> Notification: ...

    def list_for_user(
        self, user_id: UserId, *, limit: int, cursor: str | None
    ) -> tuple[list[Notification], str | None]: ...

    def mark_read(self, notification_id: NotificationId, user_id: UserId) -> None: ...
