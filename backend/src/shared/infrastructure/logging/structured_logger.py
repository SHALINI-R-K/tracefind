from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any

_REDACT_KEYS = {"image", "embedding", "password", "token"}


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        body: dict[str, Any] = {
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "extra_fields"):
            body.update(record.extra_fields)  # type: ignore[attr-defined]
        return json.dumps(_redact(body), default=str)


def _redact(body: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in body.items():
        if key in _REDACT_KEYS:
            redacted[key] = "<redacted>"
        elif isinstance(value, dict):
            redacted[key] = _redact(value)
        else:
            redacted[key] = value
    return redacted


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))
    logger.propagate = False
    return logger


def log(logger: logging.Logger, level: int, msg: str, **fields: Any) -> None:
    record = logger.makeRecord(
        logger.name, level, fn="", lno=0, msg=msg, args=(), exc_info=None
    )
    record.extra_fields = fields  # type: ignore[attr-defined]
    logger.handle(record)
