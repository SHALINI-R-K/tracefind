from __future__ import annotations

import json
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from contexts.identity_access.domain.repositories.user_directory import UserDirectory
from contexts.notification.domain.services.email_sender import EmailSender
from shared.domain.exceptions.domain_exception import UpstreamError
from shared.infrastructure.aws.secrets import get_secret
from shared.infrastructure.logging.structured_logger import get_logger, log

_logger = get_logger("smtp.gmail")

_SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
_SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
_SMTP_TIMEOUT = float(os.environ.get("SMTP_TIMEOUT_SECONDS", "5"))
_SMTP_SECRET_NAME = os.environ.get("SMTP_SECRET_NAME", "tracefind/gmail-smtp")


class GmailSmtpEmailSender(EmailSender):
    """Send transactional email via Gmail SMTP using an App Password.

    Secret in AWS Secrets Manager (id = SMTP_SECRET_NAME) must be a JSON
    string with `username` (the Gmail address) and `app_password` (a 16-char
    App Password generated in Google Account → Security → 2-Step Verification).
    """

    def __init__(self, *, from_email: str, user_directory: UserDirectory) -> None:
        self._from = from_email
        self._users = user_directory

    def send(self, *, to_user_id: str, subject: str, body_html: str) -> None:
        email = self._users.email_for(to_user_id)
        if not email:
            log(_logger, logging.WARNING, "no_email_for_user", user_id=to_user_id)
            return

        username, app_password = _load_credentials()

        msg = MIMEMultipart("alternative")
        msg["From"] = self._from
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body_html, "html", "utf-8"))

        try:
            with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=_SMTP_TIMEOUT) as server:
                server.starttls()
                server.login(username, app_password)
                server.send_message(msg)
        except smtplib.SMTPException as exc:
            raise UpstreamError(f"gmail smtp send failed: {exc}") from exc
        except OSError as exc:
            raise UpstreamError(f"gmail smtp connection failed: {exc}") from exc


def _load_credentials() -> tuple[str, str]:
    raw = get_secret(_SMTP_SECRET_NAME)
    try:
        data = json.loads(raw)
        return data["username"], data["app_password"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise UpstreamError(
            f"SMTP secret {_SMTP_SECRET_NAME} must be JSON with "
            "`username` and `app_password` keys"
        ) from exc
