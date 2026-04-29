import base64

import pytest

from src.contexts.claims.application.commands.confirm_claim import ConfirmClaimCommand
from src.contexts.claims.infrastructure.persistence.dynamo_claim_repository import (
    DynamoClaimRepository,
)
from src.contexts.matching.domain.entities.match import Match
from src.contexts.matching.domain.value_objects.similarity_score import SimilarityScore
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
from src.shared.domain.exceptions.domain_exception import ConflictError
from src.shared.domain.value_objects.identifier import UserId
from src.shared.infrastructure.event_bus.dynamodb_stream_event_bus import RecordingEventBus


def _img() -> str:
    raw = b"\x89PNG\r\n\x1a\n" + b"x" * 1024
    return "data:image/png;base64," + base64.b64encode(raw).decode()


def _seed_match(dynamo_tables) -> tuple[str, str, str]:
    item_repo = DynamoItemReportRepository(dynamo_tables["items"])
    create = CreateItemReportCommand(
        repository=item_repo,
        embedder=FakeEmbeddingClient(),
        event_bus=RecordingEventBus(),
        ttl_seconds=3600,
    )
    lost_user = str(UserId.new())
    found_user = str(UserId.new())
    lost = create.execute(
        CreateItemReportInput(
            user_id=lost_user,
            type="lost",
            description="black leather wallet with cards",
            category="wallet",
            image_data_uri=_img(),
        )
    )
    found = create.execute(
        CreateItemReportInput(
            user_id=found_user,
            type="found",
            description="leather wallet found near gate",
            category="wallet",
            image_data_uri=_img(),
        )
    )

    match_repo = DynamoMatchRepository(dynamo_tables["matches"])
    from src.shared.domain.value_objects.identifier import ItemId

    match = Match.propose(
        lost_item_id=ItemId(lost.id),
        found_item_id=ItemId(found.id),
        score=SimilarityScore(0.9),
        lost_user_id=lost_user,
        found_user_id=found_user,
    )
    match_repo.save(match)
    return lost.id, found.id, str(match.id)


def test_first_claim_wins_second_conflicts(dynamo_tables) -> None:
    lost_id, found_id, match_id = _seed_match(dynamo_tables)
    cmd = ConfirmClaimCommand(
        claim_repo=DynamoClaimRepository(dynamo_tables["claims"]),
        match_repo=DynamoMatchRepository(dynamo_tables["matches"]),
        item_repo=DynamoItemReportRepository(dynamo_tables["items"]),
        items_table_name=dynamo_tables["items"],
    )
    item_repo = DynamoItemReportRepository(dynamo_tables["items"])
    from src.shared.domain.value_objects.identifier import ItemId

    lost = item_repo.get(ItemId(lost_id))
    result = cmd.execute(
        item_id=lost_id,
        match_id=match_id,
        decision="confirm",
        caller_user_id=str(lost.user_id),
    )
    assert result["status"] == "confirmed"

    with pytest.raises(ConflictError):
        cmd.execute(
            item_id=lost_id,
            match_id=match_id,
            decision="confirm",
            caller_user_id=str(lost.user_id),
        )


def test_reject_does_not_lock_items(dynamo_tables) -> None:
    lost_id, _found_id, match_id = _seed_match(dynamo_tables)
    cmd = ConfirmClaimCommand(
        claim_repo=DynamoClaimRepository(dynamo_tables["claims"]),
        match_repo=DynamoMatchRepository(dynamo_tables["matches"]),
        item_repo=DynamoItemReportRepository(dynamo_tables["items"]),
        items_table_name=dynamo_tables["items"],
    )
    item_repo = DynamoItemReportRepository(dynamo_tables["items"])
    from src.contexts.reporting.domain.value_objects.report_status import ReportStatus
    from src.shared.domain.value_objects.identifier import ItemId

    lost = item_repo.get(ItemId(lost_id))
    cmd.execute(
        item_id=lost_id,
        match_id=match_id,
        decision="reject",
        caller_user_id=str(lost.user_id),
    )
    refreshed = item_repo.get(ItemId(lost_id))
    assert refreshed.status == ReportStatus.ACTIVE
