from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from contexts.reporting.domain.value_objects.report_type import ReportType
from shared.domain.events.domain_event import DomainEvent
from shared.domain.value_objects.identifier import Identifier, ItemId, UserId
from shared.domain.value_objects.timestamp import Timestamp


@dataclass(frozen=True)
class ItemReported(DomainEvent):
    item_id: ItemId = None  # type: ignore[assignment]
    user_id: UserId = None  # type: ignore[assignment]
    type: ReportType = None  # type: ignore[assignment]
    category: str | None = None
    event_id: Identifier = field(default_factory=Identifier.new)
    occurred_at: Timestamp = field(default_factory=Timestamp.now)

    @property
    def name(self) -> str:
        return "reporting.item_reported"

    def payload(self) -> dict[str, Any]:
        return {
            "item_id": str(self.item_id),
            "user_id": str(self.user_id),
            "type": self.type.value,
            "category": self.category,
        }
