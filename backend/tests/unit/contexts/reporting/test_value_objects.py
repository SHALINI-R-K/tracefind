import base64

import pytest

from src.contexts.reporting.domain.value_objects.category import Category
from src.contexts.reporting.domain.value_objects.description import Description
from src.contexts.reporting.domain.value_objects.image_payload import ImagePayload
from src.contexts.reporting.domain.value_objects.report_type import ReportType
from src.shared.domain.exceptions.domain_exception import InvalidInputError


def test_report_type_parse_and_opposite() -> None:
    assert ReportType.parse("lost") is ReportType.LOST
    assert ReportType.LOST.opposite() is ReportType.FOUND
    assert ReportType.FOUND.opposite() is ReportType.LOST
    with pytest.raises(InvalidInputError):
        ReportType.parse("misplaced")


def test_description_bounds() -> None:
    Description("a valid description")
    with pytest.raises(InvalidInputError):
        Description("hi")
    with pytest.raises(InvalidInputError):
        Description("x" * 501)


def test_category_optional() -> None:
    assert Category.from_optional(None) is None
    assert Category("bag").value == "bag"
    with pytest.raises(InvalidInputError):
        Category("alien-artifact")


def test_image_payload_data_uri() -> None:
    raw = b"\x89PNG\r\n\x1a\n" + b"x" * 512
    uri = "data:image/png;base64," + base64.b64encode(raw).decode()
    payload = ImagePayload.from_data_uri(uri)
    assert payload.mime == "image/png"
    assert payload.bytes_ == raw

    with pytest.raises(InvalidInputError):
        ImagePayload.from_data_uri("not a uri")
    with pytest.raises(InvalidInputError):
        ImagePayload.from_data_uri("data:image/gif;base64,abc")
