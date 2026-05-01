from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CreateItemReportInput:
    user_id: str
    type: str
    description: str
    category: str | None
    image_data_uris: tuple[str, ...]  # 1..3 photos as data URIs
    location: str | None = None
    incident_at_iso: str | None = None  # ISO 8601 datetime, optional


@dataclass(frozen=True)
class ItemReportView:
    id: str
    user_id: str
    type: str
    description: str
    category: str | None
    status: str
    created_at: str
    location: str | None = None
    incident_at: str | None = None
    photo_count: int = 1
