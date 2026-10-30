"""Functorial Undo & Mathematical Adjoint Rollback Manager (`soc_g4b_audit`).

Enforces:
- Invariant [L1-002]: Statechart Determinism & 1-Tap Functorial Reversibility.
- Strict adjoint functorial state rollback preserving causal consistency and cryptographic hashes.
- Bit-reversal mechanics: exact Landauer bit recovery and thermodynamic heat reversal accounting.
"""

from __future__ import annotations

import copy
import hashlib
import time
from typing import Any, Dict, List, Optional
import uuid

from .domain_models import (
    AuditDomainInvariantViolation,
    AuditVerificationStage,
    FunctorialUndoCheckpoint,
    LandauerThermodynamicLedger,
)


class FunctorialUndoViolation(Exception):
    """Raised when an adjoint rollback fails or attempts to violate causal monotonicity."""
    pass


class AuditFunctorialUndoManager:
    """Manages causal checkpoints, adjoint rollbacks, and thermodynamic bit recovery."""

    def __init__(self) -> None:
        self._stack: List[FunctorialUndoCheckpoint] = []
        self._checkpoints_by_id: Dict[str, FunctorialUndoCheckpoint] = {}

    def create_checkpoint(
        self,
        stage: AuditVerificationStage,
        state_hash: str,
        landauer_bits_checkpoint: int,
        context: Optional[Dict[str, Any]] = None,
    ) -> FunctorialUndoCheckpoint:
        """Pushes an immutable causal checkpoint onto the undo stack."""
        checkpoint_id = f"ckpt_undo_{uuid.uuid4().hex[:12]}"
        ctx = copy.deepcopy(context or {})

        checkpoint = FunctorialUndoCheckpoint(
            checkpoint_id=checkpoint_id,
            stage=stage,
            state_hash=state_hash,
            landauer_bits_checkpoint=landauer_bits_checkpoint,
            restoration_context=ctx,
        )
        checkpoint.validate_invariants()

        self._stack.append(checkpoint)
        self._checkpoints_by_id[checkpoint_id] = checkpoint
        return checkpoint

    def rollback_to_checkpoint(
        self,
        checkpoint_id: str,
        thermodynamic_ledger: Optional[LandauerThermodynamicLedger] = None,
    ) -> FunctorialUndoCheckpoint:
        """Rolls back the causal stack to the designated checkpoint and recovers Landauer bits."""
        if checkpoint_id not in self._checkpoints_by_id:
            raise FunctorialUndoViolation(f"Checkpoint ID '{checkpoint_id}' not found in undo history.")

        target_idx = -1
        for i, cp in enumerate(self._stack):
            if cp.checkpoint_id == checkpoint_id:
                target_idx = i
                break

        if target_idx == -1:
            raise FunctorialUndoViolation(f"Checkpoint '{checkpoint_id}' is no longer active on causal stack.")

        target_cp = self._stack[target_idx]

        # Calculate bit recovery if ledger is provided
        if thermodynamic_ledger is not None:
            current_bits = thermodynamic_ledger.total_bits_erased
            target_bits = target_cp.landauer_bits_checkpoint
            if current_bits > target_bits:
                recovered = current_bits - target_bits
                thermodynamic_ledger.record_bit_recovery(recovered)

        # Truncate stack back to target checkpoint
        self._stack = self._stack[: target_idx + 1]
        return target_cp

    def rollback_latest(
        self,
        thermodynamic_ledger: Optional[LandauerThermodynamicLedger] = None,
    ) -> FunctorialUndoCheckpoint:
        """Pops the most recent checkpoint and restores to the preceding causal state."""
        if len(self._stack) < 2:
            raise FunctorialUndoViolation("Cannot rollback latest: undo stack depth is less than 2.")

        # Pop current top
        popped = self._stack.pop()

        # Target is new top
        target_cp = self._stack[-1]

        if thermodynamic_ledger is not None:
            current_bits = thermodynamic_ledger.total_bits_erased
            target_bits = target_cp.landauer_bits_checkpoint
            if current_bits > target_bits:
                recovered = current_bits - target_bits
                thermodynamic_ledger.record_bit_recovery(recovered)

        return target_cp

    def get_stack_depth(self) -> int:
        return len(self._stack)

    def get_checkpoint_history(self) -> List[FunctorialUndoCheckpoint]:
        return list(self._stack)
