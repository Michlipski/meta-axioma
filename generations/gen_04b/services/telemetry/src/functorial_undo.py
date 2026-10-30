"""Functorial Undo & Mathematical Adjoint Rollback Engine (`soc_g4b_telemetry`).

Enforces:
- Invariant [L1-002]: Statechart Determinism & 1-Tap Functorial Reversibility.
- Strict causal checkpoint creation and pure adjoint rollback mechanics.
- Bit-reversal mechanics: exact Landauer bit recovery and thermodynamic heat dissipation reversal.
"""

from __future__ import annotations

import copy
import time
from typing import Any, Dict, List, Optional
import uuid

from .domain_models import (
    FunctorialUndoCheckpoint,
    TelemetryDomainInvariantViolation,
)


class TelemetryFunctorialUndoManager:
    """Manages causal checkpoints, adjoint rollbacks, and Landauer bit-reversal mechanics."""

    def __init__(self) -> None:
        self._stack: List[FunctorialUndoCheckpoint] = []
        self._checkpoints_by_id: Dict[str, FunctorialUndoCheckpoint] = {}

    def create_checkpoint(
        self,
        checkpoint_id: str,
        statechart_state: str,
        bits_erased: int,
        active_spans_count: int,
        state_snapshot: Dict[str, Any],
    ) -> FunctorialUndoCheckpoint:
        """Pushes an immutable causal checkpoint onto the undo stack."""
        if not checkpoint_id:
            checkpoint_id = f"ckpt_undo_{uuid.uuid4().hex[:12]}"

        checkpoint = FunctorialUndoCheckpoint(
            checkpoint_id=checkpoint_id,
            timestamp=int(time.time() * 1000),
            statechart_state=statechart_state,
            bits_erased=bits_erased,
            active_spans_count=active_spans_count,
            state_snapshot=copy.deepcopy(state_snapshot),
        )
        checkpoint.validate_invariants()

        self._stack.append(checkpoint)
        self._checkpoints_by_id[checkpoint_id] = checkpoint
        return checkpoint

    def rollback_to_checkpoint(
        self,
        checkpoint_id: str,
        thermodynamic_engine: Optional[Any] = None,
    ) -> FunctorialUndoCheckpoint:
        """Rolls back the causal stack to the designated checkpoint and recovers Landauer bits."""
        if checkpoint_id not in self._checkpoints_by_id:
            raise TelemetryDomainInvariantViolation(
                f"Checkpoint ID '{checkpoint_id}' not found in undo history."
            )

        target_idx = -1
        for i, cp in enumerate(self._stack):
            if cp.checkpoint_id == checkpoint_id:
                target_idx = i
                break

        if target_idx == -1:
            raise TelemetryDomainInvariantViolation(
                f"Checkpoint '{checkpoint_id}' is no longer active on causal stack."
            )

        target_cp = self._stack[target_idx]

        # Calculate bit recovery if thermodynamic engine is provided
        if thermodynamic_engine is not None and hasattr(thermodynamic_engine, "ledger"):
            current_bits = thermodynamic_engine.ledger.total_bits_erased
            target_bits = target_cp.bits_erased
            if current_bits > target_bits:
                recovered = current_bits - target_bits
                thermodynamic_engine.record_bit_recovery(recovered, operation=f"rollback_to_{checkpoint_id}")

        # Truncate stack back to target checkpoint
        self._stack = self._stack[: target_idx + 1]
        return target_cp

    def rollback_latest(
        self,
        thermodynamic_engine: Optional[Any] = None,
    ) -> FunctorialUndoCheckpoint:
        """Pops the most recent checkpoint and restores to the preceding causal state."""
        if len(self._stack) < 2:
            raise TelemetryDomainInvariantViolation(
                "Cannot rollback latest: undo stack depth is less than 2."
            )

        # Preceding checkpoint
        target_cp = self._stack[-2]
        return self.rollback_to_checkpoint(target_cp.checkpoint_id, thermodynamic_engine=thermodynamic_engine)

    def get_checkpoint_history(self) -> List[FunctorialUndoCheckpoint]:
        """Returns the full chronological history of active checkpoints on the stack."""
        return list(self._stack)

    def get_checkpoint(self, checkpoint_id: str) -> Optional[FunctorialUndoCheckpoint]:
        """Retrieves a checkpoint by its unique identifier."""
        return self._checkpoints_by_id.get(checkpoint_id)

    @property
    def stack_depth(self) -> int:
        return len(self._stack)
