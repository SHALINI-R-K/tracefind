from __future__ import annotations

import logging

from contexts.identity_access.domain.repositories.user_directory import UserDirectory
from contexts.notification.domain.services.email_sender import EmailSender
from shared.domain.exceptions.domain_exception import UpstreamError
from shared.infrastructure.aws.boto3_clients import ses_client
from shared.infrastructure.logging.structured_logger import get_logger, log

_logger = get_logger("ses")


class SesEmailSender(EmailSender):
    def __init__(self, *, from_email: str, user_directory: UserDirectory) -> None:
        self._from = from_email
        self._users = user_directory

    def send(self, *, to_user_id: str, subject: str, body_html: str) -> None:
        email = self._users.email_for(to_user_id)
        if not email:
            log(_logger, logging.WARNING, "no_email_for_user", user_id=to_user_id)
            return
        try:
            ses_client().send_email(
                Source=self._from,
                Destination={"ToAddresses": [email]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {"Html": {"Data": body_html, "Charset": "UTF-8"}},
                },
            )
        except Exception as exc:  # noqa: BLE001
            raise UpstreamError(f"ses send failed: {exc}") from exc
