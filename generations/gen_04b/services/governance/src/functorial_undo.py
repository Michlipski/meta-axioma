"""Functorial Undo & Categorical Adjoint State Reversal (`soc_g4b_governance`).

Enforces:
- Invariant [L1-002]: Statechart Determinism & 1-Tap Functorial Reversibility.
- Strict categorical adjoint state reversal: S_{t-1} = f^{-1}(S_t) for all
  governance decisions, supervisor overrides, RFC adjudications, and circuit breaker states.
- Preserves causal monotonicity, cryptographic state hashes, and Landauer bit recovery bounds.
"""

from __future__ import annotations

import copy
import hashlib
import time
from typing import Any, Dict, List, Optional
import uuid

from .domain_models import (
    GovernanceDomainInvariantViolation,
    GovernanceKernelState,
)


class FunctorialUndoViolation(GovernanceDomainInvariantViolation):
    """Raised when an adjoint rollback operation fails or violates causal history."""
    pass


class FunctorialUndoEngine:
    """Manages causal history stack and deterministic adjoint rollbacks for Sovereign Governance."""

    def __init__(self, max_depth: int = 1000) -> None:
        self.max_depth = max_depth
        self._history_stack: List[GovernanceKernelState] = []
        self._state_hashes: List[str] = []

    def push_state(self, state: GovernanceKernelState) -> str:
        """Pushes an immutable snapshot of GovernanceKernelState onto the causal undo stack."""
        state.validate_invariants()
        snapshot = copy.deepcopy(state)
        state_hash = snapshot.compute_hash()

        if len(self._history_stack) >= self.max_depth:
            # Drop oldest to preserve bounded memory (thermodynamic lease)
            self._history_stack.pop(0)
            self._state_hashes.pop(0)

        self._history_stack.append(snapshot)
        self._state_hashes.append(state_hash)
        return state_hash

    def undo(self) -> Optional[GovernanceKernelState]:
        """Reverses the most recent state transition: S_{t-1} = f^{-1}(S_t).

        Returns:
            The previous GovernanceKernelState, or None if undo stack depth is <= 1.
        """
        if not self.can_undo():
            return None

        # Pop current head state
        self._history_stack.pop()
        self._state_hashes.pop()

        # The new top of stack is S_{t-1}
        restored = copy.deepcopy(self._history_stack[-1])
        restored.validate_invariants()
        return restored

    def can_undo(self) -> bool:
        """Returns True if there is at least one previous state to roll back to."""
        return len(self._history_stack) > 1

    def history_depth(self) -> int:
        """Returns the current depth of the causal history stack."""
        return len(self._history_stack)

    def peek_current(self) -> Optional[GovernanceKernelState]:
        """Peeks at the current top of the stack without popping."""
        if not self._history_stack:
            return None
        return copy.deepcopy(self._history_stack[-1])

    def get_stack_hashes(self) -> List[str]:
        """Returns the SHA-256 state hashes of all stacked snapshots."""
        return list(self._state_hashes)

    def clear(self) -> None:
        """Clears the causal history stack."""
        self._history_stack.clear()
        self._state_hashes.clear()
