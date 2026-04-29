from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from contexts.claims.domain.entities.claim import Claim
from contexts.claims.domain.repositories.claim_repository import ClaimRepository
from contexts.claims.domain.value_objects.claim_status import ClaimDecision
from contexts.matching.domain.repositories.match_repository import MatchRepository
from contexts.reporting.domain.repositories.item_report_repository import (
    ItemReportRepository,
)
from shared.domain.exceptions.domain_exception import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from shared.domain.value_objects.identifier import ItemId, MatchId, UserId


@dataclass
class ConfirmClaimCommand:
    claim_repo: ClaimRepository
    match_repo: MatchRepository
    item_repo: ItemReportRepository
    items_table_name: str

    def execute(
        self,
        *,
        item_id: str,
        match_id: str,
        decision: str,
        caller_user_id: str,
    ) -> dict[str, Any]:
        decision_vo = ClaimDecision.parse(decision)
        match = self.match_repo.get(MatchId(match_id))

        if str(match.lost_item_id) != item_id and str(match.found_item_id) != item_id:
            raise NotFoundError("match does not reference this item")

        lost = self.item_repo.get(match.lost_item_id)
        found = self.item_repo.get(match.found_item_id)
        if caller_user_id not in {str(lost.user_id), str(found.user_id)}:
            raise ForbiddenError("only counterparties can resolve a claim")

        claim = Claim.open(
            match_id=match.id,
            claimant_user_id=UserId(caller_user_id),
            lost_item_id=lost.id,
            found_item_id=found.id,
        )

        if decision_vo is ClaimDecision.REJECT:
            claim.reject()
            match.reject()
            self.match_repo.save(match)
            self.claim_repo.save(claim)
            return claim.to_dict()

        claim.confirm(lost_owner_id=lost.user_id, found_owner_id=found.user_id)
        ok = self.claim_repo.save_with_item_lock(claim, self.items_table_name)
        if not ok:
            raise ConflictError("item already claimed")
        match.confirm()
        self.match_repo.save(match)
        return claim.to_dict()
