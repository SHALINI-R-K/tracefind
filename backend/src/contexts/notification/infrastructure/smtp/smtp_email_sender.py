from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from contexts.identity_access.domain.repositories.user_directory import UserDirectory
from contexts.notification.domain.services.email_sender import EmailSender
from shared.domain.exceptions.domain_exception import UpstreamError
from shared.infrastructure.logging.structured_logger import get_logger, log

_logger = get_logger("smtp")


class SmtpEmailSender(EmailSender):
    def __init__(
        self,
        *,
        server: str,
        port: int,
        user: str,
        password: str,
        user_directory: UserDirectory,
    ) -> None:
        self._server = server
        self._port = port
        self._user = user
        self._password = password
        self._users = user_directory

    def send(self, *, to_user_id: str, subject: str, body_html: str) -> None:
        email = self._users.email_for(to_user_id)
        if not email:
            log(_logger, logging.WARNING, "no_email_for_user", user_id=to_user_id)
            return

        msg = MIMEMultipart()
        msg["From"] = self._user
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body_html, "html"))

        try:
            with smtplib.SMTP(self._server, self._port) as server:
                server.starttls()
                server.login(self._user, self._password)
                server.send_message(msg)
        except Exception as exc:  # noqa: BLE001
            raise UpstreamError(f"smtp send failed: {exc}") from exc
