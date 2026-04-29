from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Identifier:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("identifier value cannot be empty")
        try:
            uuid.UUID(self.value)
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"identifier must be a valid UUID: {self.value}") from exc

    @classmethod
    def new(cls) -> "Identifier":
        return cls(str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class UserId(Identifier):
    pass


@dataclass(frozen=True)
class ItemId(Identifier):
    pass


@dataclass(frozen=True)
class MatchId(Identifier):
    pass


@dataclass(frozen=True)
class ClaimId(Identifier):
    pass


@dataclass(frozen=True)
class NotificationId(Identifier):
    pass
