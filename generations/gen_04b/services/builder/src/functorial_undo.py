"""Generation 4b Functorial Undo & Reversible State Checkpointing (`[L1-002]`).

Enforces:
- 1-tap deterministic state unwinding and checkpoint restoration.
- Functorial preservation of causal history and parent checkpoint links.
- Thermodynamic bit-erasure tracking during state rollback.
- Deep state context snapshotting.
"""

from __future__ import annotations

import copy
import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple

from .domain_models import (
    DomainInvariantViolation,
    FunctorialUndoCheckpoint,
)


class FunctorialUndoViolation(Exception):
    """Raised when an undo operation violates causal invariant or targets non-existent checkpoint."""
    pass


class FunctorialUndoManager:
    """Manages causal checkpoint tree and 1-tap state restorations."""

    def __init__(self):
        # All checkpoints: checkpoint_id -> FunctorialUndoCheckpoint
        self._checkpoints: Dict[str, FunctorialUndoCheckpoint] = {}
        # Linear history stack of checkpoint IDs
        self._history_stack: List[str] = []
        # Current active checkpoint ID
        self.active_checkpoint_id: Optional[str] = None

    def create_checkpoint(
        self,
        state_label: str,
        state_context: Dict[str, Any],
        erased_bits: int = 0,
        active_node_id: str = "",
        merkle_root: str = "",
    ) -> FunctorialUndoCheckpoint:
        """Captures an immutable snapshot of system state and pushes to causal history."""
        chk_id = f"chk_{hashlib.sha256((state_label + str(time.time()) + str(len(self._history_stack))).encode()).hexdigest()[:12]}"
        
        # Deepcopy context to guarantee immutability
        immutable_context = copy.deepcopy(state_context)

        checkpoint = FunctorialUndoCheckpoint(
            checkpoint_id=chk_id,
            parent_checkpoint_id=self.active_checkpoint_id,
            state_label=state_label,
            state_context=immutable_context,
            erased_bits_at_checkpoint=erased_bits,
            active_node_id=active_node_id,
            merkle_root=merkle_root,
        )
        checkpoint.validate_invariants()

        self._checkpoints[chk_id] = checkpoint
        self._history_stack.append(chk_id)
        self.active_checkpoint_id = chk_id
        return checkpoint

    def can_undo(self) -> bool:
        """Returns True if there is a parent checkpoint available for rollback."""
        if not self.active_checkpoint_id:
            return False
        active = self._checkpoints.get(self.active_checkpoint_id)
        return active is not None and active.parent_checkpoint_id is not None

    def undo(self, target_checkpoint_id: Optional[str] = None) -> Tuple[FunctorialUndoCheckpoint, int]:
        """Restores state to target checkpoint (or immediate parent), returning restored snapshot and reversed bits."""
        if not self.active_checkpoint_id:
            raise FunctorialUndoViolation("No active checkpoint exists to unwind from.")

        curr = self._checkpoints[self.active_checkpoint_id]

        if target_checkpoint_id is None:
            if not curr.parent_checkpoint_id:
                raise FunctorialUndoViolation("Cannot undo past genesis checkpoint.")
            target_id = curr.parent_checkpoint_id
        else:
            target_id = target_checkpoint_id
            if target_id not in self._checkpoints:
                raise FunctorialUndoViolation(f"Target checkpoint '{target_id}' does not exist.")

        target = self._checkpoints[target_id]

        # Calculate bit reversal differential
        bit_diff = max(0, curr.erased_bits_at_checkpoint - target.erased_bits_at_checkpoint)

        # Unwind history stack to target
        if target_id in self._history_stack:
            idx = self._history_stack.index(target_id)
            self._history_stack = self._history_stack[: idx + 1]

        self.active_checkpoint_id = target_id
        return target, bit_diff

    def get_current_context(self) -> Optional[Dict[str, Any]]:
        """Returns a copy of the currently active checkpoint's state context."""
        if not self.active_checkpoint_id:
            return None
        return copy.deepcopy(self._checkpoints[self.active_checkpoint_id].state_context)

    def get_checkpoint(self, checkpoint_id: str) -> Optional[FunctorialUndoCheckpoint]:
        return self._checkpoints.get(checkpoint_id)

    def total_checkpoints(self) -> int:
        return len(self._checkpoints)
