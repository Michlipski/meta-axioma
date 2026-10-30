"""Generation 4b Hierarchical XState v5 Statechart Engine (`soc_g4b_builder`).

Enforces:
- [L1-002] Statechart Determinism & Functorial Undo Invariant.
- [L1-G3B-011] Universal & Hierarchical Statechart IR.
- [BLUEPRINT-G4B-CAUSAL-OPT3] 36-State Reactive Causal Architecture across:
  - 4 Compound Strata:
    1. service_handshake (5 states: sovereign_init, handshake_awaiting_bundle, bundle_validated,
       handshake_rejected_enclave, handshake_deep_history)
    2. fractal_tree_orchestration (6 states: tree_root_spawned, subagent_branching_active,
       budget_lease_evaluating, branch_healing_enclave, tree_converged, orchestration_deep_history)
    3. hermetic_ast_synthesis (12 states: ast_skeleton_extracting, builders_synthesizing,
       substrate_emitted_gate, surgical_patch_evaluating, hermetic_linter_auditing,
       reactive_audit_evaluating, byzantine_chaos_injecting, linter_violation_enclave,
       all_leaves_converged_gate, hypergraph_indexing, ast_synthesis_certified, synthesis_deep_history)
    4. quine_certification (7 states: quine_sandbox_provisioning, daughter_compiler_emitting,
       daughter_reactive_dag_verified, daughter_self_hosting_test, daughter_crucible_certified,
       quine_deep_history, quine_zenith_sealed)
  - 2 Parallel Orthogonal Regions:
    1. concurrent_tree_linter (3 states: tree_linter_idle, tree_linter_analyzing_ast, tree_linter_alert)
    2. landauer_dissipation_meter (3 states: meter_monitoring, meter_bit_erasure_sample, meter_cutoff_tripped_enclave)
  - 4 Deep History States (handshake_deep_history, orchestration_deep_history, synthesis_deep_history, quine_deep_history)
  - 4 Recovery Enclaves (handshake_rejected_enclave, branch_healing_enclave, linter_violation_enclave, meter_cutoff_tripped_enclave)
- 1-Tap Functorial Undo integration for deterministic unwinding.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .functorial_undo import FunctorialUndoManager


class StatechartTransitionError(Exception):
    """Raised when an illegal transition or unmet guard condition is attempted."""
    pass


class StateNodeType(str, Enum):
    ATOMIC = "atomic"
    COMPOUND = "compound"
    PARALLEL = "parallel"
    HISTORY = "history"
    FINAL = "final"


class G4bBuilderStatechartEngine:
    """Universal 36-State Hierarchical XState v5 Engine for Sovereign Builder."""

    ALL_STATES: Set[str] = {
        # Stratum 1: service_handshake (5 states)
        "sovereign_init",
        "handshake_awaiting_bundle",
        "bundle_validated",
        "handshake_rejected_enclave",
        "handshake_deep_history",
        # Stratum 2: fractal_tree_orchestration (6 states)
        "tree_root_spawned",
        "subagent_branching_active",
        "budget_lease_evaluating",
        "branch_healing_enclave",
        "tree_converged",
        "orchestration_deep_history",
        # Stratum 3: hermetic_ast_synthesis (12 states)
        "ast_skeleton_extracting",
        "builders_synthesizing",
        "substrate_emitted_gate",
        "surgical_patch_evaluating",
        "hermetic_linter_auditing",
        "reactive_audit_evaluating",
        "byzantine_chaos_injecting",
        "linter_violation_enclave",
        "all_leaves_converged_gate",
        "hypergraph_indexing",
        "ast_synthesis_certified",
        "synthesis_deep_history",
        # Stratum 4: quine_certification (7 states)
        "quine_sandbox_provisioning",
        "daughter_compiler_emitting",
        "daughter_reactive_dag_verified",
        "daughter_self_hosting_test",
        "daughter_crucible_certified",
        "quine_deep_history",
        "quine_zenith_sealed",
        # Parallel Region 1: concurrent_tree_linter (3 states)
        "tree_linter_idle",
        "tree_linter_analyzing_ast",
        "tree_linter_alert",
        # Parallel Region 2: landauer_dissipation_meter (3 states)
        "meter_monitoring",
        "meter_bit_erasure_sample",
        "meter_cutoff_tripped_enclave",
    }

    TRANSITIONS: Dict[Tuple[str, str], str] = {
        # Stratum 1: service_handshake
        ("sovereign_init", "EV_AWAIT_BUNDLE"): "handshake_awaiting_bundle",
        ("handshake_awaiting_bundle", "EV_BUNDLE_VALID"): "bundle_validated",
        ("handshake_awaiting_bundle", "EV_BUNDLE_REJECTED"): "handshake_rejected_enclave",
        ("handshake_rejected_enclave", "EV_RETRY_HANDSHAKE"): "handshake_awaiting_bundle",

        # Stratum 2: fractal_tree_orchestration
        ("bundle_validated", "EV_START_ORCHESTRATION"): "tree_root_spawned",
        ("tree_root_spawned", "EV_BRANCH_SPAWN"): "subagent_branching_active",
        ("subagent_branching_active", "EV_EVAL_BUDGET"): "budget_lease_evaluating",
        ("subagent_branching_active", "EV_BRANCH_FAILED"): "branch_healing_enclave",
        ("budget_lease_evaluating", "EV_BUDGET_OK"): "tree_converged",
        ("budget_lease_evaluating", "EV_BUDGET_EXHAUSTED"): "branch_healing_enclave",
        ("branch_healing_enclave", "EV_HEALING_RESOLVED"): "subagent_branching_active",

        # Stratum 3: hermetic_ast_synthesis (12 states)
        ("tree_converged", "EV_START_SYNTHESIS"): "ast_skeleton_extracting",
        ("ast_skeleton_extracting", "EV_DISPATCH_BUILDERS"): "builders_synthesizing",
        ("ast_skeleton_extracting", "EV_PATCH_EVAL"): "surgical_patch_evaluating",
        ("builders_synthesizing", "EV_SUBSTRATE_EMITTED"): "substrate_emitted_gate",
        ("builders_synthesizing", "EV_BRANCH_FAILED"): "linter_violation_enclave",
        ("substrate_emitted_gate", "EV_SUBSTRATE_VERIFIED"): "surgical_patch_evaluating",
        ("substrate_emitted_gate", "EV_SUBSTRATE_FAILED"): "linter_violation_enclave",
        ("surgical_patch_evaluating", "EV_AUDIT_HERMETIC"): "hermetic_linter_auditing",
        ("hermetic_linter_auditing", "EV_LINTER_PASSED"): "reactive_audit_evaluating",
        ("hermetic_linter_auditing", "EV_LINTER_VIOLATION"): "linter_violation_enclave",
        ("linter_violation_enclave", "EV_PATCH_APPLIED"): "hermetic_linter_auditing",
        ("reactive_audit_evaluating", "EV_REACTIVE_AUDIT_OK"): "byzantine_chaos_injecting",
        ("reactive_audit_evaluating", "EV_LINTER_VIOLATION"): "linter_violation_enclave",
        ("byzantine_chaos_injecting", "EV_CHAOS_TESTS_PASSED"): "all_leaves_converged_gate",
        ("byzantine_chaos_injecting", "EV_BRANCH_FAILED"): "linter_violation_enclave",
        ("byzantine_chaos_injecting", "EV_LINTER_VIOLATION"): "linter_violation_enclave",
        ("all_leaves_converged_gate", "EV_ALL_LEAVES_CONVERGED"): "hypergraph_indexing",
        ("all_leaves_converged_gate", "EV_MORE_LEAVES_PENDING"): "builders_synthesizing",
        ("hypergraph_indexing", "EV_INDEXING_COMPLETE"): "ast_synthesis_certified",

        # Stratum 4: quine_certification (7 states)
        ("ast_synthesis_certified", "EV_START_QUINE_CRUCIBLE"): "quine_sandbox_provisioning",
        ("quine_sandbox_provisioning", "EV_SANDBOX_READY"): "daughter_compiler_emitting",
        ("daughter_compiler_emitting", "EV_DAUGHTER_EMITTED"): "daughter_reactive_dag_verified",
        ("daughter_reactive_dag_verified", "EV_REACTIVE_DAG_VERIFIED"): "daughter_self_hosting_test",
        ("daughter_reactive_dag_verified", "EV_SELF_HOSTING_VERIFIED"): "daughter_crucible_certified",
        ("daughter_self_hosting_test", "EV_SELF_HOSTING_VERIFIED"): "daughter_crucible_certified",
        ("daughter_self_hosting_test", "EV_CRUCIBLE_CERTIFIED"): "quine_zenith_sealed",
        ("daughter_crucible_certified", "EV_CRUCIBLE_CERTIFIED"): "quine_zenith_sealed",
        ("daughter_crucible_certified", "EV_SEAL_ZENITH"): "quine_zenith_sealed",
    }

    def __init__(self, undo_manager: Optional[FunctorialUndoManager] = None):
        self.undo_mgr = undo_manager or FunctorialUndoManager()

        # Active state configuration
        self.active_main_state: str = "sovereign_init"
        self.active_linter_state: str = "tree_linter_idle"
        self.active_meter_state: str = "meter_monitoring"

        # Deep history registers (4 deep history registers)
        self.history_registers: Dict[str, str] = {
            "handshake_deep_history": "sovereign_init",
            "orchestration_deep_history": "tree_root_spawned",
            "synthesis_deep_history": "ast_skeleton_extracting",
            "quine_deep_history": "quine_sandbox_provisioning",
        }

        # Context
        self.context: Dict[str, Any] = {
            "bundle_id": None,
            "root_node_id": None,
            "tokens_spent": 0,
            "erased_bits": 0,
            "last_error": None,
        }

        # Transition log
        self.transition_log: List[Dict[str, Any]] = []

        # Create initial genesis checkpoint
        self._record_checkpoint("GENESIS_INIT")

    def get_active_configuration(self) -> Tuple[str, str, str]:
        """Returns the current orthogonal state configuration tuple."""
        return (self.active_main_state, self.active_linter_state, self.active_meter_state)

    def _record_checkpoint(self, event_label: str) -> None:
        """Pushes state configuration and context to FunctorialUndoManager."""
        self.undo_mgr.create_checkpoint(
            state_label=f"{event_label} -> {self.active_main_state}",
            state_context={
                "main_state": self.active_main_state,
                "linter_state": self.active_linter_state,
                "meter_state": self.active_meter_state,
                "context": dict(self.context),
                "history_registers": dict(self.history_registers),
            },
            erased_bits=self.context.get("erased_bits", 0),
            active_node_id=str(self.context.get("root_node_id", "")),
        )

    def send(self, event: str, payload: Optional[Dict[str, Any]] = None) -> Tuple[str, str, str]:
        """Processes an event, executes state transitions, and records undo checkpoints."""
        payload = payload or {}
        prev_config = self.get_active_configuration()

        # Update context
        for k, v in payload.items():
            self.context[k] = v

        # Process Main State transitions
        self._dispatch_main_event(event, payload)

        # Process Parallel Region 1 (Tree Linter)
        self._dispatch_linter_event(event, payload)

        # Process Parallel Region 2 (Landauer Meter)
        self._dispatch_meter_event(event, payload)

        # Update deep history registers across all 4 compound strata
        if self.active_main_state in (
            "sovereign_init", "handshake_awaiting_bundle", "bundle_validated", "handshake_rejected_enclave"
        ):
            self.history_registers["handshake_deep_history"] = self.active_main_state
        elif self.active_main_state in (
            "tree_root_spawned", "subagent_branching_active", "budget_lease_evaluating",
            "branch_healing_enclave", "tree_converged"
        ):
            self.history_registers["orchestration_deep_history"] = self.active_main_state
        elif self.active_main_state in (
            "ast_skeleton_extracting", "builders_synthesizing", "substrate_emitted_gate",
            "surgical_patch_evaluating", "hermetic_linter_auditing", "reactive_audit_evaluating",
            "byzantine_chaos_injecting", "linter_violation_enclave", "all_leaves_converged_gate",
            "hypergraph_indexing", "ast_synthesis_certified"
        ):
            self.history_registers["synthesis_deep_history"] = self.active_main_state
        elif self.active_main_state in (
            "quine_sandbox_provisioning", "daughter_compiler_emitting", "daughter_reactive_dag_verified",
            "daughter_self_hosting_test", "daughter_crucible_certified", "quine_zenith_sealed"
        ):
            self.history_registers["quine_deep_history"] = self.active_main_state

        new_config = self.get_active_configuration()
        self.transition_log.append({
            "event": event,
            "prev": prev_config,
            "curr": new_config,
            "timestamp": time.time(),
        })

        # Record Functorial Undo Checkpoint
        self._record_checkpoint(event)

        return new_config

    def _dispatch_main_event(self, event: str, payload: Dict[str, Any]) -> None:
        curr = self.active_main_state

        # Deep History Restorations
        if event == "EV_RESTORE_HANDSHAKE_HISTORY":
            self.active_main_state = self.history_registers["handshake_deep_history"]
            return
        if event == "EV_RESTORE_ORCHESTRATION_HISTORY":
            self.active_main_state = self.history_registers["orchestration_deep_history"]
            return
        if event == "EV_RESTORE_SYNTHESIS_HISTORY":
            self.active_main_state = self.history_registers["synthesis_deep_history"]
            return
        if event == "EV_RESTORE_QUINE_HISTORY":
            self.active_main_state = self.history_registers["quine_deep_history"]
            return

        if (curr, event) in self.TRANSITIONS:
            self.active_main_state = self.TRANSITIONS[(curr, event)]

    def _dispatch_linter_event(self, event: str, payload: Dict[str, Any]) -> None:
        curr = self.active_linter_state
        if curr == "tree_linter_idle":
            if event in ("EV_START_SYNTHESIS", "EV_AUDIT_HERMETIC", "EV_LINTER_SCAN", "EV_DISPATCH_BUILDERS"):
                self.active_linter_state = "tree_linter_analyzing_ast"
        elif curr == "tree_linter_analyzing_ast":
            if event == "EV_LINTER_VIOLATION":
                self.active_linter_state = "tree_linter_alert"
            elif event in ("EV_LINTER_PASSED", "EV_INDEXING_COMPLETE", "EV_ALL_LEAVES_CONVERGED", "EV_REACTIVE_AUDIT_OK"):
                self.active_linter_state = "tree_linter_idle"
        elif curr == "tree_linter_alert":
            if event in ("EV_PATCH_APPLIED", "EV_HEALING_RESOLVED"):
                self.active_linter_state = "tree_linter_analyzing_ast"

    def _dispatch_meter_event(self, event: str, payload: Dict[str, Any]) -> None:
        curr = self.active_meter_state
        if curr == "meter_monitoring":
            if event in ("EV_RECORD_BIT_ERASURE", "EV_PATCH_EVAL", "EV_SUBSTRATE_EMITTED"):
                self.active_meter_state = "meter_bit_erasure_sample"
            elif event in ("EV_BUDGET_EXHAUSTED", "EV_CUTOFF_TRIPPED"):
                self.active_meter_state = "meter_cutoff_tripped_enclave"
        elif curr == "meter_bit_erasure_sample":
            if event == "EV_CUTOFF_TRIPPED":
                self.active_meter_state = "meter_cutoff_tripped_enclave"
            else:
                self.active_meter_state = "meter_monitoring"
        elif curr == "meter_cutoff_tripped_enclave":
            if event == "EV_RESTORE_BUDGET":
                self.active_meter_state = "meter_monitoring"

    def undo_step(self) -> Tuple[str, str, str]:
        """Performs 1-tap Functorial Undo, restoring the immediate prior state configuration."""
        if not self.undo_mgr.can_undo():
            raise StatechartTransitionError("Cannot undo: at genesis checkpoint.")

        restored_chk, bit_diff = self.undo_mgr.undo()
        ctx = restored_chk.state_context
        self.active_main_state = ctx["main_state"]
        self.active_linter_state = ctx["linter_state"]
        self.active_meter_state = ctx["meter_state"]
        self.context = dict(ctx["context"])
        self.history_registers = dict(ctx["history_registers"])

        return self.get_active_configuration()
