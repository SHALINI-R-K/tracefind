from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any

from contexts.admin.domain.repositories.audit_repository import AuditRepository
from shared.infrastructure.aws.boto3_clients import dynamodb_resource


def _encode_cursor(key: dict[str, Any] | None) -> str | None:
    if not key:
        return None
    return base64.urlsafe_b64encode(json.dumps(key, default=str).encode()).decode()


def _decode_cursor(cursor: str | None) -> dict[str, Any] | None:
    if not cursor:
        return None
    return json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())


@dataclass
class AdminListReportsQuery:
    items_table_name: str

    def execute(
        self, *, status: str | None, limit: int, cursor: str | None = None
    ) -> tuple[list[dict[str, Any]], str | None]:
        table = dynamodb_resource().Table(self.items_table_name)
        kwargs: dict[str, Any] = {"Limit": limit}
        if status:
            kwargs["FilterExpression"] = "#s = :s"
            kwargs["ExpressionAttributeNames"] = {"#s": "status"}
            kwargs["ExpressionAttributeValues"] = {":s": status}
        start_key = _decode_cursor(cursor)
        if start_key:
            kwargs["ExclusiveStartKey"] = start_key
        resp = table.scan(**kwargs)
        rows = [
            {
                "id": r.get("id"),
                "user_id": r.get("user_id"),
                "type": r.get("type"),
                "description": r.get("description"),
                "category": r.get("category"),
                "status": r.get("status"),
                "created_at": r.get("created_at"),
            }
            for r in resp.get("Items", [])
        ]
        return rows, _encode_cursor(resp.get("LastEvaluatedKey"))


@dataclass
class AdminAuditQuery:
    audit_repo: AuditRepository

    def execute(
        self,
        *,
        actor_user_id: str | None,
        target_id: str | None,
        limit: int,
        cursor: str | None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        entries, next_cursor = self.audit_repo.list(
            actor_user_id=actor_user_id,
            target_id=target_id,
            limit=limit,
            cursor=cursor,
        )
        return [e.to_dict() for e in entries], next_cursor
