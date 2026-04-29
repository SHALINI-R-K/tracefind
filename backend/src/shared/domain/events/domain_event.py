from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from shared.domain.value_objects.identifier import Identifier
from shared.domain.value_objects.timestamp import Timestamp


@dataclass(frozen=True)
class DomainEvent(ABC):
    event_id: Identifier = field(default_factory=Identifier.new)
    occurred_at: Timestamp = field(default_factory=Timestamp.now)

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def payload(self) -> dict[str, Any]: ...

    def to_envelope(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "name": self.name,
            "occurred_at": self.occurred_at.to_iso(),
            "payload": self.payload(),
        }
