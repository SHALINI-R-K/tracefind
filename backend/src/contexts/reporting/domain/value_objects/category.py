from __future__ import annotations

from dataclasses import dataclass

from shared.domain.exceptions.domain_exception import InvalidInputError

_ALLOWED = {
    "bag", "wallet", "phone", "laptop", "keys",
    "documents", "clothing", "jewelry", "book", "other",
}


@dataclass(frozen=True)
class Category:
    value: str

    def __post_init__(self) -> None:
        if self.value not in _ALLOWED:
            raise InvalidInputError(f"unknown category: {self.value}")

    @classmethod
    def from_optional(cls, raw: str | None) -> "Category | None":
        return cls(raw) if raw else None
