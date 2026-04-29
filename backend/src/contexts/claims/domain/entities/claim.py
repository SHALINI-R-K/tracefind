from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from contexts.claims.domain.events.item_claimed import ItemClaimed
from contexts.claims.domain.value_objects.claim_status import ClaimStatus
from shared.domain.events.domain_event import DomainEvent
from shared.domain.value_objects.identifier import ClaimId, ItemId, MatchId, UserId
from shared.domain.value_objects.timestamp import Timestamp


@dataclass
class Claim:
    id: ClaimId
    match_id: MatchId
    claimant_user_id: UserId
    lost_item_id: ItemId
    found_item_id: ItemId
    status: ClaimStatus
    created_at: Timestamp
    resolved_at: Timestamp | None
    _events: list[DomainEvent] = field(default_factory=list, repr=False)

    @classmethod
    def open(
        cls,
        *,
        match_id: MatchId,
        claimant_user_id: UserId,
        lost_item_id: ItemId,
        found_item_id: ItemId,
    ) -> "Claim":
        return cls(
            id=ClaimId.new(),
            match_id=match_id,
            claimant_user_id=claimant_user_id,
            lost_item_id=lost_item_id,
            found_item_id=found_item_id,
            status=ClaimStatus.PENDING,
            created_at=Timestamp.now(),
            resolved_at=None,
        )

    def confirm(self, lost_owner_id: UserId, found_owner_id: UserId) -> None:
        self.status = ClaimStatus.CONFIRMED
        self.resolved_at = Timestamp.now()
        self._events.append(
            ItemClaimed(
                claim_id=self.id,
                match_id=self.match_id,
                lost_item_id=self.lost_item_id,
                found_item_id=self.found_item_id,
                lost_user_id=str(lost_owner_id),
                found_user_id=str(found_owner_id),
            )
        )

    def reject(self) -> None:
        self.status = ClaimStatus.REJECTED
        self.resolved_at = Timestamp.now()

    def pull_events(self) -> list[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "match_id": str(self.match_id),
            "claimant_user_id": str(self.claimant_user_id),
            "lost_item_id": str(self.lost_item_id),
            "found_item_id": str(self.found_item_id),
            "status": self.status.value,
            "created_at": self.created_at.to_iso(),
            "resolved_at": self.resolved_at.to_iso() if self.resolved_at else None,
        }
