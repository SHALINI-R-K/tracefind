from __future__ import annotations

from decimal import Decimal
from typing import Any

from boto3.dynamodb.conditions import Key

from contexts.matching.domain.entities.match import Match
from contexts.matching.domain.repositories.match_repository import MatchRepository
from contexts.matching.domain.value_objects.match_status import MatchStatus
from contexts.matching.domain.value_objects.similarity_score import SimilarityScore
from shared.domain.exceptions.domain_exception import NotFoundError
from shared.domain.value_objects.identifier import ItemId, MatchId
from shared.domain.value_objects.timestamp import Timestamp
from shared.infrastructure.aws.boto3_clients import dynamodb_resource


class DynamoMatchRepository(MatchRepository):
    def __init__(self, table_name: str) -> None:
        self._table = dynamodb_resource().Table(table_name)

    def save(self, match: Match) -> None:
        self._table.put_item(Item=self._to_record(match))

    def save_many(self, matches: list[Match]) -> None:
        with self._table.batch_writer() as batch:
            for match in matches:
                batch.put_item(Item=self._to_record(match))

    def get(self, match_id: MatchId) -> Match:
        resp = self._table.get_item(Key={"id": str(match_id)})
        record = resp.get("Item")
        if not record:
            raise NotFoundError(f"match {match_id} not found")
        return self._from_record(record)

    def list_for_item(
        self, item_id: ItemId, *, min_score: float, limit: int
    ) -> list[Match]:
        results: list[Match] = []
        for index in ("GSI1", "GSI2"):
            resp = self._table.query(
                IndexName=index,
                KeyConditionExpression=(
                    Key("lost_item_id").eq(str(item_id))
                    if index == "GSI1"
                    else Key("found_item_id").eq(str(item_id))
                ),
                Limit=limit,
            )
            for record in resp.get("Items", []):
                if float(record.get("score", 0)) < min_score:
                    continue
                results.append(self._from_record(record))
        results.sort(key=lambda m: m.score.value, reverse=True)
        return results[:limit]

    @staticmethod
    def _to_record(match: Match) -> dict[str, Any]:
        return {
            "id": str(match.id),
            "lost_item_id": str(match.lost_item_id),
            "found_item_id": str(match.found_item_id),
            "score": Decimal(str(round(match.score.value, 6))),
            "status": match.status.value,
            "created_at": match.created_at.to_iso(),
        }

    @staticmethod
    def _from_record(record: dict[str, Any]) -> Match:
        return Match(
            id=MatchId(record["id"]),
            lost_item_id=ItemId(record["lost_item_id"]),
            found_item_id=ItemId(record["found_item_id"]),
            score=SimilarityScore(float(record["score"])),
            status=MatchStatus(record["status"]),
            created_at=Timestamp.from_iso(record["created_at"]),
        )
