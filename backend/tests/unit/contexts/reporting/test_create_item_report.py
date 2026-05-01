import base64

from contexts.matching.infrastructure.embedding.bedrock_embedding_client import (
    FakeEmbeddingClient,
)
from contexts.reporting.application.commands.create_item_report import (
    CreateItemReportCommand,
)
from contexts.reporting.application.dtos.report_dto import CreateItemReportInput
from contexts.reporting.domain.entities.item_report import ItemReport
from contexts.reporting.domain.repositories.item_report_repository import (
    ItemReportRepository,
)
from contexts.reporting.domain.value_objects.report_status import ReportStatus
from contexts.reporting.domain.value_objects.report_type import ReportType
from shared.domain.value_objects.identifier import ItemId, UserId
from shared.infrastructure.event_bus.dynamodb_stream_event_bus import RecordingEventBus


class InMemoryItemRepo(ItemReportRepository):
    def __init__(self) -> None:
        self.items: dict[str, ItemReport] = {}

    def save(self, report: ItemReport) -> None:
        self.items[str(report.id)] = report

    def get(self, item_id: ItemId) -> ItemReport:
        return self.items[str(item_id)]

    def list_by_user(self, user_id: UserId, *, limit: int, cursor: str | None):
        return [r for r in self.items.values() if r.user_id == user_id], None

    def list_active_candidates(self, *, opposite_of: ReportType, days_back: int, embedding_model_version: str, limit: int):
        return [
            r
            for r in self.items.values()
            if r.type == opposite_of.opposite()
            and r.status == ReportStatus.ACTIVE
            and r.embedding_model_version == embedding_model_version
        ][:limit]

    def update_status_active_to(self, item_id: ItemId, *, target):
        r = self.items.get(str(item_id))
        if not r or r.status != ReportStatus.ACTIVE:
            return False
        r.status = target
        return True


def test_create_item_report_persists_and_emits_event() -> None:
    repo = InMemoryItemRepo()
    bus = RecordingEventBus()
    cmd = CreateItemReportCommand(
        repository=repo,
        embedder=FakeEmbeddingClient(),
        event_bus=bus,
        ttl_seconds=3600,
    )
    raw = b"\x89PNG\r\n\x1a\n" + b"x" * 1024
    image = "data:image/png;base64," + base64.b64encode(raw).decode()
    view = cmd.execute(
        CreateItemReportInput(
            user_id=str(UserId.new()),
            type="lost",
            description="black backpack with red zipper",
            category="bag",
            image_data_uris=(image,),
        )
    )
    assert view.type == "lost"
    assert view.status == "active"
    assert len(repo.items) == 1
    assert any(e.name == "reporting.item_reported" for e in bus.published)
