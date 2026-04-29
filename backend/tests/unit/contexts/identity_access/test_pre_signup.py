import os
from unittest.mock import patch

import pytest

from src.contexts.identity_access.interfaces.cognito_triggers import pre_signup


def _event(email: str, captcha_token: str | None = None) -> dict:
    return {
        "request": {
            "userAttributes": {"email": email},
            "clientMetadata": {"captchaToken": captcha_token} if captcha_token else {},
        }
    }


def test_no_secret_passes_through(monkeypatch) -> None:
    monkeypatch.delenv("HCAPTCHA_SECRET", raising=False)
    event = _event("user@example.com")
    assert pre_signup.lambda_handler(event, None) is event


def test_internal_domain_bypasses(monkeypatch) -> None:
    monkeypatch.setenv("HCAPTCHA_SECRET", "x")
    event = _event("loadtest@tracefind-internal.local")
    assert pre_signup.lambda_handler(event, None) is event


def test_missing_token_rejects(monkeypatch) -> None:
    monkeypatch.setenv("HCAPTCHA_SECRET", "x")
    with pytest.raises(Exception, match="captchaToken required"):
        pre_signup.lambda_handler(_event("u@example.com"), None)


def test_failed_verify_rejects(monkeypatch) -> None:
    monkeypatch.setenv("HCAPTCHA_SECRET", "x")
    with patch.object(pre_signup, "_verify", return_value=False):
        with pytest.raises(Exception, match="captcha verification failed"):
            pre_signup.lambda_handler(_event("u@example.com", "tok"), None)


def test_passing_verify_succeeds(monkeypatch) -> None:
    monkeypatch.setenv("HCAPTCHA_SECRET", "x")
    event = _event("u@example.com", "tok")
    with patch.object(pre_signup, "_verify", return_value=True):
        assert pre_signup.lambda_handler(event, None) is event
