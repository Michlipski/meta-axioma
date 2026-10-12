"""Telemetry event definitions and schemas."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class EventType(str, Enum):
    EPOCH_STARTED = "EPOCH_STARTED"
    CANDIDATE_GENERATED = "CANDIDATE_GENERATED"
    USER_SEED_SUBMITTED = "USER_SEED_SUBMITTED"
    SIMULATION_COMPLETED = "SIMULATION_COMPLETED"
    EVALUATION_COMPLETED = "EVALUATION_COMPLETED"
    COMPARATIVE_EVALUATION_COMPLETED = "COMPARATIVE_EVALUATION_COMPLETED"
    HITL_INTERRUPT_TRIGGERED = "HITL_INTERRUPT_TRIGGERED"
    HITL_RESPONSE_RECEIVED = "HITL_RESPONSE_RECEIVED"
    AXIOM_COMMITTED = "AXIOM_COMMITTED"
    AXIOM_REJECTED = "AXIOM_REJECTED"
    NEGATIVE_AXIOM_INJECTED = "NEGATIVE_AXIOM_INJECTED"
    PHASE_TRANSITION_JETTISON = "PHASE_TRANSITION_JETTISON"
    AXIOM_LOOKAHEAD_EVALUATED = "AXIOM_LOOKAHEAD_EVALUATED"
    EPOCH_COMPLETED = "EPOCH_COMPLETED"


@dataclass
class TelemetryEvent:
    """An event emitted by the bootstrapper runtime."""
    event_type: EventType
    epoch: int
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "epoch": self.epoch,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }
