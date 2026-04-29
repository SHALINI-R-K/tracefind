from __future__ import annotations

from dataclasses import dataclass

from contexts.reporting.domain.repositories.item_report_repository import (
    ItemReportRepository,
)
from contexts.reporting.domain.services.embedding_generator import EmbeddingGenerator
from contexts.reporting.domain.value_objects.image_payload import ImagePayload
from shared.domain.value_objects.identifier import ItemId


@dataclass
class ReembedReportCommand:
    """Re-compute embedding for an existing item using a refreshed model.

    Because images are not persisted, the caller must supply the image data URI
    (e.g. via a one-time admin re-upload flow). Description is read from the
    stored record.
    """

    repository: ItemReportRepository
    embedder: EmbeddingGenerator

    def execute(self, *, item_id: str, image_data_uri: str) -> dict[str, str]:
        report = self.repository.get(ItemId(item_id))
        image = ImagePayload.from_data_uri(image_data_uri)
        embedding, model_version = self.embedder.embed(image, report.description)
        report.embedding = embedding
        report.embedding_model_version = model_version
        self.repository.save(report)
        return {"id": str(report.id), "embedding_model_version": model_version}
