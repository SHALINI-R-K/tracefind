from __future__ import annotations

from dataclasses import dataclass

from shared.domain.exceptions.domain_exception import InvalidInputError

_MIN_LEN = 5
_MAX_LEN = 500


@dataclass(frozen=True)
class Description:
    value: str

    def __post_init__(self) -> None:
        cleaned = self.value.strip()
        if len(cleaned) < _MIN_LEN:
            raise InvalidInputError(f"description must be at least {_MIN_LEN} characters")
        if len(cleaned) > _MAX_LEN:
            raise InvalidInputError(f"description must be at most {_MAX_LEN} characters")
        object.__setattr__(self, "value", cleaned)
