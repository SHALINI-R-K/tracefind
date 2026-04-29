from __future__ import annotations

from typing import Protocol

from contexts.claims.domain.entities.claim import Claim
from shared.domain.value_objects.identifier import ClaimId


class ClaimRepository(Protocol):
    def save_with_item_lock(
        self,
        claim: Claim,
        items_table: str,
    ) -> bool:
        """Persist the claim AND atomically move both items to `claimed`.

        Implemented as a TransactWriteItems with conditional updates on the
        items table. Returns True on success, False if either item was already
        non-active (i.e. claimed by someone else first).
        """
        ...

    def save(self, claim: Claim) -> None: ...

    def get(self, claim_id: ClaimId) -> Claim: ...
