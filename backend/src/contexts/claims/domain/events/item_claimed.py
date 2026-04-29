from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shared.domain.events.domain_event import DomainEvent
from shared.domain.value_objects.identifier import ClaimId, Identifier, ItemId, MatchId
from shared.domain.value_objects.timestamp import Timestamp


@dataclass(frozen=True)
class ItemClaimed(DomainEvent):
    claim_id: ClaimId = None  # type: ignore[assignment]
    match_id: MatchId = None  # type: ignore[assignment]
    lost_item_id: ItemId = None  # type: ignore[assignment]
    found_item_id: ItemId = None  # type: ignore[assignment]
    lost_user_id: str = ""
    found_user_id: str = ""
    event_id: Identifier = field(default_factory=Identifier.new)
    occurred_at: Timestamp = field(default_factory=Timestamp.now)

    @property
    def name(self) -> str:
        return "claims.item_claimed"

    def payload(self) -> dict[str, Any]:
        return {
            "claim_id": str(self.claim_id),
            "match_id": str(self.match_id),
            "lost_item_id": str(self.lost_item_id),
            "found_item_id": str(self.found_item_id),
            "lost_user_id": self.lost_user_id,
            "found_user_id": self.found_user_id,
        }
