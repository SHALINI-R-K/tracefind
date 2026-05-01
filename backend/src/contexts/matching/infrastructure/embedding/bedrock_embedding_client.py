from __future__ import annotations

import base64
import json
import math
import os
import urllib.request
import urllib.error

from contexts.reporting.domain.services.embedding_generator import EmbeddingGenerator
from contexts.reporting.domain.value_objects.description import Description
from contexts.reporting.domain.value_objects.image_payload import ImagePayload
from shared.domain.exceptions.domain_exception import UpstreamError
from shared.infrastructure.aws.boto3_clients import bedrock_runtime_client
from shared.infrastructure.aws.secrets import get_secret

_TEXT_MODEL = os.environ.get("BEDROCK_TEXT_MODEL", "amazon.titan-embed-text-v2:0")
_GROQ_SECRET_NAME = os.environ.get("GROQ_SECRET_NAME", "tracefind/groq-api-key")
_GROQ_MODEL = os.environ.get("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
_GROQ_TIMEOUT_SECONDS = float(os.environ.get("GROQ_TIMEOUT_SECONDS", "5"))


class BedrockEmbeddingClient(EmbeddingGenerator):
    def __init__(self, model_version: str) -> None:
        self._model_version = model_version

    def embed(
        self, image: ImagePayload, description: Description
    ) -> tuple[list[float], str]:
        # 1. Ask Groq to caption the image
        groq_caption = self._invoke_groq_vision(image)
        
        # 2. Combine user description with AI caption
        combined_text = f"User Description: {description.value}\n\nAI Visual Analysis: {groq_caption}"
        
        # 3. Generate a vector embedding for the combined text
        text_vec = self._invoke_text(combined_text)
        
        # We don't use image embeddings anymore, so we return the l2 normalized text embedding.
        normalized_vec = _l2_normalize(text_vec, 1.0)
        return normalized_vec, self._model_version

    def _invoke_groq_vision(self, image: ImagePayload) -> str:
        api_key = get_secret(_GROQ_SECRET_NAME)
        b64_image = base64.b64encode(image.bytes_).decode("utf-8")
        data_uri = f"data:{image.mime};base64,{b64_image}"

        payload = {
            "model": _GROQ_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this lost/found item in high detail. Focus on its color, brand, distinct physical features, text/logos, and condition. Do not talk about the background. Be concise but highly descriptive."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_uri
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300,
            "temperature": 0.2
        }

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "TraceFind-Backend/1.0 (Python/urllib)"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=_GROQ_TIMEOUT_SECONDS) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise UpstreamError(f"Groq API error: {e.code} - {error_body}") from e
        except Exception as exc:
            raise UpstreamError(f"Groq API failed: {exc}") from exc

        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise UpstreamError(
                f"Groq returned unexpected response shape: {body}"
            ) from exc
        if not isinstance(content, str) or not content.strip():
            raise UpstreamError(f"Groq returned empty caption: {body}")
        return content

    def _invoke_text(self, text: str) -> list[float]:
        body = json.dumps({"inputText": text})
        try:
            resp = bedrock_runtime_client().invoke_model(
                modelId=_TEXT_MODEL,
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
