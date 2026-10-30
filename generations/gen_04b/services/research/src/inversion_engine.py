"""Generation 4b Dialectical Negation & Architectural Inversion Engine (`soc_g4b_researcher`).

Enforces:
- [L1-G4B-005] Compulsory Architectural Inversion:
  Detects comfortable default primitives (centralized locks, mutable singletons, polling loops)
  and injects formal negative constraints (`NEG_PRIMITIVE`) that compel the synthesizer to
  construct novel category-theoretic and distributed alternatives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from .domain_models import (
    DialecticalNegationSeed,
    DomainInvariantViolation,
)


class NegatedPrimitiveViolation(Exception):
    """Raised when an architectural candidate re-introduces a vetoed default primitive."""
    pass


class DialecticalInversionEngine:
    """Engine responsible for injecting NEG_PRIMITIVE constraints and breaking bias."""

    # Canonical default primitives and their orthogonal inversions
    CANONICAL_INVERSIONS: Dict[str, Dict[str, str]] = {
        "CENTRALIZED_COORDINATOR": {
            "negated_invariant": "NEG-PRIMITIVE-001: Centralized coordinator or leader node is strictly forbidden.",
            "forced_alternative": "Decentralized P2P gossip mesh with Sheaf-Quorum consensus.",
            "banned_tokens": ["coordinator", "master_node", "central_broker", "leader_election"],
        },
        "SHARED_MUTABLE_STATE": {
            "negated_invariant": "NEG-PRIMITIVE-002: In-place mutation of shared memory is strictly forbidden.",
            "forced_alternative": "Pure immutable state transitions S_{t+1} = f(S_t, E) with Functorial Undo.",
            "banned_tokens": ["global_state", "singleton", "shared_dict", "mutable_variable"],
        },
        "PERIODIC_POLLING": {
            "negated_invariant": "NEG-PRIMITIVE-003: Fixed periodic sleep/polling loops are strictly forbidden.",
            "forced_alternative": "Reactive event-driven async streaming with push backpressure.",
            "banned_tokens": ["while_sleep", "poll_interval", "busy_wait", "periodic_timer"],
        },
        "SYNCHRONOUS_BLOCKING_RPC": {
            "negated_invariant": "NEG-PRIMITIVE-004: Synchronous thread-blocking calls are strictly forbidden.",
            "forced_alternative": "Non-blocking AsyncIO actor mailbox messaging with timeout enclaves.",
            "banned_tokens": ["requests.get", "time.sleep", "thread.join", "blocking_call"],
        },
        "SHARED_SQLITE_FILE": {
            "negated_invariant": "NEG-PRIMITIVE-005: Shared file-level SQLite locks are strictly forbidden across nodes.",
            "forced_alternative": "CRDT event-sourcing with partition-tolerant local-first storage.",
            "banned_tokens": ["sqlite3.connect", "database.db", "table_lock", "shared_sqlite"],
        },
    }

    def __init__(self):
        self.active_seeds: Dict[str, DialecticalNegationSeed] = {}
        self.enforced_invariants: List[str] = []

    def inject_inversion(self, primitive_key: str) -> DialecticalNegationSeed:
        """Injects a NEG_PRIMITIVE seed into the active compilation constraints."""
        if primitive_key not in self.CANONICAL_INVERSIONS:
            raise KeyError(
                f"Unknown primitive '{primitive_key}'. Valid: {list(self.CANONICAL_INVERSIONS.keys())}"
            )

        spec = self.CANONICAL_INVERSIONS[primitive_key]
        seed_id = f"seed_neg_{uuid.uuid4().hex[:8]}"

        seed = DialecticalNegationSeed(
            seed_id=seed_id,
            default_primitive=primitive_key,
            negated_invariant=spec["negated_invariant"],
            forced_alternative_archetype=spec["forced_alternative"],
        )
        seed.validate_invariants()
        self.active_seeds[seed_id] = seed
        self.enforced_invariants.append(spec["negated_invariant"])
        return seed

    def audit_architecture_against_negations(
        self,
        architecture_spec: Dict[str, Any],
    ) -> List[str]:
        """Audits a candidate architecture specification against all active NEG_PRIMITIVE seeds.

        Returns a list of violations (empty list if architecture is clean).
        """
        raw_text = json.dumps(architecture_spec).lower()
        violations: List[str] = []

        for seed in self.active_seeds.values():
            key = seed.default_primitive
            if key in self.CANONICAL_INVERSIONS:
                banned_tokens = self.CANONICAL_INVERSIONS[key]["banned_tokens"]
                for token in banned_tokens:
                    if token.lower() in raw_text:
                        violations.append(
                            f"Violation of {seed.negated_invariant}: detected banned token '{token}' "
                            f"in candidate architecture."
                        )

        return violations

    def enforce_clean_architecture(self, architecture_spec: Dict[str, Any]) -> None:
        """Raises NegatedPrimitiveViolation if candidate violates any active NEG_PRIMITIVE."""
        violations = self.audit_architecture_against_negations(architecture_spec)
        if violations:
            raise NegatedPrimitiveViolation(
                f"[L1-G4B-005 Trap] Candidate architecture violated active negative invariants:\n- "
                + "\n- ".join(violations)
            )

    def generate_random_inversion_challenge(self) -> DialecticalNegationSeed:
        """Picks a canonical default primitive at random or sequentially to stress an island."""
        keys = list(self.CANONICAL_INVERSIONS.keys())
        # Pick the first one not already active, or the first key
        for k in keys:
            if not any(s.default_primitive == k for s in self.active_seeds.values()):
                return self.inject_inversion(k)
        return self.inject_inversion(keys[0])
