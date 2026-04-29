from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from contexts.admin.domain.repositories.audit_repository import AuditRepository
from shared.infrastructure.aws.boto3_clients import dynamodb_resource


@dataclass
class AdminListReportsQuery:
    items_table_name: str

    def execute(self, *, status: str | None, limit: int) -> list[dict[str, Any]]:
        table = dynamodb_resource().Table(self.items_table_name)
        kwargs: dict[str, Any] = {"Limit": limit}
        if status:
            kwargs["FilterExpression"] = "#s = :s"
            kwargs["ExpressionAttributeNames"] = {"#s": "status"}
            kwargs["ExpressionAttributeValues"] = {":s": status}
        resp = table.scan(**kwargs)
        return [
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
