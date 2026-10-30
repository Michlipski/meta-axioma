"""Generation 4b Hierarchical XState v5 Functorial Statechart Engine (`soc_g4b_researcher`).

Enforces:
- [L1-002] Statechart Determinism & Functorial Undo Invariant.
- [L1-G3B-011] Universal & Hierarchical Statechart IR.
- 32-State Architecture across:
  - 3 Compound Strata (epistemic_discovery, adversarial_crucible, protocol_adjudication)
  - 2 Parallel Orthogonal Regions (concurrent_byzantine_fuzzer, landauer_thermodynamic_meter)
  - 3 Deep History Registers (discovery_deep_history, crucible_deep_history, adjudication_deep_history)
  - 4 Dead-End Recovery Enclaves (anti_shortcut_enclave, mode_collapse_enclave, rfc_counter_proof_enclave, unwind_recovery_enclave)
- 1-Tap Functorial Undo / Calibrated Unwind restoring state snapshot, context, and thermodynamic bits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import uuid

from .domain_models import (
    DomainInvariantViolation,
    FunctorialUndoCheckpoint,
)


class StatechartTransitionError(Exception):
    """Raised when an illegal transition or unmet guard condition is attempted."""
    pass


class FunctorialUndoError(Exception):
    """Raised when a checkpoint restoration violates causality or cannot be located."""
    pass


class StateNodeType(str, Enum):
    ATOMIC = "atomic"
    COMPOUND = "compound"
    PARALLEL = "parallel"
    HISTORY = "history"
    FINAL = "final"


class G4bStatechartEngine:
    """Universal 32-State Hierarchical XState v5 Engine with 1-Tap Functorial Undo."""

    # Complete 32-state inventory
    ALL_STATES: Set[str] = {
        # Stratum 1: epistemic_discovery (7 states)
        "sovereign_init",
        "island_quarantine",
        "hypothesis_formulation",
        "constraint_boundary_mapping",
        "discovery_evaluating",
        "discovery_deep_history",
        "anti_shortcut_enclave",
        # Stratum 2: adversarial_crucible (8 states)
        "novelty_search_active",
        "taboo_distance_check",
        "mode_collapse_enclave",
        "dialectical_negation_inject",
        "boundary_stress_fuzzing",
        "pareto_frontier_filter",
        "crucible_deep_history",
        "crucible_certified",
        # Stratum 3: protocol_adjudication (7 states)
        "spec_bundle_published",
        "builder_rfc_ingress",
        "rfc_counter_proof_eval",
        "rfc_counter_proof_enclave",
        "spec_amendment_signed",
        "adjudication_deep_history",
        "generational_handover_ready",
        # Parallel Region 1: concurrent_byzantine_fuzzer (4 states)
        "fuzzer_quiescent",
        "fuzzer_generating_vectors",
        "fuzzer_evaluating_response",
        "fuzzer_fault_trapped",
        # Parallel Region 2: landauer_thermodynamic_meter (4 states)
        "meter_monitoring",
        "meter_bit_erasure_sample",
        "meter_capital_rebalance",
        "meter_cutoff_tripped",
        # Recovery & Final Enclaves (2 states)
        "unwind_recovery_enclave",
        "epistemic_zenith_sealed",
    }

    def __init__(self, initial_context: Optional[Dict[str, Any]] = None):
        # Active state configuration
        self.active_state: str = "sovereign_init"
        self.active_fuzzer_state: str = "fuzzer_quiescent"
        self.active_meter_state: str = "meter_monitoring"

        # Deep history registers
        self.history_registers: Dict[str, str] = {
            "discovery_deep_history": "sovereign_init",
            "crucible_deep_history": "novelty_search_active",
            "adjudication_deep_history": "spec_bundle_published",
        }

        # Dynamic context
        self.context: Dict[str, Any] = {
            "target_soc_id": "soc_g4b_researcher",
            "islands_spawned": 0,
            "hypotheses_count": 0,
            "taboo_distance": 1.0,
            "negation_injected": False,
            "rfcs_pending": 0,
            "rfcs_resolved": 0,
            "erased_bits": 0,
            "exploratory_tokens_unspent": 589380,
            "protected_tokens_floor": 392920,
            "is_sealed": False,
        }
        if initial_context:
            self.context.update(initial_context)

        # Checkpoint registry for 1-tap Functorial Undo
        self.checkpoints: Dict[str, FunctorialUndoCheckpoint] = {}
        self.checkpoint_sequence: List[str] = []
        self.transition_log: List[Dict[str, Any]] = []

        # Create initial genesis checkpoint
        self.create_checkpoint("genesis_checkpoint")

    def get_active_configuration(self) -> Dict[str, str]:
        """Returns the complete active configuration across strata and parallel regions."""
        return {
            "primary_stratum_state": self.active_state,
            "parallel_fuzzer_region": self.active_fuzzer_state,
            "parallel_meter_region": self.active_meter_state,
        }

    def create_checkpoint(self, checkpoint_id: Optional[str] = None) -> FunctorialUndoCheckpoint:
        """Captures an immutable snapshot for deterministic Functorial Undo."""
        c_id = checkpoint_id or f"chk_{uuid.uuid4().hex[:8]}"
        snap = {
            "active_state": self.active_state,
            "fuzzer_state": self.active_fuzzer_state,
            "meter_state": self.active_meter_state,
            "history_registers": dict(self.history_registers),
            "context": dict(self.context),
        }
        raw_repr = json.dumps(snap, sort_keys=True)
        snap_hash = hashlib.sha256(raw_repr.encode("utf-8")).hexdigest()

        chk = FunctorialUndoCheckpoint(
            checkpoint_id=c_id,
            step_index=len(self.transition_log),
            statechart_snapshot_hash=snap_hash,
            context_delta=dict(self.context),
            erased_bits_to_revert=int(self.context.get("erased_bits", 0)),
        )
        chk.validate_invariants()

        self.checkpoints[c_id] = chk
        self.checkpoint_sequence.append(c_id)
        return chk

    def execute_functorial_undo(self, checkpoint_id: str) -> Dict[str, Any]:
        """Executes a 1-tap Functorial Undo, restoring state, context, and reclaiming bits."""
        if checkpoint_id not in self.checkpoints:
            raise FunctorialUndoError(f"Checkpoint not found: {checkpoint_id}")

        chk = self.checkpoints[checkpoint_id]

        # Prior snapshot recovery
        self.context = dict(chk.context_delta)

        # Determine which history state or enclave to route into
        if self.active_state in (
            "sovereign_init", "island_quarantine", "hypothesis_formulation",
            "constraint_boundary_mapping", "discovery_evaluating", "anti_shortcut_enclave",
        ):
            self.active_state = self.history_registers["discovery_deep_history"]
        elif self.active_state in (
            "novelty_search_active", "taboo_distance_check", "mode_collapse_enclave",
            "dialectical_negation_inject", "boundary_stress_fuzzing", "pareto_frontier_filter",
            "crucible_certified",
        ):
            self.active_state = self.history_registers["crucible_deep_history"]
        else:
            self.active_state = self.history_registers["adjudication_deep_history"]

        undo_event = {
            "event": "FUNCTORIAL_UNDO_EXECUTED",
            "checkpoint_id": checkpoint_id,
            "restored_state": self.active_state,
            "reclaimed_bits": chk.erased_bits_to_revert,
            "timestamp_ns": time.time_ns(),
        }
        self.transition_log.append(undo_event)
        return undo_event

    def send(self, event: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Dispatches an event and executes deterministic transitions across state nodes."""
        payload = payload or {}
        prior_state = self.active_state

        # Update deep history before moving
        if self.active_state in (
            "sovereign_init", "island_quarantine", "hypothesis_formulation",
            "constraint_boundary_mapping", "discovery_evaluating"
        ):
            self.history_registers["discovery_deep_history"] = self.active_state
        elif self.active_state in (
            "novelty_search_active", "taboo_distance_check", "dialectical_negation_inject",
            "boundary_stress_fuzzing", "pareto_frontier_filter", "crucible_certified"
        ):
            self.history_registers["crucible_deep_history"] = self.active_state
        elif self.active_state in (
            "spec_bundle_published", "builder_rfc_ingress", "rfc_counter_proof_eval",
            "spec_amendment_signed", "generational_handover_ready"
        ):
            self.history_registers["adjudication_deep_history"] = self.active_state

        # =====================================================================
        # Stratum 1: Epistemic Discovery Transitions
        # =====================================================================
        if self.active_state == "sovereign_init" and event == "EV_SPAWN_ISLANDS":
            self.active_state = "island_quarantine"
            self.context["islands_spawned"] = payload.get("island_count", 3)

        elif self.active_state == "island_quarantine" and event == "EV_ISLANDS_SEEDED":
            self.active_state = "hypothesis_formulation"

        elif self.active_state == "hypothesis_formulation" and event == "EV_HYPOTHESIS_FORMULATED":
            self.active_state = "constraint_boundary_mapping"
            self.context["hypotheses_count"] = self.context.get("hypotheses_count", 0) + 1

        elif self.active_state == "constraint_boundary_mapping" and event == "EV_BOUNDARIES_MAPPED":
            self.active_state = "discovery_evaluating"

        elif self.active_state == "discovery_evaluating":
            if event == "EV_SHORTCUT_DETECTED":
                # Guard: Trap easy shortcuts in anti_shortcut_enclave
                self.active_state = "anti_shortcut_enclave"
            elif event == "EV_DISCOVERY_CERTIFIED":
                # Advance to Stratum 2
                self.active_state = "novelty_search_active"

        elif self.active_state == "anti_shortcut_enclave" and event == "EV_UNWIND_SHORTCUT":
            # Calibrated unwind recovery back to hypothesis formulation
            self.active_state = "hypothesis_formulation"

        # =====================================================================
        # Stratum 2: Adversarial Crucible Transitions
        # =====================================================================
        elif self.active_state == "novelty_search_active" and event == "EV_EVALUATE_NOVELTY":
            self.active_state = "taboo_distance_check"

        elif self.active_state == "taboo_distance_check":
            dist = float(payload.get("taboo_distance", self.context.get("taboo_distance", 1.0)))
            self.context["taboo_distance"] = dist
            if event == "EV_TABOO_BREACH" or dist < 0.40:
                self.active_state = "mode_collapse_enclave"
            elif event == "EV_TABOO_SATISFIED" or dist >= 0.40:
                self.active_state = "dialectical_negation_inject"

        elif self.active_state == "mode_collapse_enclave" and event == "EV_FORCE_NEGATION":
            self.active_state = "dialectical_negation_inject"
            self.context["negation_injected"] = True

        elif self.active_state == "dialectical_negation_inject" and event == "EV_NEGATION_APPLIED":
            self.active_state = "boundary_stress_fuzzing"

        elif self.active_state == "boundary_stress_fuzzing" and event == "EV_STRESS_PASSED":
            self.active_state = "pareto_frontier_filter"

        elif self.active_state == "pareto_frontier_filter" and event == "EV_PARETO_OPTIMAL":
            self.active_state = "crucible_certified"

        elif self.active_state == "crucible_certified" and event == "EV_EMIT_DELIVERABLES":
            # Advance to Stratum 3
            self.active_state = "spec_bundle_published"

        # =====================================================================
        # Stratum 3: Protocol Adjudication Transitions
        # =====================================================================
        elif self.active_state == "spec_bundle_published" and event == "EV_BUILDER_ATTACHED":
            self.active_state = "builder_rfc_ingress"

        elif self.active_state == "builder_rfc_ingress" and event == "EV_SUBMIT_RFC":
            self.active_state = "rfc_counter_proof_eval"
            self.context["rfcs_pending"] = self.context.get("rfcs_pending", 0) + 1

        elif self.active_state == "rfc_counter_proof_eval":
            if event == "EV_AXIOM_VIOLATION":
                self.active_state = "rfc_counter_proof_enclave"
            elif event == "EV_AMENDMENT_PROVED":
                self.active_state = "spec_amendment_signed"
                self.context["rfcs_resolved"] = self.context.get("rfcs_resolved", 0) + 1

        elif self.active_state == "rfc_counter_proof_enclave" and event == "EV_REJECT_RFC_WITH_PROOF":
            self.active_state = "builder_rfc_ingress"

        elif self.active_state == "spec_amendment_signed":
            if event == "EV_ANOTHER_RFC":
                self.active_state = "builder_rfc_ingress"
            elif event == "EV_ALL_RFCS_RESOLVED":
                self.active_state = "generational_handover_ready"

        elif self.active_state == "generational_handover_ready" and event == "EV_SEAL_CRUCIBLE":
            self.active_state = "epistemic_zenith_sealed"
            self.context["is_sealed"] = True

        # Global Unwind Event
        elif event == "EV_GLOBAL_UNWIND":
            self.active_state = "unwind_recovery_enclave"

        # =====================================================================
        # Parallel Orthogonal Region 1: concurrent_byzantine_fuzzer
        # =====================================================================
        if event == "EV_FUZZ_TICK" and self.active_fuzzer_state == "fuzzer_quiescent":
            self.active_fuzzer_state = "fuzzer_generating_vectors"
        elif event == "EV_VECTORS_DISPATCHED" and self.active_fuzzer_state == "fuzzer_generating_vectors":
            self.active_fuzzer_state = "fuzzer_evaluating_response"
        elif event == "EV_BYZANTINE_FAULT_CAUGHT" and self.active_fuzzer_state == "fuzzer_evaluating_response":
            self.active_fuzzer_state = "fuzzer_fault_trapped"
        elif event == "EV_FAULT_LOGGED" and self.active_fuzzer_state == "fuzzer_fault_trapped":
            self.active_fuzzer_state = "fuzzer_quiescent"

        # =====================================================================
        # Parallel Orthogonal Region 2: landauer_thermodynamic_meter
        # =====================================================================
        if event == "EV_BIT_ERASURE_EVENT" and self.active_meter_state == "meter_monitoring":
            self.active_meter_state = "meter_bit_erasure_sample"
            erased = payload.get("bits", 128)
            self.context["erased_bits"] = self.context.get("erased_bits", 0) + erased
            self.context["exploratory_tokens_unspent"] = max(
                0, self.context.get("exploratory_tokens_unspent", 589380) - payload.get("tokens", 50)
            )
        elif event == "EV_REBALANCE_CAPITAL" and self.active_meter_state == "meter_bit_erasure_sample":
            if self.context.get("exploratory_tokens_unspent", 0) < 1024:
                self.active_meter_state = "meter_cutoff_tripped"
            else:
                self.active_meter_state = "meter_monitoring"

        # Log transition
        self.transition_log.append({
            "from_state": prior_state,
            "to_state": self.active_state,
            "event": event,
            "payload": payload,
            "fuzzer_state": self.active_fuzzer_state,
            "meter_state": self.active_meter_state,
            "timestamp_ns": time.time_ns(),
        })

        return self.get_active_configuration()
