from __future__ import annotations

from typing import Protocol

from contexts.admin.domain.entities.audit_entry import AuditEntry


class AuditRepository(Protocol):
    def append(self, entry: AuditEntry) -> None: ...

    def list(
        self,
        *,
        actor_user_id: str | None,
        target_id: str | None,
        limit: int,
        cursor: str | None,
    ) -> tuple[list[AuditEntry], str | None]: ...
