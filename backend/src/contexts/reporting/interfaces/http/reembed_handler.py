from __future__ import annotations

from typing import Any

from contexts.matching.infrastructure.embedding.bedrock_embedding_client import (
    BedrockEmbeddingClient,
)
from contexts.reporting.application.commands.reembed_report import (
    ReembedReportCommand,
)
from contexts.reporting.infrastructure.persistence.dynamo_item_report_repository import (
    DynamoItemReportRepository,
)
from shared.application import config
from shared.application.http import (
    handler,
    parse_body,
    require_admin,
    response,
)
from shared.domain.exceptions.domain_exception import InvalidInputError

_command = ReembedReportCommand(
    repository=DynamoItemReportRepository(config.items_table()),
    embedder=BedrockEmbeddingClient(model_version=config.embedding_model_version()),
)


@handler
def lambda_handler(event: dict[str, Any]) -> dict[str, Any]:
    require_admin(event)
    item_id = (event.get("pathParameters") or {}).get("id")
    if not item_id:
        raise InvalidInputError("missing item id")
    body = parse_body(event)
    image = body.get("image", "")
    if not image:
        raise InvalidInputError("image data URI required")
    return response(200, _command.execute(item_id=item_id, image_data_uri=image))
