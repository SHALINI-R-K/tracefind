from __future__ import annotations

import base64
import json
import math
import os

from contexts.reporting.domain.services.embedding_generator import EmbeddingGenerator
from contexts.reporting.domain.value_objects.description import Description
from contexts.reporting.domain.value_objects.image_payload import ImagePayload
from shared.domain.exceptions.domain_exception import UpstreamError
from shared.infrastructure.aws.boto3_clients import bedrock_runtime_client

_IMAGE_MODEL = os.environ.get("BEDROCK_IMAGE_MODEL", "amazon.titan-embed-image-v1")
_TEXT_MODEL = os.environ.get("BEDROCK_TEXT_MODEL", "amazon.titan-embed-text-v2:0")
_IMAGE_WEIGHT = float(os.environ.get("EMBEDDING_IMAGE_WEIGHT", "0.6"))
_TEXT_WEIGHT = float(os.environ.get("EMBEDDING_TEXT_WEIGHT", "0.4"))


class BedrockEmbeddingClient(EmbeddingGenerator):
    def __init__(self, model_version: str) -> None:
        self._model_version = model_version

    def embed(
        self, image: ImagePayload, description: Description
    ) -> tuple[list[float], str]:
        image_vec = self._invoke_image(image)
        text_vec = self._invoke_text(description.value)
        combined = _l2_normalize(image_vec, _IMAGE_WEIGHT) + _l2_normalize(
            text_vec, _TEXT_WEIGHT
        )
        return combined, self._model_version

    def _invoke_image(self, image: ImagePayload) -> list[float]:
        body = json.dumps(
            {"inputImage": base64.b64encode(image.bytes_).decode()}
        )
        return self._invoke(_IMAGE_MODEL, body)

    def _invoke_text(self, text: str) -> list[float]:
        body = json.dumps({"inputText": text})
        return self._invoke(_TEXT_MODEL, body)

    def _invoke(self, model_id: str, body: str) -> list[float]:
        try:
            resp = bedrock_runtime_client().invoke_model(
                modelId=model_id,
                body=body,
                contentType="application/json",
                accept="application/json",
            )
            payload = json.loads(resp["body"].read())
            return [float(x) for x in payload.get("embedding", [])]
        except Exception as exc:  # noqa: BLE001
            raise UpstreamError(f"bedrock embedding failed: {exc}") from exc


def _l2_normalize(vec: list[float], weight: float) -> list[float]:
    if not vec:
        return []
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [(x / norm) * weight for x in vec]


class FakeEmbeddingClient(EmbeddingGenerator):
    """Deterministic test double — hashes inputs to a 16-dim vector."""

    def __init__(self, model_version: str = "fake-v1") -> None:
        self._model_version = model_version

    def embed(
        self, image: ImagePayload, description: Description
    ) -> tuple[list[float], str]:
        seed = (image.bytes_[:16] + description.value.encode())[:32]
        vec = [(b / 255.0) * 2 - 1 for b in seed]
        while len(vec) < 16:
            vec.append(0.0)
        return vec[:16], self._model_version
