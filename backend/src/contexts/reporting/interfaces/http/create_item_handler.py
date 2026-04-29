from __future__ import annotations

from dataclasses import asdict
from typing import Any

from contexts.matching.infrastructure.embedding.bedrock_embedding_client import (
    BedrockEmbeddingClient,
)
from contexts.reporting.application.commands.create_item_report import (
    CreateItemReportCommand,
)
from contexts.reporting.application.dtos.report_dto import CreateItemReportInput
from contexts.reporting.infrastructure.persistence.dynamo_item_report_repository import (
    DynamoItemReportRepository,
)
from shared.application import config
from shared.application.http import (
    caller_user_id,
    handler,
    parse_body,
    response,
)
from shared.infrastructure.event_bus.dynamodb_stream_event_bus import StreamEventBus

_repo = DynamoItemReportRepository(config.items_table())
_embedder = BedrockEmbeddingClient(model_version=config.embedding_model_version())
_command = CreateItemReportCommand(
    repository=_repo,
    embedder=_embedder,
    event_bus=StreamEventBus(),
    ttl_seconds=config.item_ttl_seconds(),
)


@handler
def lambda_handler(event: dict[str, Any]) -> dict[str, Any]:
    body = parse_body(event)
    user_id = caller_user_id(event)
    payload = CreateItemReportInput(
        user_id=user_id,
        type=body.get("type", ""),
        description=body.get("description", ""),
        category=body.get("category"),
        image_data_uri=body.get("image", ""),
    )
    view = _command.execute(payload)
    return response(201, asdict(view))
