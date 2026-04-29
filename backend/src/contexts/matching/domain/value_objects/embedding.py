from __future__ import annotations

import math
from dataclasses import dataclass

from shared.domain.exceptions.domain_exception import InvalidInputError


@dataclass(frozen=True)
class Embedding:
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.values:
            raise InvalidInputError("embedding cannot be empty")

    def cosine(self, other: "Embedding") -> float:
        if len(self.values) != len(other.values):
            raise InvalidInputError("embedding dimensions do not match")
        dot = sum(a * b for a, b in zip(self.values, other.values))
        na = math.sqrt(sum(a * a for a in self.values))
        nb = math.sqrt(sum(b * b for b in other.values))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)
