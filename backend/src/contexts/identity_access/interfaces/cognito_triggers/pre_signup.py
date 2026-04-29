from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from shared.infrastructure.logging.structured_logger import get_logger, log
import logging

_logger = get_logger("cognito.pre_signup")
_HCAPTCHA_SECRET_ENV = "HCAPTCHA_SECRET"
_HCAPTCHA_VERIFY_URL = "https://hcaptcha.com/siteverify"
_BYPASS_DOMAINS = {"@tracefind-internal.local"}


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    """Cognito Pre Sign-up trigger.

    Validates an hCaptcha token supplied via clientMetadata.captchaToken.
    Set HCAPTCHA_SECRET to enable; if unset, the trigger no-ops (dev/local).
    """
    secret = os.environ.get(_HCAPTCHA_SECRET_ENV)
    if not secret:
        log(_logger, logging.WARNING, "captcha_disabled")
        return event

    email = (event.get("request", {}).get("userAttributes", {}) or {}).get("email", "")
    if any(email.endswith(domain) for domain in _BYPASS_DOMAINS):
        return event

    metadata = event.get("request", {}).get("clientMetadata") or {}
    token = metadata.get("captchaToken")
    if not token:
        raise Exception("captchaToken required")

    if not _verify(secret, token):
        log(_logger, logging.WARNING, "captcha_failed", email=email)
        raise Exception("captcha verification failed")

    return event


def _verify(secret: str, token: str) -> bool:
    body = urllib.parse.urlencode({"secret": secret, "response": token}).encode()
    req = urllib.request.Request(_HCAPTCHA_VERIFY_URL, data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            payload = json.loads(resp.read().decode())
            return bool(payload.get("success"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        log(_logger, logging.ERROR, "captcha_verify_error", error=str(exc))
        return False
