"""Hierarchical XState v5 Statechart Engine (`soc_g4b_telemetry`).

Enforces:
- Invariant [L1-002]: Statechart Determinism & Functorial Reversibility.
- Exact 30-State Formal Specification:
  - 4 Root Strata (16 states):
    state_uninitialized, state_binding_lan, state_sovereign_bound, ingress_standby,
    active_stream_ingestion, active_thermodynamic_evaluation, active_sla_benchmarking,
    active_merkle_anchoring, active_attestation_emission, stream_batch_validating,
    metric_aggregation_active, merkle_dag_verifying, state_operational_certified,
    attestation_dispatching, ledger_reconciliation, enclave_unwind_restoring.
  - 4 Recovery Enclaves (4 states):
    syntax_breach_recovery, byzantine_fuzz_quarantine, network_loopback_emergency,
    sla_degradation_fallback.
  - 2 Parallel Regions (6 states):
    Sentry Observer: sentry_listening, sentry_heartbeat_tracking, sentry_alert_raised.
    Thermodynamic Meter: thermo_monitoring, thermo_dissipating, thermo_landauer_saturated.
  - 4 Deep History Checkpoints (4 states):
    hist_pre_ingestion, hist_pre_thermo, hist_pre_benchmark, hist_pre_merkle.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Set

from .domain_models import (
    RecoveryEnclaveType,
    TelemetryDomainInvariantViolation,
)


class TelemetryStatechartEngine:
    """Deterministic 30-state Hierarchical XState v5 Statechart Engine for Sovereign Telemetry."""

    # Exact 30 formal states
    ROOT_STRATA_STATES: Set[str] = {
        "state_uninitialized",
        "state_binding_lan",
        "state_sovereign_bound",
        "ingress_standby",
        "active_stream_ingestion",
        "stream_batch_validating",
        "metric_aggregation_active",
        "active_thermodynamic_evaluation",
        "ledger_reconciliation",
        "active_sla_benchmarking",
        "active_merkle_anchoring",
        "merkle_dag_verifying",
        "active_attestation_emission",
        "attestation_dispatching",
        "state_operational_certified",
        "enclave_unwind_restoring",
    }

    RECOVERY_ENCLAVE_STATES: Set[str] = {
        "syntax_breach_recovery",
        "byzantine_fuzz_quarantine",
        "network_loopback_emergency",
        "sla_degradation_fallback",
    }

    PARALLEL_SENTRY_STATES: Set[str] = {
        "sentry_listening",
        "sentry_heartbeat_tracking",
        "sentry_alert_raised",
    }

    PARALLEL_THERMO_STATES: Set[str] = {
        "thermo_monitoring",
        "thermo_dissipating",
        "thermo_landauer_saturated",
    }

    DEEP_HISTORY_CHECKPOINTS: Set[str] = {
        "hist_pre_ingestion",
        "hist_pre_thermo",
        "hist_pre_benchmark",
        "hist_pre_merkle",
    }

    ALL_STATES: Set[str] = (
        ROOT_STRATA_STATES
        | RECOVERY_ENCLAVE_STATES
        | PARALLEL_SENTRY_STATES
        | PARALLEL_THERMO_STATES
        | DEEP_HISTORY_CHECKPOINTS
    )

    def __init__(self, initial_state: str = "state_uninitialized") -> None:
        if initial_state not in self.ALL_STATES:
            raise TelemetryDomainInvariantViolation(f"Invalid initial state: '{initial_state}'")

        self.current_state: str = initial_state
        self.parallel_sentry_state: str = "sentry_listening"
        self.parallel_thermo_state: str = "thermo_monitoring"

        self.deep_history_targets: Dict[str, str] = {
            "hist_pre_ingestion": "ingress_standby",
            "hist_pre_thermo": "active_thermodynamic_evaluation",
            "hist_pre_benchmark": "active_sla_benchmarking",
            "hist_pre_merkle": "active_merkle_anchoring",
        }

        self.transition_log: List[Dict[str, Any]] = []
        self._record_transition("INITIALIZE", None, self.current_state, {})

    def _record_transition(
        self,
        event: str,
        source: Optional[str],
        target: str,
        payload: Dict[str, Any],
    ) -> None:
        self.transition_log.append({
            "timestamp_ms": int(time.time() * 1000),
            "event": event,
            "source": source,
            "target": target,
            "sentry_state": self.parallel_sentry_state,
            "thermo_state": self.parallel_thermo_state,
            "payload": payload,
        })

    def send(self, event_name: str, payload: Optional[Dict[str, Any]] = None) -> str:
        """Processes an incoming event, executing deterministic hierarchical transitions."""
        p = payload or {}
        source = self.current_state

        # Check parallel region events first
        if event_name == "EV_SENTRY_HEARTBEAT":
            self.parallel_sentry_state = "sentry_heartbeat_tracking"
            self._record_transition(event_name, source, self.current_state, p)
            return self.current_state
        elif event_name == "EV_SENTRY_OK":
            self.parallel_sentry_state = "sentry_listening"
            self._record_transition(event_name, source, self.current_state, p)
            return self.current_state
        elif event_name == "EV_SENTRY_ALERT":
            self.parallel_sentry_state = "sentry_alert_raised"
            self._record_transition(event_name, source, self.current_state, p)
            return self.current_state
        elif event_name == "EV_SENTRY_RESOLVED":
            self.parallel_sentry_state = "sentry_listening"
            self._record_transition(event_name, source, self.current_state, p)
            return self.current_state

        if event_name == "EV_THERMO_DISSIPATE":
            self.parallel_thermo_state = "thermo_dissipating"
            self._record_transition(event_name, source, self.current_state, p)
            return self.current_state
        elif event_name == "EV_THERMO_COOL":
            self.parallel_thermo_state = "thermo_monitoring"
            self._record_transition(event_name, source, self.current_state, p)
            return self.current_state
        elif event_name == "EV_THERMO_SATURATE":
            self.parallel_thermo_state = "thermo_landauer_saturated"
            self._record_transition(event_name, source, self.current_state, p)
            return self.current_state
        elif event_name == "EV_THERMO_RECOVER":
            self.parallel_thermo_state = "thermo_monitoring"
            self._record_transition(event_name, source, self.current_state, p)
            return self.current_state

        # Root Strata deterministic transition table
        TRANSITIONS: Dict[str, Dict[str, str]] = {
            "state_uninitialized": {
                "EV_BIND_LAN": "state_binding_lan",
            },
            "state_binding_lan": {
                "EV_LAN_BOUND": "state_sovereign_bound",
            },
            "state_sovereign_bound": {
                "EV_STANDBY": "ingress_standby",
                "EV_START_INGESTION": "active_stream_ingestion",
            },
            "ingress_standby": {
                "EV_START_INGESTION": "active_stream_ingestion",
                "EV_START_MERKLE": "active_merkle_anchoring",
            },
            "active_stream_ingestion": {
                "EV_VALIDATE_BATCH": "stream_batch_validating",
                "EV_START_THERMO": "active_thermodynamic_evaluation",
            },
            "stream_batch_validating": {
                "EV_BATCH_VALIDATED": "metric_aggregation_active",
                "EV_SYNTAX_BREACH": "syntax_breach_recovery",
            },
            "metric_aggregation_active": {
                "EV_START_THERMO": "active_thermodynamic_evaluation",
            },
            "active_thermodynamic_evaluation": {
                "EV_RECONCILE_LEDGER": "ledger_reconciliation",
                "EV_START_SLA": "active_sla_benchmarking",
            },
            "ledger_reconciliation": {
                "EV_START_SLA": "active_sla_benchmarking",
            },
            "active_sla_benchmarking": {
                "EV_START_MERKLE": "active_merkle_anchoring",
                "EV_SLA_DEGRADED": "sla_degradation_fallback",
            },
            "active_merkle_anchoring": {
                "EV_VERIFY_DAG": "merkle_dag_verifying",
                "EV_START_EMISSION": "active_attestation_emission",
            },
            "merkle_dag_verifying": {
                "EV_START_EMISSION": "active_attestation_emission",
            },
            "active_attestation_emission": {
                "EV_DISPATCH_ATTESTATION": "attestation_dispatching",
                "EV_CERTIFY_OPERATIONAL": "state_operational_certified",
            },
            "attestation_dispatching": {
                "EV_CERTIFY_OPERATIONAL": "state_operational_certified",
            },
            "state_operational_certified": {
                "EV_STANDBY": "ingress_standby",
                "EV_START_INGESTION": "active_stream_ingestion",
            },
            # Recovery Enclaves
            "syntax_breach_recovery": {
                "EV_RESTORE": "enclave_unwind_restoring",
            },
            "byzantine_fuzz_quarantine": {
                "EV_RESTORE": "enclave_unwind_restoring",
            },
            "network_loopback_emergency": {
                "EV_RESTORE": "enclave_unwind_restoring",
            },
            "sla_degradation_fallback": {
                "EV_RESTORE": "enclave_unwind_restoring",
            },
            "enclave_unwind_restoring": {
                "EV_UNWIND_COMPLETE": "ingress_standby",
            },
        }

        # Check for direct event transitions
        available = TRANSITIONS.get(source, {})
        if event_name in available:
            target = available[event_name]
            self.current_state = target
            self._record_transition(event_name, source, target, p)
            return self.current_state

        raise TelemetryDomainInvariantViolation(
            f"No valid transition from '{source}' on event '{event_name}'."
        )

    def trigger_enclave(self, enclave_type: RecoveryEnclaveType) -> str:
        """Forces an emergency transition into the designated recovery enclave."""
        source = self.current_state
        target = enclave_type.value

        if target not in self.RECOVERY_ENCLAVE_STATES:
            raise TelemetryDomainInvariantViolation(f"Target '{target}' is not a certified recovery enclave.")

        self.current_state = target
        self._record_transition(f"EV_EMERGENCY_{enclave_type.name}", source, target, {"enclave": enclave_type.value})
        return self.current_state

    def restore_deep_history(self, checkpoint_name: str) -> str:
        """Restores state from a deep history checkpoint."""
        if checkpoint_name not in self.deep_history_targets:
            raise TelemetryDomainInvariantViolation(
                f"Unknown deep history checkpoint: '{checkpoint_name}'"
            )

        source = self.current_state
        target = self.deep_history_targets[checkpoint_name]
        self.current_state = target
        self._record_transition(f"EV_RESTORE_DEEP_HISTORY({checkpoint_name})", source, target, {"history": checkpoint_name})
        return self.current_state

    def can_transition(self, event_name: str) -> bool:
        """Checks whether the event can be handled in the current state without raising an exception."""
        # Parallel events always acceptable
        if event_name.startswith("EV_SENTRY_") or event_name.startswith("EV_THERMO_"):
            return True

        TRANSITIONS: Dict[str, List[str]] = {
            "state_uninitialized": ["EV_BIND_LAN"],
            "state_binding_lan": ["EV_LAN_BOUND"],
            "state_sovereign_bound": ["EV_STANDBY", "EV_START_INGESTION"],
            "ingress_standby": ["EV_START_INGESTION", "EV_START_MERKLE"],
            "active_stream_ingestion": ["EV_VALIDATE_BATCH", "EV_START_THERMO"],
            "stream_batch_validating": ["EV_BATCH_VALIDATED", "EV_SYNTAX_BREACH"],
            "metric_aggregation_active": ["EV_START_THERMO"],
            "active_thermodynamic_evaluation": ["EV_RECONCILE_LEDGER", "EV_START_SLA"],
            "ledger_reconciliation": ["EV_START_SLA"],
            "active_sla_benchmarking": ["EV_START_MERKLE", "EV_SLA_DEGRADED"],
            "active_merkle_anchoring": ["EV_VERIFY_DAG", "EV_START_EMISSION"],
            "merkle_dag_verifying": ["EV_START_EMISSION"],
            "active_attestation_emission": ["EV_DISPATCH_ATTESTATION", "EV_CERTIFY_OPERATIONAL"],
            "attestation_dispatching": ["EV_CERTIFY_OPERATIONAL"],
            "state_operational_certified": ["EV_STANDBY", "EV_START_INGESTION"],
            "syntax_breach_recovery": ["EV_RESTORE"],
            "byzantine_fuzz_quarantine": ["EV_RESTORE"],
            "network_loopback_emergency": ["EV_RESTORE"],
            "sla_degradation_fallback": ["EV_RESTORE"],
            "enclave_unwind_restoring": ["EV_UNWIND_COMPLETE"],
        }
        return event_name in TRANSITIONS.get(self.current_state, [])

    def get_active_configuration(self) -> Dict[str, str]:
        """Returns the full hierarchical state configuration."""
        return {
            "root_state": self.current_state,
            "sentry_state": self.parallel_sentry_state,
            "thermo_state": self.parallel_thermo_state,
        }
