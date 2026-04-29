from __future__ import annotations

from enum import Enum

from shared.domain.exceptions.domain_exception import InvalidInputError


class ClaimDecision(str, Enum):
    CONFIRM = "confirm"
    REJECT = "reject"

    @classmethod
    def parse(cls, raw: str) -> "ClaimDecision":
        try:
            return cls(raw)
        except ValueError as exc:
            raise InvalidInputError(f"invalid decision: {raw}") from exc


class ClaimStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
