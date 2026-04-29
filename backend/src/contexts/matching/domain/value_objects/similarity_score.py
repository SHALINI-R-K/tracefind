from __future__ import annotations

from dataclasses import dataclass

from shared.domain.exceptions.domain_exception import InvalidInputError


@dataclass(frozen=True, order=True)
class SimilarityScore:
    value: float

    def __post_init__(self) -> None:
        if not -1.0 <= self.value <= 1.0:
            raise InvalidInputError(f"similarity must be in [-1, 1]: {self.value}")

    def above(self, threshold: "MatchThreshold") -> bool:
        return self.value >= threshold.value


@dataclass(frozen=True)
class MatchThreshold:
    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise InvalidInputError(f"threshold must be in [0, 1]: {self.value}")
