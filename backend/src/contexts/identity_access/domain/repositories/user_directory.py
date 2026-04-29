from __future__ import annotations

from typing import Protocol


class UserDirectory(Protocol):
    def email_for(self, user_id: str) -> str | None: ...
