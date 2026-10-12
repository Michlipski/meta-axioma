"""Human-in-the-Loop (HITL) asynchronous callback controller."""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Optional
from meta_axioma.types import EpochTelemetry, HitlAction, HitlVerdict, NegativeAxiom

HitlCallback = Callable[[EpochTelemetry], Awaitable[HitlVerdict]]


class HitlController:
    """Manages asynchronous interrupts at epoch boundaries and structural transitions."""

    def __init__(self, custom_callback: Optional[HitlCallback] = None):
        self._custom_callback = custom_callback
        self.is_paused = False
        self._resume_event = asyncio.Event()
        self._resume_event.set()

    def set_callback(self, callback: HitlCallback) -> None:
        """Sets or replaces the asynchronous callback hook."""
        self._custom_callback = callback

    def pause(self) -> None:
        """Pauses the execution loop asynchronously."""
        self.is_paused = True
        self._resume_event.clear()

    def resume(self) -> None:
        """Resumes the execution loop."""
        self.is_paused = False
        self._resume_event.set()

    async def interrupt(self, telemetry: EpochTelemetry) -> HitlVerdict:
        """Triggers the asynchronous HITL pause and invokes the registered callback."""
        # Await resume event if explicitly paused
        await self._resume_event.wait()

        if self._custom_callback is not None:
            # Dispatch to registered external async handler (e.g. WebSocket / Web UI / CLI)
            return await self._custom_callback(telemetry)

        # Default async handler (Auto-approves while logging telemetry to stdout)
        return self._default_verdict(telemetry)

    def _default_verdict(self, telemetry: EpochTelemetry) -> HitlVerdict:
        """Default non-blocking verdict when no external supervisor is attached."""
        return HitlVerdict(
            action=HitlAction.APPROVE,
            feedback=f"Auto-approved at epoch {telemetry.epoch} boundary.",
        )
