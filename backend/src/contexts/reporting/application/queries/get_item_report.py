from __future__ import annotations

from dataclasses import dataclass

from contexts.reporting.application.dtos.report_dto import ItemReportView
from contexts.reporting.domain.repositories.item_report_repository import (
    ItemReportRepository,
)
from shared.domain.exceptions.domain_exception import ForbiddenError
from shared.domain.value_objects.identifier import ItemId


@dataclass
class GetItemReportQuery:
    repository: ItemReportRepository

    def execute(self, item_id: str, caller_user_id: str, is_admin: bool) -> ItemReportView:
        report = self.repository.get(ItemId(item_id))
        if not is_admin and str(report.user_id) != caller_user_id:
            raise ForbiddenError("not your item")
        return ItemReportView(**report.to_dict())
