from __future__ import annotations

import base64
import json
from datetime import timedelta
from decimal import Decimal
from typing import Any

from boto3.dynamodb.conditions import Key

from contexts.reporting.domain.entities.item_report import ItemReport
from contexts.reporting.domain.repositories.item_report_repository import (
    ItemReportRepository,
)
from contexts.reporting.domain.value_objects.category import Category
from contexts.reporting.domain.value_objects.description import Description
from contexts.reporting.domain.value_objects.report_status import ReportStatus
from contexts.reporting.domain.value_objects.report_type import ReportType
from shared.domain.exceptions.domain_exception import NotFoundError
from shared.domain.value_objects.identifier import ItemId, UserId
from shared.domain.value_objects.timestamp import Timestamp
from shared.infrastructure.aws.boto3_clients import dynamodb_resource


class DynamoItemReportRepository(ItemReportRepository):
    def __init__(self, table_name: str) -> None:
        self._table = dynamodb_resource().Table(table_name)

    def save(self, report: ItemReport) -> None:
        self._table.put_item(Item=self._to_record(report))

    def get(self, item_id: ItemId) -> ItemReport:
        resp = self._table.get_item(Key={"id": str(item_id)})
        record = resp.get("Item")
        if not record:
            raise NotFoundError(f"item {item_id} not found")
        return self._from_record(record)

    def list_by_user(
        self, user_id: UserId, *, limit: int, cursor: str | None
    ) -> tuple[list[ItemReport], str | None]:
        kwargs: dict[str, Any] = {
            "IndexName": "GSI2",
            "KeyConditionExpression": Key("user_id").eq(str(user_id)),
            "Limit": limit,
            "ScanIndexForward": False,
        }
        if cursor:
            kwargs["ExclusiveStartKey"] = _decode_cursor(cursor)
        resp = self._table.query(**kwargs)
        reports = [self._from_record(r) for r in resp.get("Items", [])]
        last = resp.get("LastEvaluatedKey")
        return reports, _encode_cursor(last) if last else None

    def list_active_candidates(
        self,
        *,
        opposite_of: ReportType,
        days_back: int,
        embedding_model_version: str,
        limit: int,
    ) -> list[ItemReport]:
        target_type = opposite_of.opposite()
        candidates: list[ItemReport] = []
        now = Timestamp.now().value
        for offset in range(days_back):
            day = (now - timedelta(days=offset)).strftime("%Y-%m-%d")
            resp = self._table.query(
                IndexName="GSI1",
                KeyConditionExpression=Key("gsi1_pk").eq(f"{target_type.value}#{day}"),
                Limit=limit,
                ScanIndexForward=False,
            )
            for record in resp.get("Items", []):
                if record.get("status") != ReportStatus.ACTIVE.value:
                    continue
                if record.get("embedding_model_version") != embedding_model_version:
                    continue
                candidates.append(self._from_record(record))
                if len(candidates) >= limit:
                    return candidates
        return candidates

    def update_status_active_to(
        self, item_id: ItemId, *, target: ReportStatus
    ) -> bool:
        try:
            self._table.update_item(
                Key={"id": str(item_id)},
                UpdateExpression="SET #s = :new",
                ConditionExpression="#s = :active",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={
                    ":new": target.value,
                    ":active": ReportStatus.ACTIVE.value,
                },
            )
            return True
        except self._table.meta.client.exceptions.ConditionalCheckFailedException:
            return False

    @staticmethod
    def _to_record(report: ItemReport) -> dict[str, Any]:
        day = report.created_at.value.strftime("%Y-%m-%d")
        record: dict[str, Any] = {
            "id": str(report.id),
            "user_id": str(report.user_id),
            "type": report.type.value,
            "description": report.description.value,
            "category": report.category.value if report.category else None,
            "embedding": [Decimal(str(x)) for x in report.embedding],
            "embedding_model_version": report.embedding_model_version,
            "status": report.status.value,
            "created_at": report.created_at.to_iso(),
            "ttl": report.ttl,
            "gsi1_pk": f"{report.type.value}#{day}",
            "photo_count": report.photo_count,
        }
        if report.location:
            record["location"] = report.location
        if report.incident_at is not None:
            record["incident_at"] = report.incident_at.to_iso()
        return record

    @staticmethod
    def _from_record(record: dict[str, Any]) -> ItemReport:
        category = record.get("category")
        incident_at_raw = record.get("incident_at")
        return ItemReport(
            id=ItemId(record["id"]),
            user_id=UserId(record["user_id"]),
            type=ReportType(record["type"]),
            description=Description(record["description"]),
            category=Category(category) if category else None,
            status=ReportStatus(record["status"]),
            embedding=[float(x) for x in record.get("embedding", [])],
            embedding_model_version=record["embedding_model_version"],
            created_at=Timestamp.from_iso(record["created_at"]),
            ttl=int(record["ttl"]),
            location=record.get("location"),
            incident_at=Timestamp.from_iso(incident_at_raw) if incident_at_raw else None,
            photo_count=int(record.get("photo_count", 1)),
        )


def _encode_cursor(key: dict[str, Any]) -> str:
    return base64.urlsafe_b64encode(json.dumps(key, default=str).encode()).decode()


def _decode_cursor(cursor: str) -> dict[str, Any]:
    return json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
