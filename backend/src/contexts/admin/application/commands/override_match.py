from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from contexts.admin.domain.entities.audit_entry import AuditEntry
from contexts.admin.domain.repositories.audit_repository import AuditRepository
from contexts.matching.domain.entities.match import Match
from contexts.matching.domain.repositories.match_repository import MatchRepository
from contexts.matching.domain.value_objects.similarity_score import SimilarityScore
from contexts.reporting.domain.repositories.item_report_repository import (
    ItemReportRepository,
)
from contexts.reporting.domain.value_objects.report_type import ReportType
from shared.domain.exceptions.domain_exception import InvalidInputError
from shared.domain.value_objects.identifier import ItemId, MatchId


@dataclass
class OverrideMatchCommand:
    item_repo: ItemReportRepository
    match_repo: MatchRepository
    audit_repo: AuditRepository

    def force(
        self,
        *,
        lost_item_id: str,
        found_item_id: str,
        actor_user_id: str,
        reason: str,
    ) -> dict[str, Any]:
        if not reason:
            raise InvalidInputError("reason is required")
        lost = self.item_repo.get(ItemId(lost_item_id))
        found = self.item_repo.get(ItemId(found_item_id))
        if lost.type is not ReportType.LOST or found.type is not ReportType.FOUND:
            raise InvalidInputError("must reference one lost and one found item")

        match = Match.propose(
            lost_item_id=lost.id,
            found_item_id=found.id,
            score=SimilarityScore(1.0),
            lost_user_id=str(lost.user_id),
            found_user_id=str(found.user_id),
        )
        self.match_repo.save(match)
        entry = AuditEntry.record(
            actor_user_id=actor_user_id,
            action="override_match",
            target_id=str(match.id),
            after={
                "match": match.to_dict(),
                "reason": reason,
            },
        )
        self.audit_repo.append(entry)
        return {"match": match.to_dict(), "audit_id": str(entry.id)}

    def delete(self, *, match_id: str, actor_user_id: str, reason: str) -> dict[str, Any]:
        if not reason:
            raise InvalidInputError("reason is required")
        match = self.match_repo.get(MatchId(match_id))
        before = match.to_dict()
        match.reject()
        self.match_repo.save(match)
        entry = AuditEntry.record(
            actor_user_id=actor_user_id,
            action="reject_match",
            target_id=match_id,
            before=before,
            after={"match": match.to_dict(), "reason": reason},
        )
        self.audit_repo.append(entry)
        return {"match": match.to_dict(), "audit_id": str(entry.id)}
