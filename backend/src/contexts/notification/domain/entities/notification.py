from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from contexts.notification.domain.value_objects.channel import NotificationType
from shared.domain.value_objects.identifier import NotificationId, UserId
from shared.domain.value_objects.timestamp import Timestamp

_NOTIFICATION_NS = uuid.UUID("c9b0d36a-1f9b-4f4f-8c4f-1d2c3d4e5f60")


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

    @classmethod
    def for_match(
        cls,
        *,
        user_id: UserId,
        match_id: str,
        payload: dict[str, Any],
        ttl_seconds: int,
    ) -> "Notification":
        # Deterministic id from (user_id, match_id) so retries dedupe at the
        # DynamoDB ConditionExpression layer instead of producing duplicate
        # rows + duplicate emails.
        deterministic = uuid.uuid5(_NOTIFICATION_NS, f"{user_id}:{match_id}")
        now = Timestamp.now()
        return cls(
            id=NotificationId(str(deterministic)),
            user_id=user_id,
            type=NotificationType.MATCH_FOUND,
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
