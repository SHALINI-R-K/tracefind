from __future__ import annotations

import base64
import json
from typing import Any

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from contexts.notification.domain.entities.notification import Notification
from contexts.notification.domain.repositories.notification_repository import (
    NotificationRepository,
)
from contexts.notification.domain.value_objects.channel import NotificationType
from shared.domain.exceptions.domain_exception import ConflictError, NotFoundError
from shared.domain.value_objects.identifier import NotificationId, UserId
from shared.domain.value_objects.timestamp import Timestamp
from shared.infrastructure.aws.boto3_clients import dynamodb_resource


class DynamoNotificationRepository(NotificationRepository):
    def __init__(self, table_name: str) -> None:
        self._table = dynamodb_resource().Table(table_name)

    def save(self, notification: Notification) -> None:
        try:
            self._table.put_item(
                Item={
                    "id": str(notification.id),
                    "user_id": str(notification.user_id),
                    "type": notification.type.value,
                    "payload": notification.payload,
                    "read": notification.read,
                    "created_at": notification.created_at.to_iso(),
                    "ttl": notification.ttl,
                },
                ConditionExpression="attribute_not_exists(id)",
            )
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                raise ConflictError(
                    f"notification {notification.id} already exists"
                ) from exc
            raise

    def get(self, notification_id: NotificationId) -> Notification:
        resp = self._table.get_item(Key={"id": str(notification_id)})
        record = resp.get("Item")
        if not record:
            raise NotFoundError(f"notification {notification_id} not found")
        return self._from_record(record)

    def list_for_user(
        self, user_id: UserId, *, limit: int, cursor: str | None
    ) -> tuple[list[Notification], str | None]:
        kwargs: dict[str, Any] = {
            "IndexName": "GSI1",
            "KeyConditionExpression": Key("user_id").eq(str(user_id)),
            "Limit": limit,
            "ScanIndexForward": False,
        }
        if cursor:
            kwargs["ExclusiveStartKey"] = json.loads(
                base64.urlsafe_b64decode(cursor.encode()).decode()
            )
        resp = self._table.query(**kwargs)
        items = [self._from_record(r) for r in resp.get("Items", [])]
        last = resp.get("LastEvaluatedKey")
        next_cursor = (
            base64.urlsafe_b64encode(json.dumps(last, default=str).encode()).decode()
            if last
            else None
        )
        return items, next_cursor

    def mark_read(self, notification_id: NotificationId, user_id: UserId) -> None:
        self._table.update_item(
            Key={"id": str(notification_id)},
            UpdateExpression="SET #r = :true",
            ConditionExpression="user_id = :uid",
            ExpressionAttributeNames={"#r": "read"},
            ExpressionAttributeValues={":true": True, ":uid": str(user_id)},
        )

    @staticmethod
    def _from_record(record: dict[str, Any]) -> Notification:
        return Notification(
            id=NotificationId(record["id"]),
            user_id=UserId(record["user_id"]),
            type=NotificationType(record["type"]),
            payload=record.get("payload") or {},
            read=bool(record.get("read", False)),
            created_at=Timestamp.from_iso(record["created_at"]),
            ttl=int(record["ttl"]),
        )
