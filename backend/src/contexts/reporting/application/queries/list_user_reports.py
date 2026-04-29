from __future__ import annotations

from dataclasses import dataclass

from contexts.reporting.application.dtos.report_dto import ItemReportView
from contexts.reporting.domain.repositories.item_report_repository import (
    ItemReportRepository,
)
from shared.domain.value_objects.identifier import UserId


@dataclass
class ListUserReportsQuery:
    repository: ItemReportRepository

    def execute(
        self, user_id: str, *, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[ItemReportView], str | None]:
        reports, next_cursor = self.repository.list_by_user(
            UserId(user_id), limit=limit, cursor=cursor
        )
        return [ItemReportView(**r.to_dict()) for r in reports], next_cursor
