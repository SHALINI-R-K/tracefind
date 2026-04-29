from __future__ import annotations

import re
from dataclasses import dataclass

from shared.domain.exceptions.domain_exception import InvalidInputError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_RE.match(self.value):
            raise InvalidInputError(f"invalid email: {self.value}")
