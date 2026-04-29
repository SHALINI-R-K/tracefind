from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shared.domain.events.domain_event import DomainEvent
from shared.domain.value_objects.identifier import Identifier, ItemId
from shared.domain.value_objects.timestamp import Timestamp


@dataclass(frozen=True)
class ReportStatusChanged(DomainEvent):
    item_id: ItemId = None  # type: ignore[assignment]
    from_status: str = ""
    to_status: str = ""
    event_id: Identifier = field(default_factory=Identifier.new)
    occurred_at: Timestamp = field(default_factory=Timestamp.now)

    @property
    def name(self) -> str:
        return "reporting.status_changed"

    def payload(self) -> dict[str, Any]:
        return {
            "item_id": str(self.item_id),
            "from": self.from_status,
            "to": self.to_status,
        }
