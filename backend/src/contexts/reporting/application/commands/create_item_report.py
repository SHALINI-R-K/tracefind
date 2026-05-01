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
from shared.domain.exceptions.domain_exception import InvalidInputError
from shared.domain.value_objects.identifier import UserId
from shared.domain.value_objects.timestamp import Timestamp
from shared.infrastructure.event_bus.dynamodb_stream_event_bus import EventBus


_MAX_PHOTOS = 3
_MAX_LOCATION_LENGTH = 200


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

        # Validate + parse photos
        if not payload.image_data_uris:
            raise InvalidInputError("at least one photo is required")
        if len(payload.image_data_uris) > _MAX_PHOTOS:
            raise InvalidInputError(
                f"at most {_MAX_PHOTOS} photos allowed per report"
            )
        images = [ImagePayload.from_data_uri(uri) for uri in payload.image_data_uris]

        # Validate optional location
        location = (payload.location or "").strip() or None
        if location and len(location) > _MAX_LOCATION_LENGTH:
            raise InvalidInputError(
                f"location must be {_MAX_LOCATION_LENGTH} characters or fewer"
            )

        # Parse optional incident_at — caller sends ISO 8601
        incident_at = (
            Timestamp.from_iso(payload.incident_at_iso)
            if payload.incident_at_iso
            else None
        )

        # Build the context string the embedder includes alongside description.
        # Provides the model with "where" and "when" alongside "what".
        context_parts: list[str] = []
        if location:
            context_parts.append(f"Location: {location}")
        if incident_at is not None:
            context_parts.append(f"Incident time: {incident_at.to_iso()}")
        context = "\n".join(context_parts)

        embedding, model_version = self.embedder.embed(
            images, description, context=context
        )

        report = ItemReport.create(
            user_id=UserId(payload.user_id),
            type=report_type,
            description=description,
            category=category,
            embedding=embedding,
            embedding_model_version=model_version,
            created_at=Timestamp.now(),
            ttl_seconds=self.ttl_seconds,
            location=location,
            incident_at=incident_at,
            photo_count=len(images),
        )
        self.repository.save(report)
        self.event_bus.publish(report.pull_events())

        return ItemReportView(**report.to_dict())
