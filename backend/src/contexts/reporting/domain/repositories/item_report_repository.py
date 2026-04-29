from __future__ import annotations

from typing import Protocol

from contexts.reporting.domain.entities.item_report import ItemReport
from contexts.reporting.domain.value_objects.report_status import ReportStatus
from contexts.reporting.domain.value_objects.report_type import ReportType
from shared.domain.value_objects.identifier import ItemId, UserId


class ItemReportRepository(Protocol):
    def save(self, report: ItemReport) -> None: ...

    def get(self, item_id: ItemId) -> ItemReport: ...

    def list_by_user(
        self, user_id: UserId, *, limit: int, cursor: str | None
    ) -> tuple[list[ItemReport], str | None]: ...

    def list_active_candidates(
        self,
        *,
        opposite_of: ReportType,
        days_back: int,
        embedding_model_version: str,
        limit: int,
    ) -> list[ItemReport]: ...

    def update_status_active_to(
        self,
        item_id: ItemId,
        *,
        target: ReportStatus,
    ) -> bool:
        """Conditional update: only succeeds when current status == ACTIVE.

        Returns True if the update succeeded, False if pre-condition failed.
        """
        ...
