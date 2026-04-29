from __future__ import annotations

from dataclasses import dataclass

from contexts.reporting.application.dtos.report_dto import (
    CreateItemReportInput,
    ItemReportView,
)
from contexts.reporting.domain.entities.item_report import ItemReport
from contexts.reporting.domain.repositories.item_report_repository import (
    ItemReportRepository,
)
from contexts.reporting.domain.services.embedding_generator import EmbeddingGenerator
from contexts.reporting.domain.value_objects.category import Category
from contexts.reporting.domain.value_objects.description import Description
from contexts.reporting.domain.value_objects.image_payload import ImagePayload
from contexts.reporting.domain.value_objects.report_type import ReportType
from shared.domain.value_objects.identifier import UserId
from shared.domain.value_objects.timestamp import Timestamp
from shared.infrastructure.event_bus.dynamodb_stream_event_bus import EventBus


@dataclass
class CreateItemReportCommand:
    repository: ItemReportRepository
    embedder: EmbeddingGenerator
    event_bus: EventBus
    ttl_seconds: int

    def execute(self, payload: CreateItemReportInput) -> ItemReportView:
        report_type = ReportType.parse(payload.type)
        description = Description(payload.description)
        category = Category.from_optional(payload.category)
        image = ImagePayload.from_data_uri(payload.image_data_uri)

        embedding, model_version = self.embedder.embed(image, description)

        report = ItemReport.create(
            user_id=UserId(payload.user_id),
            type=report_type,
            description=description,
            category=category,
            embedding=embedding,
            embedding_model_version=model_version,
            created_at=Timestamp.now(),
            ttl_seconds=self.ttl_seconds,
        )
        self.repository.save(report)
        self.event_bus.publish(report.pull_events())

        d = report.to_dict()
        return ItemReportView(**d)
