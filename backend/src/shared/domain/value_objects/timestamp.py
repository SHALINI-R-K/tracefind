from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Timestamp:
    value: datetime

    def __post_init__(self) -> None:
        if self.value.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")

    @classmethod
    def now(cls) -> "Timestamp":
        return cls(datetime.now(timezone.utc))

    @classmethod
    def from_iso(cls, iso: str) -> "Timestamp":
        return cls(datetime.fromisoformat(iso))

    def to_iso(self) -> str:
        return self.value.isoformat()

    def epoch_seconds(self) -> int:
        return int(self.value.timestamp())
