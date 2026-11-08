"""Generation 4b Independent Adversarial QA Synthesizer (`[SPEC-G4B-BUILDER-001]`).

Enforces:
- CognitiveRole.ADVERSARIAL_QA_ENGINEER role boundary enforcement.
- Context sanitization stripping internal implementation details, builder reasoning, and private variables.
- Strict QA file boundary: Authorized to target `tests/`, `test_*.py`, `*_test.py`.
- Absolute prohibition against modifying `src/` or production code, raising QABoundaryViolation.
- Black-box test execution and external invariant verification returning ByzantineChaosReport.
"""

from __future__ import annotations

import copy
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from .domain_models import (
    ByzantineChaosReport,
    CognitiveRole,
    DomainInvariantViolation,
)


class QABoundaryViolation(DomainInvariantViolation):
    """Raised when an adversarial QA engineer attempts to modify production code or breach test boundaries."""
    pass


# Allowed QA Mutation Targets (Tests & scratch enclaves only)
ALLOWED_QA_PATTERNS = [
    re.compile(r"(?:^|/)tests?/"),
    re.compile(r"(?:^|/)test_[^/]+\.py$"),
    re.compile(r"(?:^|/)[^/]+_test\.py$"),
    re.compile(r"(?:^|/)\.scratch/"),
]

# Strictly Prohibited Production Code Targets for QA
PROHIBITED_PROD_PATTERNS = [
    re.compile(r"(?:^|/)(?:generations/[^/]+/)?services/[^/]+/src/"),
    re.compile(r"(?:^|/)apps/[^/]+/src/"),
    re.compile(r"(?:^|/)apps/[^/]+/static/"),
    re.compile(r"(?:^|/)src/"),
]

# Sensitive implementation detail keys stripped during context sanitization
STRIP_INTERNAL_KEYS: Set[str] = {
    "reasoning",
    "scratchpad",
    "implementation_notes",
    "internal_state",
    "private_fields",
    "builder_notes",
    "workarounds",
    "shortcuts",
    "inner_vars",
    "ast_internals",
    "private_methods",
    "source_internals",
    "ast_skeleton",
    "mock_stubs",
    "cached_shortcuts",
}


def validate_qa_target(target_path: str) -> None:
    """Validates that target_path conforms to the adversarial QA boundary.

    Raises:
        QABoundaryViolation: If target_path modifies production code in src/
                             or falls outside the authorized tests directory/files.
    """
    if not target_path or not str(target_path).strip():
        raise QABoundaryViolation("QA mutation target path must not be empty.")

    norm_path = str(target_path).replace("\\", "/").strip()

    # 1. Prohibit any production code target
    for pattern in PROHIBITED_PROD_PATTERNS:
        if pattern.search(norm_path):
            # Allow only if it is explicitly under a tests/ folder (e.g. tests/fixtures/)
            if not ("/tests/" in norm_path or norm_path.startswith("tests/")):
                raise QABoundaryViolation(
                    f"[SPEC-G4B-BUILDER-001 Violation] Adversarial QA Engineer is quarantined "
                    f"from modifying production code: '{target_path}'."
                )

    # 2. Must match allowed test patterns
    is_allowed = False
    for allowed_re in ALLOWED_QA_PATTERNS:
        if allowed_re.search(norm_path):
            is_allowed = True
            break

    if not is_allowed:
        raise QABoundaryViolation(
            f"[SPEC-G4B-BUILDER-001 Violation] Adversarial QA Engineer is only authorized "
            f"to target test files or directories ('tests/', 'test_*.py'), got: '{target_path}'."
        )


def _sanitize_dict_recursive(data: Any) -> Any:
    """Recursively strips private fields and internal builder details."""
    if isinstance(data, dict):
        clean_dict: Dict[str, Any] = {}
        for k, v in data.items():
            k_str = str(k)
            # Strip private keys starting with '_' (except dunder specials)
            if k_str.startswith("_") and not (k_str.startswith("__") and k_str.endswith("__")):
                continue
            # Strip banned internal implementation keys
            if k_str.lower() in STRIP_INTERNAL_KEYS:
                continue
            clean_dict[k_str] = _sanitize_dict_recursive(v)
        return clean_dict
    elif isinstance(data, list):
        return [_sanitize_dict_recursive(item) for item in data]
    return data


def sanitize_context_for_qa(
    acceptance_spec: Dict[str, Any],
    flow_contracts: List[str],
    public_api_signatures: List[str],
    interface_skeletons: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Strips internal implementation details, builder reasoning, and private variables.

    Returns:
        Sanitized context dictionary containing only public specifications and boundary invariants.
    """
    sanitized_spec = _sanitize_dict_recursive(copy.deepcopy(acceptance_spec))

    # Filter public API signatures: reject private methods starting with '_'
    clean_signatures: List[str] = []
    for sig in public_api_signatures:
        sig_str = sig.strip()
        # Drop private functions like 'def _internal_helper'
        if re.search(r"\bdef\s+_[a-zA-Z0-9_]+", sig_str):
            continue
        # Drop private classes like 'class _PrivateHelper'
        if re.search(r"\bclass\s+_[a-zA-Z0-9_]+", sig_str):
            continue
        clean_signatures.append(sig_str)

    res = {
        "acceptance_spec": sanitized_spec,
        "flow_contracts": list(flow_contracts),
        "public_api_signatures": clean_signatures,
        "sanitized_at_unix_ms": int(time.time() * 1000),
        "is_sanitized": True,
    }
    if interface_skeletons:
        res["interface_skeletons"] = dict(interface_skeletons)
    return res


class QASynthesizer:
    """Independent Adversarial QA Synthesizer coordinating black-box verification."""

    def __init__(self, workspace_root: Optional[str] = None):
        self.role: CognitiveRole = CognitiveRole.ADVERSARIAL_QA_ENGINEER
        self.workspace_root = Path(workspace_root).resolve() if workspace_root else Path.cwd()
        self.qa_reports: Dict[str, ByzantineChaosReport] = {}

    def validate_target(self, target_path: str) -> None:
        """Validates that target_path complies with QA role boundaries."""
        validate_qa_target(target_path)

    def prepare_sanitized_context(
        self,
        acceptance_spec: Dict[str, Any],
        flow_contracts: Optional[List[str]] = None,
        public_api_signatures: Optional[List[str]] = None,
        interface_skeletons: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Sanitizes context before dispatching adversarial test generation."""
        return sanitize_context_for_qa(
            acceptance_spec=acceptance_spec,
            flow_contracts=flow_contracts or [],
            public_api_signatures=public_api_signatures or [],
            interface_skeletons=interface_skeletons,
        )

    def execute_test_suite(
        self,
        test_file_path: str,
        timeout_seconds: float = 30.0,
    ) -> ByzantineChaosReport:
        """Executes a test file as an independent subprocess against live grounded code."""
        validate_qa_target(test_file_path)

        p = Path(test_file_path)
        if not p.is_absolute():
            abs_p = (self.workspace_root / p).resolve()
        else:
            abs_p = p.resolve()

        if not abs_p.exists():
            raise QABoundaryViolation(f"Test file '{test_file_path}' does not physically exist.")

        # Execute test runner in subprocess
        cmd = [sys.executable, "-m", "unittest", str(abs_p)]
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=str(self.workspace_root),
            )
            passed = (res.returncode == 0)
        except subprocess.TimeoutExpired:
            passed = False
        except Exception:
            passed = False

        # Invariant: If passed=True, recovered == injected; if passed=False, recovered < injected
        injected = 1
        recovered = 1 if passed else 0

        target_module = p.stem.replace("test_", "")
        report_id = f"byz_{hashlib.sha256((str(abs_p) + str(time.time())).encode()).hexdigest()[:12]}"

        report = ByzantineChaosReport(
            report_id=report_id,
            target_module=target_module,
            chaos_scenarios_tested=1,
            passed=passed,
            injected_fault_count=injected,
            recovered_fault_count=recovered,
            chaos_seed=42,
            executed_at_unix_ms=int(time.time() * 1000),
        )
        report.validate_invariants()

        self.qa_reports[str(abs_p)] = report
        return report

    def get_qa_reports(self) -> List[ByzantineChaosReport]:
        """Returns all executed QA reports."""
        return list(self.qa_reports.values())
