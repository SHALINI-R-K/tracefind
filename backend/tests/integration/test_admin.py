import base64

from src.contexts.admin.application.commands.moderate_report import (
    ModerateReportCommand,
)
from src.contexts.admin.application.commands.override_match import OverrideMatchCommand
from src.contexts.admin.infrastructure.persistence.dynamo_audit_repository import (
    DynamoAuditRepository,
)
from src.contexts.matching.infrastructure.embedding.bedrock_embedding_client import (
    FakeEmbeddingClient,
)
from src.contexts.matching.infrastructure.persistence.dynamo_match_repository import (
    DynamoMatchRepository,
)
from src.contexts.reporting.application.commands.create_item_report import (
    CreateItemReportCommand,
)
from src.contexts.reporting.application.dtos.report_dto import CreateItemReportInput
from src.contexts.reporting.infrastructure.persistence.dynamo_item_report_repository import (
    DynamoItemReportRepository,
)
from src.shared.domain.value_objects.identifier import UserId
from src.shared.infrastructure.event_bus.dynamodb_stream_event_bus import RecordingEventBus


def _img() -> str:
    raw = b"\x89PNG\r\n\x1a\n" + b"x" * 1024
    return "data:image/png;base64," + base64.b64encode(raw).decode()


def test_archive_writes_audit_entry(dynamo_tables) -> None:
    item_repo = DynamoItemReportRepository(dynamo_tables["items"])
    audit_repo = DynamoAuditRepository(dynamo_tables["audit"])
    create = CreateItemReportCommand(
        repository=item_repo,
        embedder=FakeEmbeddingClient(),
        event_bus=RecordingEventBus(),
        ttl_seconds=3600,
    )
    view = create.execute(
        CreateItemReportInput(
            user_id=str(UserId.new()),
            type="lost",
            description="something inappropriate",
            category="other",
            image_data_uri=_img(),
        )
    )
    cmd = ModerateReportCommand(item_repo=item_repo, audit_repo=audit_repo)
    actor = str(UserId.new())
    result = cmd.archive(item_id=view.id, actor_user_id=actor, reason="abusive content")
    assert result["item"]["status"] == "archived"

    entries, _ = audit_repo.list(actor_user_id=actor, target_id=None, limit=10, cursor=None)
    assert len(entries) == 1
    assert entries[0].action == "archive_item"


def test_override_match_creates_match_and_audit(dynamo_tables) -> None:
    item_repo = DynamoItemReportRepository(dynamo_tables["items"])
    match_repo = DynamoMatchRepository(dynamo_tables["matches"])
    audit_repo = DynamoAuditRepository(dynamo_tables["audit"])
    create = CreateItemReportCommand(
        repository=item_repo,
        embedder=FakeEmbeddingClient(),
        event_bus=RecordingEventBus(),
        ttl_seconds=3600,
    )
    lost = create.execute(
        CreateItemReportInput(
            user_id=str(UserId.new()),
            type="lost",
            description="lost set of keys with red lanyard",
            category="keys",
            image_data_uri=_img(),
        )
    )
    found = create.execute(
        CreateItemReportInput(
            user_id=str(UserId.new()),
            type="found",
            description="found keys near library entrance",
            category="keys",
            image_data_uri=_img(),
        )
    )
    cmd = OverrideMatchCommand(
        item_repo=item_repo, match_repo=match_repo, audit_repo=audit_repo
    )
    actor = str(UserId.new())
    result = cmd.force(
        lost_item_id=lost.id,
        found_item_id=found.id,
        actor_user_id=actor,
        reason="manual link confirmed by reception",
    )
    assert result["match"]["score"] == 1.0

    entries, _ = audit_repo.list(actor_user_id=actor, target_id=None, limit=10, cursor=None)
    assert len(entries) == 1
    assert entries[0].action == "override_match"
