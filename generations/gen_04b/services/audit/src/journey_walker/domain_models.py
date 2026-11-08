"""Domain models and formal dataclasses for the Headless UI Journey Walker ([L1-G4B-017]).

Invariants Enforced:
  - [L1-G4B-017]: Headless Journey Walker & Statechart Covering-Path Fuzzer
  - [L1-G3B-013]: Empirical Journey Observation & Subprocess Grounding
  - [NEG-PRIMITIVE-001]: Pure Functorial Determinism & Reversible Diagnostics
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
import time
from typing import Any, Dict, List, Optional


class JourneyVerificationFailure(Exception):
    """Raised when a journey walk fails due to step failure, unhandled console error, or latency breach."""


class DOMMutationTimeoutViolation(JourneyVerificationFailure):
    """Raised when expected visual DOM mutation fails to appear within max_latency_ms."""


class OcclusionViolation(JourneyVerificationFailure):
    """Raised when an interactive touch target is occluded by higher z-index element."""


class ViewportClippingViolation(JourneyVerificationFailure):
    """Raised when an interactive touch target lies partially or wholly outside the visible viewport."""


@dataclass(frozen=True)
class BoundingBox:
    """2D Cartesian bounding box representation for layout and occlusion calculation."""
    x: float
    y: float
    width: float
    height: float
    z_index: int = 0
    is_visible: bool = True
    selector: str = ""

    def contains_point(self, px: float, py: float) -> bool:
        """Evaluates whether point (px, py) falls inside this bounding box."""
        return (
            self.x <= px <= (self.x + self.width) and
            self.y <= py <= (self.y + self.height)
        )

    @property
    def center_point(self) -> tuple[float, float]:
        """Calculates center coordinates (x + w/2, y + h/2)."""
        return (self.x + self.width / 2.0, self.y + self.height / 2.0)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BoundingBox:
        return cls(
            x=float(data.get("x", 0.0)),
            y=float(data.get("y", 0.0)),
            width=float(data.get("width", 0.0)),
            height=float(data.get("height", 0.0)),
            z_index=int(data.get("z_index", 0)),
            is_visible=bool(data.get("is_visible", True)),
            selector=str(data.get("selector", "")),
        )


@dataclass(frozen=True)
class JourneyStep:
    """Structured declarative journey step specification."""
    step_id: str
    action_type: str             # "CLICK", "INPUT", "DRAG", "KEY_PRESS", "NAVIGATE", "WAIT"
    target_selector: str         # CSS selector, e.g. "#template-spring-queen", "[data-action='EV_ONBOARD']"
    input_value: Optional[str] = None   # Value to type, select option, or drag delta
    expected_state: Optional[str] = None  # Expected StatechartIR state (e.g. "active.onboarded")
    expected_dom_mutation: Optional[str] = None  # Selector or text that must appear in DOM
    max_latency_ms: int = 200    # Maximum allowable UI reaction time
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "action_type": self.action_type,
            "target_selector": self.target_selector,
            "input_value": self.input_value,
            "expected_state": self.expected_state,
            "expected_dom_mutation": self.expected_dom_mutation,
            "max_latency_ms": self.max_latency_ms,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> JourneyStep:
        return cls(
            step_id=str(data["step_id"]),
            action_type=str(data.get("action_type", "CLICK")).upper(),
            target_selector=str(data.get("target_selector", "")),
            input_value=data.get("input_value"),
            expected_state=data.get("expected_state"),
            expected_dom_mutation=data.get("expected_dom_mutation"),
            max_latency_ms=int(data.get("max_latency_ms", 200)),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass(frozen=True)
class JourneyStepResult:
    """Execution telemetry record for an individual journey step."""
    step_id: str
    status: str                  # "PASSED" | "FAILED"
    latency_ms: float
    action_type: str
    target_selector: str
    dom_mutation_verified: bool
    bounding_box: Optional[BoundingBox] = None
    error_message: Optional[str] = None
    state_after: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.bounding_box:
            d["bounding_box"] = self.bounding_box.to_dict()
        return d


@dataclass(frozen=True)
class JourneyReport:
    """Consolidated attestation report for a complete headless journey execution."""
    total_steps_executed: int
    statechart_coverage_pct: float  # Must be >= 90.0 for passing certification
    unhandled_console_errors: List[str]
    max_observed_latency_ms: float
    journey_status: str             # "PASSED" | "FAILED"
    step_results: List[JourneyStepResult]
    flow_name: str = "AnonymousJourney"
    timestamp: float = field(default_factory=time.time)
    witness_hash: str = ""

    def calculate_witness_hash(self) -> str:
        """Computes deterministic SHA-256 attestation digest."""
        payload = {
            "total_steps_executed": self.total_steps_executed,
            "statechart_coverage_pct": round(self.statechart_coverage_pct, 4),
            "unhandled_console_errors": self.unhandled_console_errors,
            "max_observed_latency_ms": round(self.max_observed_latency_ms, 2),
            "journey_status": self.journey_status,
            "flow_name": self.flow_name,
            "step_ids": [s.step_id for s in self.step_results],
        }
        raw = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        h = self.witness_hash or self.calculate_witness_hash()
        return {
            "total_steps_executed": self.total_steps_executed,
            "statechart_coverage_pct": self.statechart_coverage_pct,
            "unhandled_console_errors": list(self.unhandled_console_errors),
            "max_observed_latency_ms": self.max_observed_latency_ms,
            "journey_status": self.journey_status,
            "step_results": [s.to_dict() for s in self.step_results],
            "flow_name": self.flow_name,
            "timestamp": self.timestamp,
            "witness_hash": h,
        }

    def save_to_file(self, path: str) -> None:
        """Serializes journey verification report to JSON on disk."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
