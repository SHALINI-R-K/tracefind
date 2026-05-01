from __future__ import annotations

from dataclasses import dataclass

from shared.domain.exceptions.domain_exception import InvalidInputError

_ALLOWED = {
    "accessory", "backpack", "bag", "book", "bottle",
    "camera", "card", "charger", "clothing", "documents",
    "earphones", "glasses", "headphones", "jacket", "jewelry",
    "keys", "laptop", "pen", "phone", "shoes",
    "tablet", "umbrella", "wallet", "watch", "other",
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
