"""Physical Mutation Falsifier & Non-Tautological Test Sentry (`soc_g4b_audit`).

Enforces:
- [INV-G4B-MUTATION-001]: Physical Mutation Falsification Invariant.
- Mathematical Proof:
    Result(mutated_code) == FAIL => Certified Non-Tautological
    Result(mutated_code) == PASS => TautologicalTestViolation (REJECT)
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid

from .domain_models import (
    AuditDomainInvariantViolation,
    MutationWitness,
    TautologicalTestViolation,
)


class PhysicalMutationFalsifier:
    """Proves that test suites are non-tautological by verifying they fail when code is damaged on disk."""

    def __init__(self, node_id: str = "node_mutation_falsifier") -> None:
        self.node_id = node_id

    def assert_mutation_fails_test(
        self,
        target_file: Path | str,
        mutation_pattern: Tuple[str, str],
        test_command: List[str],
        expected_failure_substring: Optional[str] = None,
        timeout_s: float = 30.0,
    ) -> MutationWitness:
        """Physically mutates target_file on disk and asserts test_command fails."""
        target_path = Path(target_file).resolve()
        if not target_path.exists() or not target_path.is_file():
            raise AuditDomainInvariantViolation(f"Target file does not exist or is not a file: {target_path}")

        pattern, replacement = mutation_pattern
        original_bytes = target_path.read_bytes()
        original_sha256 = hashlib.sha256(original_bytes).hexdigest()

        try:
            original_text = original_bytes.decode("utf-8")
        except UnicodeDecodeError as e:
            raise AuditDomainInvariantViolation(f"Target file must be UTF-8 text for mutation: {target_path}") from e

        if pattern not in original_text:
            raise AuditDomainInvariantViolation(
                f"Mutation target pattern {pattern!r} was not found in target file: {target_path}"
            )

        # Create bit-reversible backup: .<filename>.bak.<original_sha256>
        backup_filename = f".{target_path.name}.bak.{original_sha256}"
        backup_path = target_path.parent / backup_filename
        backup_path.write_bytes(original_bytes)

        mutated_text = original_text.replace(pattern, replacement, 1)
        mutated_bytes = mutated_text.encode("utf-8")
        mutated_sha256 = hashlib.sha256(mutated_bytes).hexdigest()

        proc: Optional[subprocess.CompletedProcess] = None

        try:
            # Physically mutate file on disk
            target_path.write_bytes(mutated_bytes)

            try:
                proc = subprocess.run(
                    test_command,
                    capture_output=True,
                    text=True,
                    timeout=timeout_s,
                )
            except subprocess.TimeoutExpired as te:
                timeout_err_msg = f"Test command timed out after {timeout_s}s: {te}"
                stdout = te.stdout or ""
                stderr = (te.stderr or "") + f"\n{timeout_err_msg}"
                proc = subprocess.CompletedProcess(
                    args=test_command,
                    returncode=124,
                    stdout=stdout,
                    stderr=stderr,
                )
        finally:
            # Guaranteed restoration with SHA-256 integrity verification
            if backup_path.exists():
                restored_bytes = backup_path.read_bytes()
            else:
                restored_bytes = original_bytes

            target_path.write_bytes(restored_bytes)
            restored_sha256 = hashlib.sha256(target_path.read_bytes()).hexdigest()

            if backup_path.exists():
                try:
                    backup_path.unlink()
                except Exception:
                    pass

            if restored_sha256 != original_sha256:
                raise AuditDomainInvariantViolation(
                    f"Physical restoration failure on {target_path}: "
                    f"restored SHA-256 ({restored_sha256}) does not match original ({original_sha256})."
                )

        stdout = proc.stdout if proc is not None else ""
        stderr = proc.stderr if proc is not None else ""
        exit_code = proc.returncode if proc is not None else -1

        # Check: Did test pass despite code mutation?
        if exit_code == 0:
            raise TautologicalTestViolation(
                f"[INV-G4B-MUTATION-001 Violation] Test suite passed (exit code 0) despite physical mutation in "
                f"'{target_path.name}' ({pattern!r} -> {replacement!r}).\n"
                f"Test command: {' '.join(test_command)}\n"
                f"Stdout snippet:\n{stdout[:1000]}\n"
                f"Stderr snippet:\n{stderr[:1000]}"
            )

        # Test failed as expected (non-zero exit code)
        if expected_failure_substring:
            combined_output = f"{stdout}\n{stderr}"
            if expected_failure_substring not in combined_output:
                raise AuditDomainInvariantViolation(
                    f"Test failed as expected with exit code {exit_code}, but expected failure substring "
                    f"{expected_failure_substring!r} was not found in test output.\n"
                    f"Output snippet:\n{combined_output[:1000]}"
                )

        witness = MutationWitness(
            witness_id=f"wit_mut_{uuid.uuid4().hex[:12]}",
            target_file=str(target_path),
            mutation_pattern=mutation_pattern,
            test_command=list(test_command),
            exit_code=exit_code,
            stdout_snippet=stdout[:500],
            stderr_snippet=stderr[:500],
            original_sha256=original_sha256,
            mutated_sha256=mutated_sha256,
            restored_sha256=restored_sha256,
            verified=True,
            timestamp_ns=time.time_ns(),
        )
        return witness


def check_and_restore_stale_mutations(repo_root: Path | str) -> List[Path]:
    """Scans repository for orphaned .*.bak.<sha256> backup files and restores original content."""
    root = Path(repo_root).resolve()
    restored: List[Path] = []
    if not root.exists():
        return restored

    for p in root.rglob(".*.bak.*"):
        if not p.is_file():
            continue
        parts = p.name.split(".bak.")
        if len(parts) == 2 and len(parts[1]) == 64:
            target_name = parts[0].lstrip(".")
            target_path = p.parent / target_name
            backup_bytes = p.read_bytes()
            backup_sha256 = parts[1]
            if hashlib.sha256(backup_bytes).hexdigest() == backup_sha256:
                target_path.write_bytes(backup_bytes)
                restored.append(target_path)
            try:
                p.unlink()
            except Exception:
                pass

    return restored
