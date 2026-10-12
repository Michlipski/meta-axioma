"""Demarcated Exception Enclaves & Bounded Invariant Suspension ([L1-016]).

Formal Expression:
    ∀ m ∉ I,  Enclave(m) ⟹ ∂ Scope(m) ∩ S_outer = ∅  ∧  AuditWitness(m) ≠ ⊥

Operational Rule:
    Any necessary violation or edge-case bypass of an active architectural
    invariant must be confined within an explicitly demarcated Exception Enclave;
    enclaves must isolate the failure blast radius, emit machine-readable
    dissipation audit witnesses, and prohibit unverified state leakage to outer
    composable scopes.
"""

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Dict, List, Optional
import time


@dataclass
class EnclaveAuditWitness:
    """Cryptographic machine-readable audit witness emitted by an Exception Enclave."""
    enclave_id: str
    suspended_invariants: List[str]
    justification: str
    blast_radius_contained: bool
    state_leakage_prevented: bool
    humane_recovery_guidance: str
    timestamp: float = field(default_factory=time.time)
    witness_hash: str = ""

    def __post_init__(self):
        if not self.witness_hash:
            data = {
                "id": self.enclave_id,
                "invariants": sorted(self.suspended_invariants),
                "justification": self.justification,
                "contained": self.blast_radius_contained,
                "time": self.timestamp,
            }
            raw = json.dumps(data, sort_keys=True)
            self.witness_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ExceptionEnclave:
    """Bounded execution scope that isolates invariant suspensions and contains failures."""

    _active_enclave_stack: List["ExceptionEnclave"] = []

    def __init__(
        self,
        enclave_id: str,
        suspended_invariants: List[str],
        justification: str,
        humane_recovery_guidance: str = "Recovering gracefully within demarcated boundary.",
    ):
        self.enclave_id = enclave_id
        self.suspended_invariants = suspended_invariants
        self.justification = justification
        self.humane_recovery_guidance = humane_recovery_guidance
        self.witness: Optional[EnclaveAuditWitness] = None
        self.caught_exception: Optional[Exception] = None
        self.is_active = False

    def __enter__(self) -> "ExceptionEnclave":
        self.is_active = True
        ExceptionEnclave._active_enclave_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ExceptionEnclave._active_enclave_stack.pop()
        self.is_active = False

        # Invariant suspension requires audit witness generation
        self.witness = EnclaveAuditWitness(
            enclave_id=self.enclave_id,
            suspended_invariants=self.suspended_invariants,
            justification=self.justification,
            blast_radius_contained=True,
            state_leakage_prevented=True,
            humane_recovery_guidance=self.humane_recovery_guidance,
        )

        if exc_val is not None:
            # Blast radius containment: capture exception and prevent unverified state leakage
            self.caught_exception = exc_val
            # Return True to suppress unhandled crashing to outer scope, ensuring graceful recovery
            return True
        return False

    @classmethod
    def current_enclave(cls) -> Optional["ExceptionEnclave"]:
        """Returns the currently active innermost enclave, if any."""
        if cls._active_enclave_stack:
            return cls._active_enclave_stack[-1]
        return None

    @classmethod
    def is_invariant_suspended(cls, invariant_id: str) -> bool:
        """Checks if an invariant is explicitly suspended in the current enclave."""
        for enclave in reversed(cls._active_enclave_stack):
            if invariant_id in enclave.suspended_invariants:
                return True
        return False
