"""Types and data models for Axioma Sentinel (System 07).

Embodying Generation 2 structural invariants:
- [L1-G2-001] Functorial Reversibility & Multi-Substrate Projection
- [L1-G2-002] Ephemeral Exception Enclaves with 3-Pass Auto-Healing
- [L1-G2-003] Cognitive Ergonomics & Persona Goal Velocity
- [L1-G2-004] Introspectable Capability Tokens with Cryptographic Witnesses
- [L1-G2-005] Human Intent Elicitation Alignment
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time


class ActionStatus(str, Enum):
    """Execution status of an agent tool action."""
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    HEALED = "HEALED"
    QUARANTINED = "QUARANTINED"
    REVERTED = "REVERTED"


class IncidentSeverity(str, Enum):
    """Severity rating of an invariant breach."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class AgentToolAction:
    """Represents a capability-scoped tool action dispatched by an autonomous agent."""
    action_id: str
    tool_name: str
    persona: str
    parameters: Dict[str, Any]
    capability_token_id: str
    timestamp: float
    status: ActionStatus = ActionStatus.PENDING
    result: Any = None
    erased_bits: int = 0
    dissipated_joules: float = 0.0
    witness_hash: str = ""
    remediation_notes: List[str] = field(default_factory=list)


@dataclass
class EnclaveIncident:
    """Isolated exception enclave event tracking multi-pass healing."""
    incident_id: str
    action_id: str
    tool_name: str
    severity: IncidentSeverity
    initial_error: str
    passes_attempted: int
    max_passes: int
    healed: bool
    blast_leakage_detected: bool
    remediation_steps: List[str]
    timestamp: float
    quarantine_state: Optional[Dict[str, Any]] = None


@dataclass
class CheckpointSnapshot:
    """Functorial state checkpoint allowing exact 1-click rollback."""
    checkpoint_id: str
    action_id: str
    state_payload: Dict[str, Any]
    state_hash: str
    timestamp: float
    restorable: bool = True


@dataclass
class SentinelSystemState:
    """Global reactive system state for Axioma Sentinel."""
    active_tokens: int
    total_actions_dispatched: int
    healed_incidents: int
    quarantined_incidents: int
    total_erased_bits: int
    total_dissipated_joules: float
    current_state_hash: str
    last_rollback_timestamp: Optional[float] = None
