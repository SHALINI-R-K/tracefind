from __future__ import annotations

from typing import Iterable, Protocol

from shared.domain.events.domain_event import DomainEvent


class EventBus(Protocol):
    def publish(self, events: Iterable[DomainEvent]) -> None: ...


class StreamEventBus:
    """No-op publisher.

    Domain events for the reporting/matching pipeline are propagated implicitly
    through DynamoDB Streams attached to the Items and Matches tables — the
    write to the table IS the publish. This class exists so application
    services can declare an EventBus dependency uniformly; for tests we swap
    in a recording fake.
    """

    def publish(self, events: Iterable[DomainEvent]) -> None:
        return None


class RecordingEventBus:
    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    def publish(self, events: Iterable[DomainEvent]) -> None:
        self.published.extend(events)
