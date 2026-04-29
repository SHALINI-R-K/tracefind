from __future__ import annotations

from enum import Enum


class ReportStatus(str, Enum):
    ACTIVE = "active"
    MATCHED = "matched"
    CLAIMED = "claimed"
    ARCHIVED = "archived"
