from __future__ import annotations

import logging
import os
from functools import lru_cache

import boto3

from contexts.identity_access.domain.repositories.user_directory import UserDirectory
from shared.infrastructure.aws.boto3_clients import _BOTO_CONFIG  # type: ignore[attr-defined]
from shared.infrastructure.logging.structured_logger import get_logger, log

_logger = get_logger("cognito.user_directory")


@lru_cache(maxsize=1)
def _cognito_client():
    return boto3.client(
        "cognito-idp",
        config=_BOTO_CONFIG,
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )


class CognitoUserDirectory(UserDirectory):
    def __init__(self, user_pool_id: str | None = None) -> None:
        self._user_pool_id = user_pool_id or os.environ.get("COGNITO_USER_POOL_ID", "")

    def email_for(self, user_id: str) -> str | None:
        if not self._user_pool_id:
            return None
        try:
            resp = _cognito_client().admin_get_user(
                UserPoolId=self._user_pool_id,
                Username=user_id,
            )
        except Exception as exc:  # noqa: BLE001
            log(_logger, logging.WARNING, "user_lookup_failed", user_id=user_id, error=str(exc))
            return None
        for attr in resp.get("UserAttributes", []):
            if attr.get("Name") == "email":
                return attr.get("Value")
        return None
