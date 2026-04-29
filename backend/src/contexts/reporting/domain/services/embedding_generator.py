from __future__ import annotations

from typing import Protocol

from contexts.reporting.domain.value_objects.description import Description
from contexts.reporting.domain.value_objects.image_payload import ImagePayload


class EmbeddingGenerator(Protocol):
    def embed(self, image: ImagePayload, description: Description) -> tuple[list[float], str]:
        """Return (combined embedding vector, model version string)."""
        ...
