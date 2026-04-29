from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from contexts.notification.domain.value_objects.channel import NotificationType
from shared.domain.value_objects.identifier import NotificationId, UserId
from shared.domain.value_objects.timestamp import Timestamp


@dataclass
class Notification:
    id: NotificationId
    user_id: UserId
    type: NotificationType
    payload: dict[str, Any]
    read: bool
    created_at: Timestamp
    ttl: int

    @classmethod
    def create(
        cls,
        *,
        user_id: UserId,
        type: NotificationType,
        payload: dict[str, Any],
        ttl_seconds: int,
    ) -> "Notification":
        now = Timestamp.now()
        return cls(
            id=NotificationId.new(),
            user_id=user_id,
            type=type,
            payload=payload,
            read=False,
            created_at=now,
            ttl=now.epoch_seconds() + ttl_seconds,
        )

    def mark_read(self) -> None:
        self.read = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.type.value,
            "payload": self.payload,
            "read": self.read,
            "created_at": self.created_at.to_iso(),
        }
