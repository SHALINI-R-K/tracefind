from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from contexts.notification.domain.entities.notification import Notification
from contexts.notification.domain.repositories.notification_repository import (
    NotificationRepository,
)
from contexts.notification.domain.services.email_sender import EmailSender
from contexts.notification.domain.value_objects.channel import NotificationType
from shared.domain.value_objects.identifier import UserId


@dataclass
class SendMatchNotificationCommand:
    repository: NotificationRepository
    email_sender: EmailSender
    ttl_seconds: int

    def execute(self, *, user_id: str, payload: dict[str, Any]) -> None:
        notification = Notification.create(
            user_id=UserId(user_id),
            type=NotificationType.MATCH_FOUND,
            payload=payload,
            ttl_seconds=self.ttl_seconds,
        )
        self.repository.save(notification)
        self.email_sender.send(
            to_user_id=user_id,
            subject="A possible match for your item",
            body_html=_render_email(payload),
        )


def _render_email(payload: dict[str, Any]) -> str:
    score = payload.get("score", 0)
    return f"""
    <html><body>
      <p>TraceFind found a possible match for one of your reports
      (similarity {score:.2f}).</p>
      <p>Sign in to review and confirm.</p>
    </body></html>
    """.strip()
