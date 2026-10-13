"""Axioma Sentinel Core State Engine.

Integrates:
- [L1-G2-001] Functorial Reversibility & Checkpoint State Restoration
- [L1-G2-002] 3-Pass Enclave Auto-Healing Integration
- [L1-G2-003] Cognitive Ergonomics & 1-Click Rollback Affordance
- [L1-G2-004] Zero-Trust Capability Scoping Integration
- [L1-008] Landauer Thermodynamic Bit-Erasure Dissipation Accounting
"""

from typing import Any, Callable, Dict, List, Optional
import copy
import hashlib
import json
import time
import uuid

from .enclave import SentinelEnclaveSupervisor
from .tokens import SentinelCapabilityAuthority
from .types import (
    ActionStatus,
    AgentToolAction,
    CheckpointSnapshot,
    EnclaveIncident,
    SentinelSystemState,
)


class SentinelCoreEngine:
    """The central reactive controller and state machine for Axioma Sentinel."""

    def __init__(self):
        self.capability_authority = SentinelCapabilityAuthority()
        self.enclave_supervisor = SentinelEnclaveSupervisor(max_passes=3)

        # State storage
        self._workspace_state: Dict[str, Any] = {
            "system_status": "OPERATIONAL",
            "active_agent_count": 3,
            "monitored_nodes": ["local-edge-01", "worker-swarm-02", "orchestrator-alpha"],
            "security_tier": "ZERO_TRUST_ENCLAVE",
            "deployed_pipelines": 7,
        }

        # Checkpoint history for functorial 1-click rollback
        self._checkpoint_history: List[CheckpointSnapshot] = []
        self._action_timeline: List[AgentToolAction] = []
        self._last_rollback_timestamp: Optional[float] = None

        # Thermodynamic Landauer dissipation ledger
        self._total_erased_bits: int = 0
        self._kb_t_ln2 = 2.87e-21  # Joules per bit erasure at 300 Kelvin

        # Create initial baseline checkpoint
        self._create_checkpoint(action_id="baseline_init")

    def _hash_state(self, state: Dict[str, Any]) -> str:
        """Computes deterministic SHA-256 hash of state dictionary."""
        serialized = json.dumps(state, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _create_checkpoint(self, action_id: str) -> CheckpointSnapshot:
        """Preserves functorial state checkpoint for reversible rollbacks."""
        state_copy = copy.deepcopy(self._workspace_state)
        shash = self._hash_state(state_copy)
        checkpoint = CheckpointSnapshot(
            checkpoint_id=f"chk_{uuid.uuid4().hex[:8]}",
            action_id=action_id,
            state_payload=state_copy,
            state_hash=shash,
            timestamp=time.time(),
        )
        self._checkpoint_history.append(checkpoint)
        # Cap checkpoint history at 50
        if len(self._checkpoint_history) > 50:
            self._checkpoint_history.pop(0)
        return checkpoint

    def dispatch_agent_action(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        token_id: Optional[str],
        simulate_fault: bool = False,
    ) -> AgentToolAction:
        """Dispatches an agent tool action through capability verification and enclave auto-healing."""
        action_id = f"act_{uuid.uuid4().hex[:8]}"
        now = time.time()

        # 1. Zero-Trust Capability Scoping Verification [L1-G2-004]
        token = self.capability_authority.verify_action(token_id=token_id, requested_action=tool_name)

        # 2. Pre-execution Checkpoint for Functorial Reversibility [L1-G2-001]
        self._create_checkpoint(action_id=action_id)

        # 3. Define tool execution logic
        def tool_logic(s_box: Dict[str, Any]) -> Dict[str, Any]:
            p = s_box.get("parameters", {})
            # If simulated fault is requested, breach on first try unless recovered
            if simulate_fault and not s_box.get("forced_recovery_mode") and not s_box.get("fallback_to_safe_mode"):
                if not isinstance(p.get("count"), int):
                    raise ValueError(
                        f"Schema Invariant Infraction: Expected int for parameter 'count', got {type(p.get('count')).__name__}"
                    )
            # Normal state mutation
            mutation_key = p.get("target_key", f"metric_{tool_name}")
            mutation_value = p.get("target_value", p.get("count", 1))
            return {
                "status": "SUCCESS",
                "modified_key": mutation_key,
                "modified_value": mutation_value,
                "timestamp": time.time(),
            }

        def invariant_checker(res: Any, s_box: Dict[str, Any]) -> tuple[bool, List[str]]:
            if isinstance(res, dict) and res.get("status") == "SUCCESS":
                return True, []
            return False, ["Execution result failed state validity invariant."]

        # 4. Execute inside Ephemeral Healing Enclave [L1-G2-002]
        exec_res, incident = self.enclave_supervisor.execute_with_auto_healing(
            tool_name=tool_name,
            operation=tool_logic,
            context=self._workspace_state,
            parameters=parameters,
            invariant_checker=invariant_checker,
        )

        # 5. Landauer Thermodynamic Dissipation Accounting [L1-008]
        # Bit erasures occur when overwriting state keys
        erased_bits = len(parameters) * 8 + (32 if incident else 8)
        dissipated_joules = erased_bits * self._kb_t_ln2
        self._total_erased_bits += erased_bits

        # 6. Apply state mutation if successful
        status = ActionStatus.EXECUTED
        remediation_notes = []

        if incident:
            if incident.healed:
                status = ActionStatus.HEALED
                remediation_notes = incident.remediation_steps
                if exec_res and isinstance(exec_res, dict):
                    self._workspace_state[exec_res.get("modified_key", "last_update")] = exec_res.get("modified_value")
            else:
                status = ActionStatus.QUARANTINED
                remediation_notes = ["Auto-repair passes exhausted; action quarantined in enclave."]
        else:
            if exec_res and isinstance(exec_res, dict):
                self._workspace_state[exec_res.get("modified_key", "last_update")] = exec_res.get("modified_value")

        witness_hash = hashlib.sha256(
            f"{action_id}:{tool_name}:{token.token_id}:{now}:{status.value}".encode("utf-8")
        ).hexdigest()

        action = AgentToolAction(
            action_id=action_id,
            tool_name=tool_name,
            persona=token.persona,
            parameters=parameters,
            capability_token_id=token.token_id,
            timestamp=now,
            status=status,
            result=exec_res,
            erased_bits=erased_bits,
            dissipated_joules=dissipated_joules,
            witness_hash=witness_hash,
            remediation_notes=remediation_notes,
        )
        self._action_timeline.insert(0, action)
        return action

    def rollback_to_last_checkpoint(self) -> Dict[str, Any]:
        """Functorial 1-Click State Rollback [L1-G2-001 & L1-G2-003].
        
        Reverts the workspace state to the state immediately preceding the latest action.
        """
        if len(self._checkpoint_history) < 2:
            return {"success": False, "message": "No earlier checkpoint available to restore."}

        # Pop current state snapshot and restore the previous one
        current_chk = self._checkpoint_history.pop()
        previous_chk = self._checkpoint_history[-1]

        # Reversibility restoration
        self._workspace_state = copy.deepcopy(previous_chk.state_payload)
        self._last_rollback_timestamp = time.time()

        # Mark latest timeline action as reverted
        if self._action_timeline:
            self._action_timeline[0].status = ActionStatus.REVERTED
            self._action_timeline[0].remediation_notes.append("State reverted via Functorial 1-Click Rollback.")

        return {
            "success": True,
            "restored_checkpoint_id": previous_chk.checkpoint_id,
            "state_hash": previous_chk.state_hash,
            "restored_state": copy.deepcopy(self._workspace_state),
        }

    def get_system_summary(self) -> Dict[str, Any]:
        """Emits comprehensive reactive system state for the UI dashboard."""
        tokens_summary = self.capability_authority.export_tokens_summary()
        incidents = self.enclave_supervisor.get_incidents_history()

        healed_count = sum(1 for i in incidents if i.healed)
        quarantined_count = sum(1 for i in incidents if not i.healed)

        return {
            "workspace_state": copy.deepcopy(self._workspace_state),
            "state_hash": self._hash_state(self._workspace_state),
            "total_actions": len(self._action_timeline),
            "healed_incidents": healed_count,
            "quarantined_incidents": quarantined_count,
            "total_erased_bits": self._total_erased_bits,
            "total_dissipated_joules": self._total_erased_bits * self._kb_t_ln2,
            "last_rollback_timestamp": self._last_rollback_timestamp,
            "tokens": tokens_summary,
            "timeline": [
                {
                    "action_id": a.action_id,
                    "tool_name": a.tool_name,
                    "persona": a.persona,
                    "status": a.status.value,
                    "parameters": a.parameters,
                    "timestamp": a.timestamp,
                    "erased_bits": a.erased_bits,
                    "witness_hash": a.witness_hash[:16] + "...",
                    "remediation_notes": a.remediation_notes,
                }
                for a in self._action_timeline[:25]
            ],
            "incidents": [
                {
                    "incident_id": inc.incident_id,
                    "tool_name": inc.tool_name,
                    "severity": inc.severity.value,
                    "initial_error": inc.initial_error,
                    "passes_attempted": inc.passes_attempted,
                    "healed": inc.healed,
                    "blast_leakage": inc.blast_leakage_detected,
                    "steps": inc.remediation_steps,
                    "timestamp": inc.timestamp,
                }
                for inc in incidents[:10]
            ],
        }
