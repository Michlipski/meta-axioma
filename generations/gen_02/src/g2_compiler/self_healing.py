"""Ephemeral Self-Healing Invariant Restoration Loop [L1-G2-002].

Biological Homeorhesis Principle:
    Infraction(s) ⟹ Loop_{k ≤ 3}(Heal(s)) ∧ BlastContainment(s)
    Compiler and runtime pipelines encountering invariant infractions must trigger
    isolated, bounded self-healing loops within ephemeral exception enclaves before
    failing or emitting fatal termination.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import copy
import traceback

from g2_compiler.types import RepairStatus, SelfHealingResult


class EphemeralSelfHealingEnclave:
    """Isolates operations within a sandboxed enclave and executes up to 3 repair passes upon invariant infractions."""

    def __init__(self, enclave_name: str = "SelfHealingEnclave", max_passes: int = 3):
        self.enclave_name = enclave_name
        self.max_passes = max_passes
        self._leakage_detected = False

    def execute_with_healing(
        self,
        operation: Callable[[Dict[str, Any]], Any],
        initial_context: Dict[str, Any],
        invariant_checker: Callable[[Any, Dict[str, Any]], Tuple[bool, List[str]]],
        remediator: Callable[[List[str], Dict[str, Any], int], Dict[str, Any]],
        operation_name: str = "UnnamedOperation",
    ) -> SelfHealingResult:
        """Executes operation in sandbox. If invariant fails, remediates iteratively up to max_passes."""
        # 1. Enclave Sandbox Isolation: deeply copy context to prevent state leakage
        sandbox_context = copy.deepcopy(initial_context)
        pre_execution_snapshot = copy.deepcopy(initial_context)

        infractions_seen: List[str] = []
        remediations_applied: List[str] = []
        current_pass = 0
        execution_result = None

        while current_pass < self.max_passes:
            current_pass += 1
            op_failed = False
            caught_exception: Optional[Exception] = None

            try:
                execution_result = operation(sandbox_context)
            except Exception as e:
                op_failed = True
                caught_exception = e
                infractions_seen.append(f"Runtime Exception: {type(e).__name__}: {str(e)}")

            if not op_failed:
                # Run formal invariant check
                invariants_ok, detected_infractions = invariant_checker(execution_result, sandbox_context)
                if invariants_ok:
                    # Enclave invariant restoration succeeded!
                    # Verify blast containment: initial context was never mutated directly
                    leakage = self._check_blast_leakage(initial_context, pre_execution_snapshot)
                    status = RepairStatus.HEALED if current_pass > 1 else RepairStatus.NO_INFRACTION
                    return SelfHealingResult(
                        operation_name=operation_name,
                        attempts_executed=current_pass,
                        max_attempts=self.max_passes,
                        infractions_detected=infractions_seen,
                        remediations_applied=remediations_applied,
                        blast_leakage_detected=leakage,
                        status=status,
                        execution_result=execution_result,
                    )
                else:
                    infractions_seen.extend(detected_infractions)

            # If we reach here, an infraction or exception occurred; trigger remediation
            remediation_desc = f"Pass {current_pass}: Remediating infractions [{', '.join(infractions_seen[-2:])}]"
            remediations_applied.append(remediation_desc)
            try:
                sandbox_context = remediator(infractions_seen, sandbox_context, current_pass)
            except Exception as rem_err:
                infractions_seen.append(f"Remediator Failure: {str(rem_err)}")
                break

        # Max passes exhausted without invariant restoration
        leakage = self._check_blast_leakage(initial_context, pre_execution_snapshot)
        return SelfHealingResult(
            operation_name=operation_name,
            attempts_executed=current_pass,
            max_attempts=self.max_passes,
            infractions_detected=infractions_seen,
            remediations_applied=remediations_applied,
            blast_leakage_detected=leakage,
            status=RepairStatus.UNRECOVERABLE,
            execution_result=execution_result,
        )

    def _check_blast_leakage(
        self, current_initial: Dict[str, Any], pristine_snapshot: Dict[str, Any]
    ) -> bool:
        """Verifies that the parent context remained untouched by sandbox mutations."""
        return current_initial != pristine_snapshot
