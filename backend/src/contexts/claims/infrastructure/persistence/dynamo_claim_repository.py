from __future__ import annotations

from decimal import Decimal
from typing import Any

from contexts.claims.domain.entities.claim import Claim
from contexts.claims.domain.repositories.claim_repository import ClaimRepository
from contexts.claims.domain.value_objects.claim_status import ClaimStatus
from contexts.reporting.domain.value_objects.report_status import ReportStatus
from shared.domain.exceptions.domain_exception import NotFoundError
from shared.domain.value_objects.identifier import ClaimId, ItemId, MatchId, UserId
from shared.domain.value_objects.timestamp import Timestamp
from shared.infrastructure.aws.boto3_clients import dynamodb_client, dynamodb_resource


class DynamoClaimRepository(ClaimRepository):
    def __init__(self, table_name: str) -> None:
        self._table_name = table_name
        self._table = dynamodb_resource().Table(table_name)
        self._client = dynamodb_client()

    def save(self, claim: Claim) -> None:
        self._table.put_item(Item=self._to_record(claim))

    def get(self, claim_id: ClaimId) -> Claim:
        resp = self._table.get_item(Key={"id": str(claim_id)})
        record = resp.get("Item")
        if not record:
            raise NotFoundError(f"claim {claim_id} not found")
        return self._from_record(record)

    def save_with_item_lock(self, claim: Claim, items_table: str) -> bool:
        try:
            self._client.transact_write_items(
                TransactItems=[
                    {
                        "Update": {
                            "TableName": items_table,
                            "Key": {"id": {"S": str(claim.lost_item_id)}},
                            "UpdateExpression": "SET #s = :claimed",
                            "ConditionExpression": "#s = :active",
                            "ExpressionAttributeNames": {"#s": "status"},
                            "ExpressionAttributeValues": {
                                ":claimed": {"S": ReportStatus.CLAIMED.value},
                                ":active": {"S": ReportStatus.ACTIVE.value},
                            },
                        }
                    },
                    {
                        "Update": {
                            "TableName": items_table,
                            "Key": {"id": {"S": str(claim.found_item_id)}},
                            "UpdateExpression": "SET #s = :claimed",
                            "ConditionExpression": "#s = :active",
                            "ExpressionAttributeNames": {"#s": "status"},
                            "ExpressionAttributeValues": {
                                ":claimed": {"S": ReportStatus.CLAIMED.value},
                                ":active": {"S": ReportStatus.ACTIVE.value},
                            },
                        }
                    },
                    {
                        "Put": {
                            "TableName": self._table_name,
                            "Item": _to_dynamodb_native(self._to_record(claim)),
                        }
                    },
                ]
            )
            return True
        except self._client.exceptions.TransactionCanceledException:
            return False

    @staticmethod
    def _to_record(claim: Claim) -> dict[str, Any]:
        return {
            "id": str(claim.id),
            "match_id": str(claim.match_id),
            "claimant_user_id": str(claim.claimant_user_id),
            "lost_item_id": str(claim.lost_item_id),
            "found_item_id": str(claim.found_item_id),
            "status": claim.status.value,
            "created_at": claim.created_at.to_iso(),
            "resolved_at": claim.resolved_at.to_iso() if claim.resolved_at else None,
        }

    @staticmethod
    def _from_record(record: dict[str, Any]) -> Claim:
        resolved = record.get("resolved_at")
        return Claim(
            id=ClaimId(record["id"]),
            match_id=MatchId(record["match_id"]),
            claimant_user_id=UserId(record["claimant_user_id"]),
            lost_item_id=ItemId(record["lost_item_id"]),
            found_item_id=ItemId(record["found_item_id"]),
            status=ClaimStatus(record["status"]),
            created_at=Timestamp.from_iso(record["created_at"]),
            resolved_at=Timestamp.from_iso(resolved) if resolved else None,
        )


def _to_dynamodb_native(record: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in record.items():
        if v is None:
            out[k] = {"NULL": True}
        elif isinstance(v, bool):
            out[k] = {"BOOL": v}
        elif isinstance(v, (int, Decimal)):
            out[k] = {"N": str(v)}
        else:
            out[k] = {"S": str(v)}
    return out
