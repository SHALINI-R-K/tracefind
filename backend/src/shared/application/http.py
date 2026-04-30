from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Callable

from shared.domain.exceptions.domain_exception import (
    ConflictError,
    DomainError,
    ForbiddenError,
    InvalidInputError,
    NotFoundError,
    UpstreamError,
)
from shared.infrastructure.logging.structured_logger import get_logger, log
import logging

_logger = get_logger("http")

_STATUS_FOR = {
    InvalidInputError: 400,
    ForbiddenError: 403,
    NotFoundError: 404,
    ConflictError: 409,
    UpstreamError: 502,
}


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def response(status: int, body: dict[str, Any] | list[Any]) -> dict[str, Any]:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, cls=DecimalEncoder),
    }


def error_response(err: Exception) -> dict[str, Any]:
    if isinstance(err, DomainError):
        status = _STATUS_FOR.get(type(err), 500)
        return response(
            status,
            {"error": {"code": err.code, "message": str(err) or err.code}},
        )
    log(_logger, logging.ERROR, "unhandled_error", error=str(err), error_type=type(err).__name__)
    return response(500, {"error": {"code": "INTERNAL_ERROR", "message": "internal error"}})


def parse_body(event: dict[str, Any]) -> dict[str, Any]:
    raw = event.get("body") or "{}"
    try:
        body = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InvalidInputError(f"invalid JSON body: {exc}") from exc
    if not isinstance(body, dict):
        raise InvalidInputError("body must be a JSON object")
    return body


def caller_user_id(event: dict[str, Any]) -> str:
    claims = (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
    )
    sub = claims.get("sub")
    if not sub:
        raise ForbiddenError("missing user identity")
    return sub


def caller_groups(event: dict[str, Any]) -> list[str]:
    claims = (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
    )
    raw = claims.get("cognito:groups", "")
    if isinstance(raw, list):
        return [str(g) for g in raw]
    if isinstance(raw, str) and raw:
        return [g.strip() for g in raw.strip("[]").split(",") if g.strip()]
    return []


def require_admin(event: dict[str, Any]) -> None:
    if "admin" not in caller_groups(event):
        raise ForbiddenError("admin role required")


def handler(fn: Callable[[dict[str, Any]], dict[str, Any]]) -> Callable[[dict[str, Any], Any], dict[str, Any]]:
    def wrapped(event: dict[str, Any], _context: Any) -> dict[str, Any]:
        try:
            return fn(event)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    return wrapped
