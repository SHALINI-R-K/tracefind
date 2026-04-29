from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from contexts.reporting.domain.events.item_reported import ItemReported
from contexts.reporting.domain.events.report_status_changed import ReportStatusChanged
from contexts.reporting.domain.value_objects.category import Category
from contexts.reporting.domain.value_objects.description import Description
from contexts.reporting.domain.value_objects.report_status import ReportStatus
from contexts.reporting.domain.value_objects.report_type import ReportType
from shared.domain.events.domain_event import DomainEvent
from shared.domain.exceptions.domain_exception import ConflictError
from shared.domain.value_objects.identifier import ItemId, UserId
from shared.domain.value_objects.timestamp import Timestamp


@dataclass
class ItemReport:
    id: ItemId
    user_id: UserId
    type: ReportType
    description: Description
    category: Category | None
    status: ReportStatus
    embedding: list[float]
    embedding_model_version: str
    created_at: Timestamp
    ttl: int
    _events: list[DomainEvent] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls,
        *,
        user_id: UserId,
        type: ReportType,
        description: Description,
        category: Category | None,
        embedding: list[float],
        embedding_model_version: str,
        created_at: Timestamp,
        ttl_seconds: int,
    ) -> "ItemReport":
        report = cls(
            id=ItemId.new(),
            user_id=user_id,
            type=type,
            description=description,
            category=category,
            status=ReportStatus.ACTIVE,
            embedding=list(embedding),
            embedding_model_version=embedding_model_version,
            created_at=created_at,
            ttl=created_at.epoch_seconds() + ttl_seconds,
        )
        report._events.append(
            ItemReported(
                item_id=report.id,
                user_id=user_id,
                type=type,
                category=category.value if category else None,
            )
        )
        return report

    def mark_matched(self) -> None:
        if self.status is not ReportStatus.ACTIVE:
            return
        self._transition(ReportStatus.MATCHED)

    def mark_claimed(self) -> None:
        if self.status is ReportStatus.CLAIMED:
            raise ConflictError("item already claimed")
        self._transition(ReportStatus.CLAIMED)

    def archive(self) -> None:
        self._transition(ReportStatus.ARCHIVED)

    def _transition(self, new_status: ReportStatus) -> None:
        old = self.status
        self.status = new_status
        self._events.append(
            ReportStatusChanged(item_id=self.id, from_status=old.value, to_status=new_status.value)
        )

    def pull_events(self) -> list[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.type.value,
            "description": self.description.value,
            "category": self.category.value if self.category else None,
            "status": self.status.value,
            "created_at": self.created_at.to_iso(),
        }
