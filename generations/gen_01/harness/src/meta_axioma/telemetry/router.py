"""Telemetry API router and event dispatcher."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine, Dict, List, Optional
from meta_axioma.telemetry.events import EventType, TelemetryEvent

AsyncListener = Callable[[TelemetryEvent], Coroutine[Any, Any, None]]
SyncListener = Callable[[TelemetryEvent], None]


class TelemetryRouter:
    """Async event dispatcher routing telemetry to API subscribers, logs, and consoles."""

    def __init__(self):
        self._async_subscribers: List[AsyncListener] = []
        self._sync_subscribers: List[SyncListener] = []
        self._event_history: List[TelemetryEvent] = []

    def subscribe_async(self, listener: AsyncListener) -> None:
        """Subscribes an asynchronous listener."""
        self._async_subscribers.append(listener)

    def subscribe_sync(self, listener: SyncListener) -> None:
        """Subscribes a synchronous listener."""
        self._sync_subscribers.append(listener)

    async def emit(self, event: TelemetryEvent) -> None:
        """Dispatches an event asynchronously to all subscribers."""
        self._event_history.append(event)

        # Dispatch sync subscribers
        for sync_fn in self._sync_subscribers:
            try:
                sync_fn(event)
            except Exception as e:
                print(f"[TelemetryRouter Error] Sync subscriber failure: {e}")

        # Dispatch async subscribers concurrently
        if self._async_subscribers:
            await asyncio.gather(
                *[subscriber(event) for subscriber in self._async_subscribers],
                return_exceptions=True,
            )

    def get_events(
        self,
        event_type: Optional[EventType] = None,
        epoch: Optional[int] = None,
    ) -> List[TelemetryEvent]:
        """Queries telemetry history by event type and/or epoch."""
        events = self._event_history
        if event_type is not None:
            events = [e for e in events if e.event_type == event_type]
        if epoch is not None:
            events = [e for e in events if e.epoch == epoch]
        return events

    def get_latest_event(self) -> Optional[TelemetryEvent]:
        """Returns the most recent emitted event."""
        return self._event_history[-1] if self._event_history else None
