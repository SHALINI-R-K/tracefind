from __future__ import annotations

from dataclasses import dataclass

from contexts.matching.domain.entities.match import Match
from contexts.matching.domain.value_objects.embedding import Embedding
from contexts.matching.domain.value_objects.similarity_score import (
    MatchThreshold,
    SimilarityScore,
)
from contexts.reporting.domain.entities.item_report import ItemReport
from contexts.reporting.domain.value_objects.report_type import ReportType


@dataclass
class MatchingService:
    threshold: MatchThreshold
    top_k: int = 10

    def find_matches(
        self,
        new_report: ItemReport,
        candidates: list[ItemReport],
    ) -> list[Match]:
        new_vec = Embedding(tuple(new_report.embedding))
        scored: list[tuple[ItemReport, SimilarityScore]] = []
        for candidate in candidates:
            if candidate.embedding_model_version != new_report.embedding_model_version:
                continue
            cand_vec = Embedding(tuple(candidate.embedding))
            score = SimilarityScore(new_vec.cosine(cand_vec))
            if score.above(self.threshold):
                scored.append((candidate, score))

        scored.sort(key=lambda pair: pair[1].value, reverse=True)
        scored = scored[: self.top_k]

        matches: list[Match] = []
        for candidate, score in scored:
            lost, found = self._order(new_report, candidate)
            matches.append(
                Match.propose(
                    lost_item_id=lost.id,
                    found_item_id=found.id,
                    score=score,
                    lost_user_id=str(lost.user_id),
                    found_user_id=str(found.user_id),
                )
            )
        return matches

    @staticmethod
    def _order(a: ItemReport, b: ItemReport) -> tuple[ItemReport, ItemReport]:
        return (a, b) if a.type is ReportType.LOST else (b, a)
