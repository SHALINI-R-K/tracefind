import base64

from contexts.matching.infrastructure.embedding.bedrock_embedding_client import (
    FakeEmbeddingClient,
)
from contexts.reporting.application.commands.create_item_report import (
    CreateItemReportCommand,
)
from contexts.reporting.application.dtos.report_dto import CreateItemReportInput
from contexts.reporting.domain.value_objects.report_status import ReportStatus
from contexts.reporting.domain.value_objects.report_type import ReportType
from contexts.reporting.infrastructure.persistence.dynamo_item_report_repository import (
    DynamoItemReportRepository,
)
from shared.domain.value_objects.identifier import UserId
from shared.infrastructure.event_bus.dynamodb_stream_event_bus import RecordingEventBus


def _img() -> str:
    raw = b"\x89PNG\r\n\x1a\n" + b"x" * 1024
    return "data:image/png;base64," + base64.b64encode(raw).decode()


def test_create_and_list(dynamo_tables) -> None:
    repo = DynamoItemReportRepository(dynamo_tables["items"])
    cmd = CreateItemReportCommand(
        repository=repo,
        embedder=FakeEmbeddingClient(),
        event_bus=RecordingEventBus(),
        ttl_seconds=3600,
    )
    user_id = str(UserId.new())
    cmd.execute(
        CreateItemReportInput(
            user_id=user_id,
            type="lost",
            description="black backpack with red zipper",
            category="bag",
            image_data_uri=_img(),
        )
    )
    cmd.execute(
        CreateItemReportInput(
            user_id=user_id,
            type="found",
            description="silver phone in cafeteria",
            category="phone",
            image_data_uri=_img(),
        )
    )
    items, _ = repo.list_by_user(UserId(user_id), limit=10, cursor=None)
    assert len(items) == 2
    assert {i.type for i in items} == {ReportType.LOST, ReportType.FOUND}


def test_active_candidates_filtered_by_version(dynamo_tables) -> None:
    repo = DynamoItemReportRepository(dynamo_tables["items"])
    cmd = CreateItemReportCommand(
        repository=repo,
        embedder=FakeEmbeddingClient(model_version="v1"),
        event_bus=RecordingEventBus(),
        ttl_seconds=3600,
    )
    cmd.execute(
        CreateItemReportInput(
            user_id=str(UserId.new()),
            type="found",
            description="black backpack found in library",
            category="bag",
            image_data_uri=_img(),
        )
    )
    candidates = repo.list_active_candidates(
        opposite_of=ReportType.LOST,
        days_back=2,
        embedding_model_version="v1",
        limit=10,
    )
    assert len(candidates) == 1
    candidates_other = repo.list_active_candidates(
        opposite_of=ReportType.LOST,
        days_back=2,
        embedding_model_version="v2",
        limit=10,
    )
    assert candidates_other == []


def test_status_conditional_update(dynamo_tables) -> None:
    repo = DynamoItemReportRepository(dynamo_tables["items"])
    cmd = CreateItemReportCommand(
        repository=repo,
        embedder=FakeEmbeddingClient(),
        event_bus=RecordingEventBus(),
        ttl_seconds=3600,
    )
    view = cmd.execute(
        CreateItemReportInput(
            user_id=str(UserId.new()),
            type="lost",
            description="another test report description",
            category="other",
            image_data_uri=_img(),
        )
    )
    from shared.domain.value_objects.identifier import ItemId

    assert repo.update_status_active_to(ItemId(view.id), target=ReportStatus.CLAIMED) is True
    assert repo.update_status_active_to(ItemId(view.id), target=ReportStatus.CLAIMED) is False
