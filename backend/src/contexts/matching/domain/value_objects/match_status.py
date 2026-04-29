from __future__ import annotations

from enum import Enum


class MatchStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
