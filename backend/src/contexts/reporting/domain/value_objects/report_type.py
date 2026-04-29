from __future__ import annotations

from enum import Enum

from shared.domain.exceptions.domain_exception import InvalidInputError


class ReportType(str, Enum):
    LOST = "lost"
    FOUND = "found"

    @classmethod
    def parse(cls, raw: str) -> "ReportType":
        try:
            return cls(raw)
        except ValueError as exc:
            raise InvalidInputError(f"invalid report type: {raw}") from exc

    def opposite(self) -> "ReportType":
        return ReportType.FOUND if self is ReportType.LOST else ReportType.LOST
