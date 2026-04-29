from __future__ import annotations

import base64
import re
from dataclasses import dataclass

from shared.domain.exceptions.domain_exception import InvalidInputError

_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
_DATA_URI = re.compile(r"^data:(?P<mime>image/(jpeg|png|webp));base64,(?P<data>.+)$", re.DOTALL)
_ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}


@dataclass(frozen=True)
class ImagePayload:
    """Transient image bytes — never persisted, only used to compute embeddings."""

    bytes_: bytes
    mime: str

    @classmethod
    def from_data_uri(cls, raw: str) -> "ImagePayload":
        if not raw:
            raise InvalidInputError("image is required")
        match = _DATA_URI.match(raw)
        if not match:
            raise InvalidInputError("image must be a data URI (image/jpeg|png|webp)")
        mime = match.group("mime")
        if mime not in _ALLOWED_MIME:
            raise InvalidInputError(f"unsupported image mime: {mime}")
        try:
            payload = base64.b64decode(match.group("data"), validate=True)
        except (ValueError, base64.binascii.Error) as exc:  # type: ignore[attr-defined]
            raise InvalidInputError("image base64 is invalid") from exc
        if len(payload) > _MAX_BYTES:
            raise InvalidInputError("image exceeds 5 MB cap")
        if len(payload) < 256:
            raise InvalidInputError("image is too small to be valid")
        return cls(payload, mime)
