from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from shared.infrastructure.logging.structured_logger import get_logger, log

from contexts.notification.domain.entities.notification import Notification
from contexts.notification.domain.repositories.notification_repository import (
    NotificationRepository,
)
from contexts.notification.domain.services.email_sender import EmailSender
from shared.domain.exceptions.domain_exception import ConflictError
from shared.domain.value_objects.identifier import UserId

_logger = get_logger("notification.send_match_notification")


@dataclass
class SendMatchNotificationCommand:
    repository: NotificationRepository
    email_sender: EmailSender
    ttl_seconds: int

    def execute(self, *, user_id: str, payload: dict[str, Any]) -> None:
        match_id = payload.get("match_id")
        if not match_id:
            raise ValueError("payload.match_id is required for idempotent send")

        notification = Notification.for_match(
            user_id=UserId(user_id),
            match_id=str(match_id),
            payload=payload,
            ttl_seconds=self.ttl_seconds,
        )
        try:
            self.repository.save(notification)
        except ConflictError:
            # Stream retry / batch redelivery — already notified this user for
            # this match. Skip email so we don't double-send.
            log(
                _logger,
                logging.INFO,
                "duplicate_notification_skipped",
                user_id=user_id,
                match_id=match_id,
            )
            return

        try:
            self.email_sender.send(
                to_user_id=user_id,
                subject="A possible match for your item",
                body_html=_render_email(payload),
            )
        except Exception as exc:
            # We log but don't re-raise, so in-app notification is still considered successful
            log(_logger, logging.WARNING, "email_delivery_failed", user_id=user_id, error=str(exc))


def _render_email(payload: dict[str, Any]) -> str:
    score = payload.get("score", 0)
    email = payload.get("other_party_email", "N/A")
    description = payload.get("other_item_description", "No description")
    item_type = payload.get("item_type", "item")
    
    other_type = "found" if item_type == "lost" else "lost"
    
    return f"""
    <html><body>
      <h2>Good news! A match was found.</h2>
      <p>TraceFind found a possible match for your {item_type} report
      (similarity score: {score:.2f}).</p>
      
      <h3>Other Party Contact Details</h3>
      <p><b>Email:</b> {email}</p>
      
      <h3>Their Item Description</h3>
      <p>{description}</p>
      
      <p>Sign in to your dashboard to review and confirm the match.</p>
    </body></html>
    """.strip()
