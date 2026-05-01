from __future__ import annotations

import os
from functools import lru_cache


@lru_cache(maxsize=8)
def env(key: str, default: str | None = None) -> str:
    val = os.environ.get(key, default)
    if val is None:
        raise RuntimeError(f"missing required env var {key}")
    return val


def items_table() -> str:
    return env("ITEMS_TABLE")


def matches_table() -> str:
    return env("MATCHES_TABLE")


def claims_table() -> str:
    return env("CLAIMS_TABLE")


def notifications_table() -> str:
    return env("NOTIFICATIONS_TABLE")


def audit_table() -> str:
    return env("AUDIT_TABLE")


def match_threshold() -> float:
    return float(env("MATCH_THRESHOLD", "0.70"))


def embedding_model_version() -> str:
    return env("EMBEDDING_MODEL_VERSION", "titan-mm-v1+titan-text-v2")


def ses_from_email() -> str:
    return env("SES_FROM_EMAIL")


def item_ttl_seconds() -> int:
    return int(env("ITEM_TTL_SECONDS", str(90 * 24 * 3600)))
