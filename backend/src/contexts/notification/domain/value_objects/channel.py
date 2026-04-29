from __future__ import annotations

from enum import Enum


class NotificationType(str, Enum):
    MATCH_FOUND = "match_found"
    CLAIM_CONFIRMED = "claim_confirmed"
    CLAIM_REJECTED = "claim_rejected"
