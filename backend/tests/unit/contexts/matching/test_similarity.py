from contexts.matching.domain.services.matching_service import MatchingService
from contexts.matching.domain.value_objects.embedding import Embedding
from contexts.matching.domain.value_objects.similarity_score import (
    MatchThreshold,
    SimilarityScore,
)
from contexts.reporting.domain.entities.item_report import ItemReport
from contexts.reporting.domain.value_objects.description import Description
from contexts.reporting.domain.value_objects.report_status import ReportStatus
from contexts.reporting.domain.value_objects.report_type import ReportType
from shared.domain.value_objects.identifier import ItemId, UserId
from shared.domain.value_objects.timestamp import Timestamp


def _report(t: ReportType, vec: list[float]) -> ItemReport:
    return ItemReport(
        id=ItemId.new(),
        user_id=UserId.new(),
        type=t,
        description=Description("a test report description"),
        category=None,
        status=ReportStatus.ACTIVE,
        embedding=vec,
        embedding_model_version="test-v1",
        created_at=Timestamp.now(),
        ttl=Timestamp.now().epoch_seconds() + 3600,
    )


def test_cosine_identical_is_one() -> None:
    a = Embedding((1.0, 0.0, 0.0))
    b = Embedding((1.0, 0.0, 0.0))
    assert a.cosine(b) == 1.0


def test_similarity_score_threshold() -> None:
    assert SimilarityScore(0.9).above(MatchThreshold(0.75))
    assert not SimilarityScore(0.5).above(MatchThreshold(0.75))


def test_matching_service_orders_lost_then_found() -> None:
    new = _report(ReportType.LOST, [1.0, 0.0])
    cand_match = _report(ReportType.FOUND, [1.0, 0.0])
    cand_miss = _report(ReportType.FOUND, [0.0, 1.0])
    service = MatchingService(threshold=MatchThreshold(0.5))
    matches = service.find_matches(new, [cand_match, cand_miss])
    assert len(matches) == 1
    assert matches[0].lost_item_id == new.id
    assert matches[0].found_item_id == cand_match.id


def test_matching_service_skips_mismatched_versions() -> None:
    new = _report(ReportType.LOST, [1.0, 0.0])
    other = _report(ReportType.FOUND, [1.0, 0.0])
    other.embedding_model_version = "different-version"
    service = MatchingService(threshold=MatchThreshold(0.5))
    assert service.find_matches(new, [other]) == []
