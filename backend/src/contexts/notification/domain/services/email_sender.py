from __future__ import annotations

from typing import Protocol


class EmailSender(Protocol):
    def send(self, *, to_user_id: str, subject: str, body_html: str) -> None: ...
