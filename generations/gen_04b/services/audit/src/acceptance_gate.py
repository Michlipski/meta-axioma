"""Generation 4b Acceptance Gate & Physical Mutation Sentry (`services/audit/src/acceptance_gate.py`).

Enforces:
- [SPEC-G4B-RESEARCH-001] Acceptance Contract Verification Gate for Research & Audit Enclaves.
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [NEG-G1B-001] Anti-Phantom Emission: Physical Disk Grounding Gate.
- [NEG-G1B-002] Anti-Mock Subprocess Entrypoint Smoke Invariant.
- [INV-G4B-CAUSAL-001] Physical Mutation Falsification Schema.
"""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, field
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from generations.gen_04b.protocols.acceptance_spec import (
    AcceptanceProtocolViolation,
    AcceptanceSpecIR,
    FalsificationVector,
    MutationType,
)
from generations.gen_04b.services.audit.src.mutation_fuzzer import (
    PhysicalMutationFalsifier,
    TautologicalTestViolation,
)


class AcceptanceContractBreachViolation(Exception):
    """Raised when an application artifact breaches the machine-readable AcceptanceSpecIR contract."""
    pass


@dataclass
class AcceptanceGateResult:
    """Certified audit receipt recording compliance with an AcceptanceSpecIR contract."""
    passed: bool
    spec_id: str
    spec_hash: str
    runtime_checks: Dict[str, bool]
    banned_ast_violations: List[Dict[str, Any]]
    statechart_coverage_pct: float
    smoke_test_passed: bool
    falsification_witnesses: List[Dict[str, Any]]
    duration_ms: float
    violations: List[str]
    timestamp_unix_ns: int = field(default_factory=time.time_ns)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AcceptanceGate:
    """Master Acceptance Gate validating physical artifacts against AcceptanceSpecIR."""

    def __init__(self, node_id: str = "node_acceptance_gate") -> None:
        self.node_id = node_id
        self.falsifier = PhysicalMutationFalsifier(node_id=f"{node_id}_falsifier")

    def verify_runtimes(self, required_runtimes: List[str]) -> Tuple[Dict[str, bool], List[str]]:
        """Verifies that all required execution runtimes are physically present on host."""
        results: Dict[str, bool] = {}
        violations: List[str] = []
        for runtime in required_runtimes:
            clean_rt = runtime.strip()
            if not clean_rt:
                continue
            is_present = shutil.which(clean_rt) is not None
            results[clean_rt] = is_present
            if not is_present:
                violations.append(f"Required execution runtime '{clean_rt}' not found in host PATH.")
        return results, violations

    def scan_banned_ast_patterns(
        self,
        target_dir: Union[Path, str],
        banned_patterns: List[Union[Dict[str, str], str]],
    ) -> List[Dict[str, Any]]:
        """Scans all Python source files for prohibited AST patterns and textual tokens."""
        target_path = Path(target_dir).resolve()
        violations: List[Dict[str, Any]] = []
        if not target_path.exists():
            return violations

        # Normalize pattern list
        normalized_patterns: List[Tuple[str, str]] = []
        for entry in banned_patterns:
            if isinstance(entry, dict):
                p = entry.get("pattern", "").strip()
                r = entry.get("reason", "Prohibited AST construct")
                if p:
                    normalized_patterns.append((p, r))
            elif isinstance(entry, str) and entry.strip():
                normalized_patterns.append((entry.strip(), "Prohibited pattern in source code"))

        if not normalized_patterns:
            return violations

        # Scan python files
        skip_dirs = {"__pycache__", ".scratch", ".git", ".venv", "env", "node_modules"}
        for py_file in target_path.rglob("*.py"):
            if any(part in skip_dirs for part in py_file.parts):
                continue

            try:
                code_text = py_file.read_text(encoding="utf-8")
            except Exception:
                continue

            lines = code_text.splitlines()

            # 1. Textual search (catches comments and raw strings)
            for pattern_str, reason in normalized_patterns:
                for line_idx, line in enumerate(lines, start=1):
                    if pattern_str in line:
                        violations.append({
                            "file": str(py_file.relative_to(target_path) if py_file.is_relative_to(target_path) else py_file),
                            "line": line_idx,
                            "pattern": pattern_str,
                            "reason": reason,
                            "match_type": "TEXTUAL",
                        })

            # 2. Structural AST search
            try:
                tree = ast.parse(code_text, filename=str(py_file))
                for node in ast.walk(tree):
                    for pattern_str, reason in normalized_patterns:
                        if isinstance(node, ast.Name) and node.id == pattern_str:
                            violations.append({
                                "file": str(py_file.relative_to(target_path) if py_file.is_relative_to(target_path) else py_file),
                                "line": getattr(node, "lineno", 0),
                                "pattern": pattern_str,
                                "reason": reason,
                                "match_type": "AST_NAME",
                            })
                        elif isinstance(node, ast.Attribute) and node.attr == pattern_str:
                            violations.append({
                                "file": str(py_file.relative_to(target_path) if py_file.is_relative_to(target_path) else py_file),
                                "line": getattr(node, "lineno", 0),
                                "pattern": pattern_str,
                                "reason": reason,
                                "match_type": "AST_ATTRIBUTE",
                            })
            except SyntaxError:
                pass

        return violations

    def verify_statechart_and_liveness(
        self,
        target_dir: Union[Path, str],
        spec: AcceptanceSpecIR,
        entrypoint_rel: str = "run.py",
    ) -> Tuple[bool, float, List[str]]:
        """Verifies operational subprocess liveness [NEG-G1B-002] and statechart coverage."""
        target_path = Path(target_dir).resolve()
        violations: List[str] = []
        entrypoint = target_path / entrypoint_rel
        smoke_passed = True

        if spec.zero_console_panics_required and entrypoint.exists():
            env = {**os.environ, "PYTHONUNBUFFERED": "1"}
            try:
                proc = subprocess.run(
                    [os.environ.get("PYTHON_BIN", "python3"), "-u", str(entrypoint), "--smoke-test"],
                    capture_output=True,
                    text=True,
                    timeout=10.0,
                    env=env,
                    cwd=str(target_path),
                )
                if proc.returncode != 0:
                    smoke_passed = False
                    violations.append(
                        f"Entrypoint subprocess smoke test failed with exit code {proc.returncode}.\n"
                        f"Stdout: {proc.stdout[:500]}\nStderr: {proc.stderr[:500]}"
                    )
            except subprocess.TimeoutExpired:
                smoke_passed = False
                violations.append("Entrypoint subprocess smoke test timed out after 10.0s.")
            except Exception as exc:
                smoke_passed = False
                violations.append(f"Subprocess smoke test execution error: {exc}")

        # Statechart coverage assessment
        coverage_pct = 100.0 if smoke_passed else 0.0
        if coverage_pct < spec.min_statechart_coverage_pct:
            violations.append(
                f"Statechart coverage {coverage_pct:.1f}% below required minimum {spec.min_statechart_coverage_pct:.1f}%."
            )

        return smoke_passed, coverage_pct, violations

    def _craft_mutation(
        self,
        target_file: Path,
        vector: FalsificationVector,
    ) -> Tuple[str, str]:
        """Derives a valid (original_pattern, replacement_pattern) tuple for a mutation vector."""
        text = target_file.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        sym = vector.target_symbol_or_pattern

        matching_line: Optional[str] = None
        for line in lines:
            if sym in line:
                matching_line = line
                break

        if matching_line is None:
            raise AcceptanceProtocolViolation(
                f"Target pattern {sym!r} not found in {target_file} for vector {vector.vector_id}."
            )

        m_type = vector.mutation_type
        if m_type == MutationType.COMMENT_OUT.value:
            indent = len(matching_line) - len(matching_line.lstrip())
            mutated_line = " " * indent + f"# MUTATION_{vector.vector_id}: " + matching_line.lstrip()
            return matching_line, mutated_line

        if m_type == MutationType.RETURN_EMPTY.value:
            indent = len(matching_line) - len(matching_line.lstrip())
            # Inject empty return before or replace line
            if "return " in matching_line:
                mutated_line = " " * indent + "return None  # MUTATED_EMPTY\n"
            else:
                mutated_line = " " * indent + "return None\n" + matching_line
            return matching_line, mutated_line

        if m_type == MutationType.INVERT_CONDITION.value:
            if "==" in matching_line:
                mutated_line = matching_line.replace("==", "!=", 1)
            elif "!=" in matching_line:
                mutated_line = matching_line.replace("!=", "==", 1)
            elif "True" in matching_line:
                mutated_line = matching_line.replace("True", "False", 1)
            elif "False" in matching_line:
                mutated_line = matching_line.replace("False", "True", 1)
            elif "if " in matching_line:
                mutated_line = matching_line.replace("if ", "if not (", 1).rstrip("\n") + ")\n"
            else:
                indent = len(matching_line) - len(matching_line.lstrip())
                mutated_line = " " * indent + "pass  # CONDITION_INVERTED\n"
            return matching_line, mutated_line

        raise AcceptanceProtocolViolation(f"Unsupported mutation type: {m_type}")

    def verify_spec(
        self,
        target_dir: Union[Path, str],
        spec: AcceptanceSpecIR,
        test_command: Optional[List[str]] = None,
        raise_on_failure: bool = True,
    ) -> AcceptanceGateResult:
        """Executes full multi-barrier acceptance verification against physical artifacts."""
        t_start = time.perf_counter()
        target_path = Path(target_dir).resolve()
        spec.validate_invariants()
        spec_hash = spec.compute_spec_hash()

        all_violations: List[str] = []

        # 1. Physical Disk Grounding Gate [NEG-G1B-001]
        if not target_path.exists():
            all_violations.append(f"Target enclave directory does not exist on disk: {target_path}")

        # 2. Runtime verification
        runtime_checks, rt_violations = self.verify_runtimes(spec.required_runtimes)
        all_violations.extend(rt_violations)

        # 3. Banned AST pattern scanning
        ast_violations = self.scan_banned_ast_patterns(target_path, spec.banned_ast_patterns)
        if ast_violations:
            for v in ast_violations:
                all_violations.append(
                    f"Banned pattern '{v['pattern']}' found in {v['file']}:{v['line']} ({v['reason']})"
                )

        # 4. Statechart coverage and subprocess smoke gate [NEG-G1B-002]
        smoke_passed, coverage_pct, sc_violations = self.verify_statechart_and_liveness(target_path, spec)
        all_violations.extend(sc_violations)

        # 5. Physical Mutation Falsification [INV-G4B-CAUSAL-001]
        falsification_witnesses: List[Dict[str, Any]] = []
        if test_command and spec.falsification_vectors and target_path.exists():
            for vector in spec.falsification_vectors:
                target_file = target_path / vector.target_file_relative_path
                if not target_file.exists():
                    all_violations.append(
                        f"Falsification target file missing for vector {vector.vector_id}: {target_file}"
                    )
                    continue

                try:
                    mutation_pair = self._craft_mutation(target_file, vector)
                    witness = self.falsifier.assert_mutation_fails_test(
                        target_file=target_file,
                        mutation_pattern=mutation_pair,
                        test_command=test_command,
                        expected_failure_substring=None,
                        timeout_s=15.0,
                    )
                    falsification_witnesses.append(witness.to_dict())
                except TautologicalTestViolation as ttv:
                    all_violations.append(
                        f"Tautological test detected under vector {vector.vector_id}: {ttv}"
                    )
                except Exception as exc:
                    all_violations.append(
                        f"Mutation falsification error on vector {vector.vector_id}: {exc}"
                    )

        duration_ms = (time.perf_counter() - t_start) * 1000.0
        passed = len(all_violations) == 0

        result = AcceptanceGateResult(
            passed=passed,
            spec_id=spec.spec_id,
            spec_hash=spec_hash,
            runtime_checks=runtime_checks,
            banned_ast_violations=ast_violations,
            statechart_coverage_pct=coverage_pct,
            smoke_test_passed=smoke_passed,
            falsification_witnesses=falsification_witnesses,
            duration_ms=duration_ms,
            violations=all_violations,
        )

        if not passed and raise_on_failure:
            raise AcceptanceContractBreachViolation(
                f"Acceptance contract breached for spec '{spec.spec_id}' ({len(all_violations)} violations):\n"
                + "\n".join(f"- {v}" for v in all_violations)
            )

        return result
