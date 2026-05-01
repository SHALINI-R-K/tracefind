from __future__ import annotations

from typing import Protocol, Sequence

from contexts.reporting.domain.value_objects.description import Description
from contexts.reporting.domain.value_objects.image_payload import ImagePayload


class EmbeddingGenerator(Protocol):
    def embed(
        self,
        images: Sequence[ImagePayload],
        description: Description,
        *,
        context: str = "",
    ) -> tuple[list[float], str]:
        """Return (combined embedding vector, model version string).

        Implementations should caption each image (if any), blend captions
        with the user's description and any free-form `context` (location,
        incident time, etc.), and produce a single text embedding.
        """
        ...
