from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from contexts.admin.domain.entities.audit_entry import AuditEntry
from contexts.admin.domain.repositories.audit_repository import AuditRepository
from contexts.reporting.domain.repositories.item_report_repository import (
    ItemReportRepository,
)
from contexts.reporting.domain.value_objects.report_status import ReportStatus
from shared.domain.exceptions.domain_exception import InvalidInputError
from shared.domain.value_objects.identifier import ItemId


@dataclass
class ModerateReportCommand:
    item_repo: ItemReportRepository
    audit_repo: AuditRepository

    def archive(self, *, item_id: str, actor_user_id: str, reason: str) -> dict[str, Any]:
        if not reason:
            raise InvalidInputError("reason is required")
        report = self.item_repo.get(ItemId(item_id))
        before = report.to_dict()
        report.archive()
        self.item_repo.save(report)
        after = report.to_dict()
        entry = AuditEntry.record(
            actor_user_id=actor_user_id,
            action="archive_item",
            target_id=item_id,
            before=before,
            after={**after, "reason": reason},
        )
        self.audit_repo.append(entry)
        return {"item": after, "audit_id": str(entry.id)}
