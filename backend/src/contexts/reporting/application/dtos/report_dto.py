from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateItemReportInput:
    user_id: str
    type: str
    description: str
    category: str | None
    image_data_uri: str


@dataclass(frozen=True)
class ItemReportView:
    id: str
    user_id: str
    type: str
    description: str
    category: str | None
    status: str
    created_at: str
