from __future__ import annotations

from typing import Protocol

from contexts.matching.domain.entities.match import Match
from shared.domain.value_objects.identifier import ItemId, MatchId


class MatchRepository(Protocol):
    def save(self, match: Match) -> None: ...

    def save_many(self, matches: list[Match]) -> None: ...

    def get(self, match_id: MatchId) -> Match: ...

    def list_for_item(self, item_id: ItemId, *, min_score: float, limit: int) -> list[Match]: ...
