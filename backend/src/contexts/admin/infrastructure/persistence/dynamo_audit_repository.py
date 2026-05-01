from __future__ import annotations

import base64
import json
from decimal import Decimal
from typing import Any

from boto3.dynamodb.conditions import Key


def _coerce(value: Any) -> Any:
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {k: _coerce(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_coerce(v) for v in value]
    return value

from contexts.admin.domain.entities.audit_entry import AuditEntry
from contexts.admin.domain.repositories.audit_repository import AuditRepository
from shared.domain.value_objects.identifier import Identifier
from shared.domain.value_objects.timestamp import Timestamp
from shared.infrastructure.aws.boto3_clients import dynamodb_resource


class DynamoAuditRepository(AuditRepository):
    def __init__(self, table_name: str) -> None:
        self._table = dynamodb_resource().Table(table_name)

    def append(self, entry: AuditEntry) -> None:
        self._table.put_item(
            Item={
                "id": str(entry.id),
                "actor_user_id": entry.actor_user_id,
                "action": entry.action,
                "target_id": entry.target_id,
                "before": _coerce(entry.before),
                "after": _coerce(entry.after),
                "created_at": entry.created_at.to_iso(),
            },
            ConditionExpression="attribute_not_exists(id)",
        )

    def list(
        self,
        *,
        actor_user_id: str | None,
        target_id: str | None,
        limit: int,
        cursor: str | None,
    ) -> tuple[list[AuditEntry], str | None]:
        kwargs: dict[str, Any] = {"Limit": limit}
        start_key = (
            json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
            if cursor
            else None
        )
        if actor_user_id:
            kwargs["IndexName"] = "GSI1"
            kwargs["KeyConditionExpression"] = Key("actor_user_id").eq(actor_user_id)
            kwargs["ScanIndexForward"] = False
        elif target_id:
            kwargs["IndexName"] = "GSI2"
            kwargs["KeyConditionExpression"] = Key("target_id").eq(target_id)
            kwargs["ScanIndexForward"] = False
        if start_key:
            kwargs["ExclusiveStartKey"] = start_key
        if actor_user_id or target_id:
            resp = self._table.query(**kwargs)
        else:
            resp = self._table.scan(**kwargs)
        items = [self._from_record(r) for r in resp.get("Items", [])]
        last = resp.get("LastEvaluatedKey")
        next_cursor = (
            base64.urlsafe_b64encode(json.dumps(last, default=str).encode()).decode()
            if last
            else None
        )
        return items, next_cursor

    @staticmethod
    def _from_record(record: dict[str, Any]) -> AuditEntry:
        return AuditEntry(
            id=Identifier(record["id"]),
            actor_user_id=record["actor_user_id"],
            action=record["action"],
            target_id=record["target_id"],
            before=record.get("before") or {},
            after=record.get("after") or {},
            created_at=Timestamp.from_iso(record["created_at"]),
        )
