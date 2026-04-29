from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from contexts.matching.domain.events.match_found import MatchFound
from contexts.matching.domain.value_objects.match_status import MatchStatus
from contexts.matching.domain.value_objects.similarity_score import SimilarityScore
from shared.domain.events.domain_event import DomainEvent
from shared.domain.value_objects.identifier import ItemId, MatchId
from shared.domain.value_objects.timestamp import Timestamp


@dataclass
class Match:
    id: MatchId
    lost_item_id: ItemId
    found_item_id: ItemId
    score: SimilarityScore
    status: MatchStatus
    created_at: Timestamp
    _events: list[DomainEvent] = field(default_factory=list, repr=False)

    @classmethod
    def propose(
        cls,
        *,
        lost_item_id: ItemId,
        found_item_id: ItemId,
        score: SimilarityScore,
        lost_user_id: str,
        found_user_id: str,
    ) -> "Match":
        match = cls(
            id=MatchId.new(),
            lost_item_id=lost_item_id,
            found_item_id=found_item_id,
            score=score,
            status=MatchStatus.PENDING,
            created_at=Timestamp.now(),
        )
        match._events.append(
            MatchFound(
                match_id=match.id,
                lost_item_id=lost_item_id,
                found_item_id=found_item_id,
                lost_user_id=lost_user_id,
                found_user_id=found_user_id,
                score=score.value,
            )
        )
        return match

    def confirm(self) -> None:
        self.status = MatchStatus.CONFIRMED

    def reject(self) -> None:
        self.status = MatchStatus.REJECTED

    def pull_events(self) -> list[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "lost_item_id": str(self.lost_item_id),
            "found_item_id": str(self.found_item_id),
            "score": round(self.score.value, 4),
            "status": self.status.value,
            "created_at": self.created_at.to_iso(),
        }
