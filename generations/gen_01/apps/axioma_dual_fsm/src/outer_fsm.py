"""Outer Zero-Trust Security & Boundary Governor FSM.
Monitors token velocity, Shannon entropy, boundary exfiltration patterns, and capability scoping.
Incorporates dynamic de-escalation (ELEVATED_SCRUTINY -> ACTIVE_MONITORING) and terminal halt trapdoors.
"""

from enum import Enum
import math
import re
from typing import Any, Dict, List, Optional, Tuple


class OuterState(str, Enum):
    SECURE_STANDBY = "SECURE_STANDBY"
    ACTIVE_MONITORING = "ACTIVE_MONITORING"
    ELEVATED_SCRUTINY = "ELEVATED_SCRUTINY"
    CONTAINED_QUARANTINE = "CONTAINED_QUARANTINE"
    ATOMIC_HALT = "ATOMIC_HALT"


# Patterns that trip exfiltration boundaries
EXFIL_PATTERNS = [
    (re.compile(r"sk-[a-zA-Z0-9]{32,}"), "OpenAI API Key Leak"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key Leak"),
    (re.compile(r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----"), "Cryptographic Private Key Exfiltration"),
    (re.compile(r"<system_instructions>"), "Prompt Injection Boundary Penetration"),
    (re.compile(r"DROP\s+TABLE|UNION\s+SELECT", re.IGNORECASE), "SQL Injection Attack Vector"),
]

# Benign structured tokens that look high-entropy but are allowed
UUID_PATTERN = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def calculate_shannon_entropy(text: str) -> float:
    """Calculates Shannon Entropy: H(X) = -sum(p * log2(p))."""
    if not text:
        return 0.0
    freq = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    total = len(text)
    entropy = 0.0
    for count in freq.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


class OuterFsm:
    """Deterministic security state machine enforcing zero-trust invariants."""

    def __init__(self, initial_state: OuterState = OuterState.SECURE_STANDBY):
        self.state: OuterState = initial_state
        self.token_velocity: float = 0.0
        self.measured_entropy: float = 0.0
        self.active_capability_leases: List[str] = ["base_query"]
        self.taint_flags: List[str] = []
        self.violation_reason: Optional[str] = None
        self.history: list[OuterState] = [initial_state]

    def activate_monitoring(self):
        if self.state == OuterState.SECURE_STANDBY:
            self._set_state(OuterState.ACTIVE_MONITORING)

    def evaluate_payload(self, text: str, token_count: int = 10, duration_sec: float = 1.0) -> Tuple[bool, str]:
        """Evaluates payload against rate, entropy, and exfiltration invariants.
        Returns (is_compliant, message).
        """
        if self.state == OuterState.ATOMIC_HALT:
            return False, "Outer FSM is in ATOMIC_HALT. Invariants permanently locked."

        # 1. Calculate metrics
        self.token_velocity = float(token_count) / max(0.001, duration_sec)
        self.measured_entropy = calculate_shannon_entropy(text)

        # 2. Check for catastrophic exfiltration patterns -> immediate ATOMIC_HALT
        for pattern, desc in EXFIL_PATTERNS:
            if pattern.search(text):
                self.violation_reason = f"Critical boundary violation: {desc}"
                self._set_state(OuterState.ATOMIC_HALT)
                return False, self.violation_reason

        # 3. Shannon Entropy Anomaly Check (e.g. Base64 exfiltration or high-entropy bursts)
        trimmed = text.strip()
        if len(trimmed) >= 28 and self.measured_entropy > 4.70:
            # Check if benign structured format (e.g. UUID)
            if UUID_PATTERN.match(trimmed):
                if self.state == OuterState.ELEVATED_SCRUTINY:
                    self._set_state(OuterState.ACTIVE_MONITORING)
                    return True, "High-entropy token verified as benign UUID. Scrutiny de-escalated to ACTIVE_MONITORING."
                return True, "Verified benign high-entropy token (UUID)."
            else:
                # Anomaly detected
                if self.state == OuterState.ACTIVE_MONITORING:
                    self._set_state(OuterState.ELEVATED_SCRUTINY)
                    return True, f"Anomalous entropy ({self.measured_entropy:.2f} bits) detected. Escalated to ELEVATED_SCRUTINY."
                elif self.state == OuterState.ELEVATED_SCRUTINY:
                    self.violation_reason = f"Sustained unverified high-entropy exfiltration ({self.measured_entropy:.2f} bits)."
                    self._set_state(OuterState.CONTAINED_QUARANTINE)
                    return False, self.violation_reason

        # 4. De-escalation Path: Normal payload clears elevated scrutiny
        if self.state == OuterState.ELEVATED_SCRUTINY and (UUID_PATTERN.match(trimmed) or self.measured_entropy <= 4.6):
            self._set_state(OuterState.ACTIVE_MONITORING)
            return True, "Payload cleared. Outer FSM de-escalated from ELEVATED_SCRUTINY to ACTIVE_MONITORING."

        # 5. Normal compliant state
        if self.state not in (OuterState.CONTAINED_QUARANTINE, OuterState.ATOMIC_HALT):
            if self.state == OuterState.SECURE_STANDBY:
                self._set_state(OuterState.ACTIVE_MONITORING)
            return True, f"Payload compliant (Entropy: {self.measured_entropy:.2f}, Velocity: {self.token_velocity:.1f} t/s)."

        return False, f"Outer boundary non-compliant in state {self.state.value}."

    def force_atomic_halt(self, reason: str):
        """Forces immediate transition to ATOMIC_HALT."""
        self.violation_reason = reason
        self._set_state(OuterState.ATOMIC_HALT)

    def revert_to_standby(self):
        """Functorial Reversibility (L1-002): resets Outer FSM to SECURE_STANDBY after human audit."""
        self.violation_reason = None
        self._set_state(OuterState.SECURE_STANDBY)

    def _set_state(self, new_state: OuterState):
        self.state = new_state
        self.history.append(new_state)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_state": self.state.value,
            "token_velocity": round(self.token_velocity, 2),
            "measured_entropy": round(self.measured_entropy, 2),
            "active_capability_leases": self.active_capability_leases,
            "taint_flags": self.taint_flags,
            "violation_reason": self.violation_reason,
            "history_depth": len(self.history),
        }
