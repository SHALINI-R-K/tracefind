from __future__ import annotations

from dataclasses import dataclass

from contexts.matching.domain.entities.match import Match
from contexts.matching.domain.repositories.match_repository import MatchRepository
from contexts.matching.domain.services.matching_service import MatchingService
from contexts.reporting.domain.repositories.item_report_repository import (
    ItemReportRepository,
)
from shared.domain.value_objects.identifier import ItemId
from shared.infrastructure.event_bus.dynamodb_stream_event_bus import EventBus


@dataclass
class RunMatchingCommand:
    item_repo: ItemReportRepository
    match_repo: MatchRepository
    matching_service: MatchingService
    event_bus: EventBus
    candidate_days: int = 30
    candidate_limit: int = 200

    def execute(self, item_id: str) -> list[Match]:
        new_report = self.item_repo.get(ItemId(item_id))
        candidates = self.item_repo.list_active_candidates(
            opposite_of=new_report.type,
            days_back=self.candidate_days,
            embedding_model_version=new_report.embedding_model_version,
            limit=self.candidate_limit,
        )
        matches = self.matching_service.find_matches(new_report, candidates)
        if not matches:
            return []
        self.match_repo.save_many(matches)
        all_events = []
        for match in matches:
            all_events.extend(match.pull_events())
        self.event_bus.publish(all_events)
        return matches
