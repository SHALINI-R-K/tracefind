from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.domain.value_objects.identifier import Identifier
from shared.domain.value_objects.timestamp import Timestamp


@dataclass
class AuditEntry:
    id: Identifier
    actor_user_id: str
    action: str
    target_id: str
    before: dict[str, Any]
    after: dict[str, Any]
    created_at: Timestamp

    @classmethod
    def record(
        cls,
        *,
        actor_user_id: str,
        action: str,
        target_id: str,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
    ) -> "AuditEntry":
        return cls(
            id=Identifier.new(),
            actor_user_id=actor_user_id,
            action=action,
            target_id=target_id,
            before=before or {},
            after=after or {},
            created_at=Timestamp.now(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "actor_user_id": self.actor_user_id,
            "action": self.action,
            "target_id": self.target_id,
            "before": self.before,
            "after": self.after,
            "created_at": self.created_at.to_iso(),
        }
