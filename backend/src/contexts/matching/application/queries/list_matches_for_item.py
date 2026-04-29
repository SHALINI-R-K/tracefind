from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from contexts.matching.domain.repositories.match_repository import MatchRepository
from contexts.reporting.domain.repositories.item_report_repository import (
    ItemReportRepository,
)
from shared.domain.exceptions.domain_exception import ForbiddenError
from shared.domain.value_objects.identifier import ItemId


@dataclass
class ListMatchesForItemQuery:
    match_repo: MatchRepository
    item_repo: ItemReportRepository

    def execute(
        self,
        item_id: str,
        caller_user_id: str,
        is_admin: bool,
        *,
        min_score: float = 0.0,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        report = self.item_repo.get(ItemId(item_id))
        if not is_admin and str(report.user_id) != caller_user_id:
            raise ForbiddenError("not your item")
        matches = self.match_repo.list_for_item(
            ItemId(item_id), min_score=min_score, limit=limit
        )
        return [m.to_dict() for m in matches]
