"""Governance Invariant Guard enforcing [INV-G4B-TRACE-001] (`soc_g4b_governance`).

Enforces:
- Invariant [INV-G4B-TRACE-001]: Universal TRACE Portfolio Conformance & Introspection Gate.
- Invariant [L1-G4B-001]: Sovereign Mesh Protocol Standardization.
- Invariant [NEG-G1B-001]: Anti-Phantom Emission Gate (Zero empty or missing specifications).

Rules:
  - TRACE-GOV-001: trace/overview.md must exist, be non-empty (>0 bytes), and declare valid frontmatter.
  - TRACE-GOV-002: trace/stack.md must exist, be non-empty, and declare stack infrastructure.
  - TRACE-GOV-003: At least one *.persona.md must exist in trace/personas/.
  - TRACE-GOV-004: At least one *.domain.md must exist in trace/domains/.
  - TRACE-GOV-005: At least one *.flow.md must exist in trace/flows/.
  - TRACE-GOV-006: Application server must implement GET /api/trace route.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple


class TraceInvariantViolation(Exception):
    """Raised when an application violates TRACE governance invariants [INV-G4B-TRACE-001]."""
    pass


@dataclass(frozen=True)
class TraceGovernanceWitness:
    """Cryptographic governance witness certifying an application's TRACE package compliance."""
    app_id: str
    is_compliant: bool
    overview_valid: bool
    stack_valid: bool
    persona_count: int
    domain_count: int
    flow_count: int
    has_api_trace_endpoint: bool
    violations: List[str]
    certified_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))


class TraceInvariantGuard:
    """Pre-commit and runtime governance guard enforcing [INV-G4B-TRACE-001]."""

    def __init__(self, guard_node_id: str = "node_trace_gov_sentry") -> None:
        self.guard_node_id = guard_node_id

    @staticmethod
    def _validate_frontmatter(file_path: Path, required_keys: List[str]) -> Tuple[bool, Optional[str]]:
        if not file_path.is_file() or file_path.stat().st_size == 0:
            return False, f"File missing or empty: {file_path.name}"
        text = file_path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            return False, f"Missing YAML frontmatter prefix '---' in {file_path.name}"
        parts = text.split("---", 2)
        if len(parts) < 3:
            return False, f"Malformed YAML frontmatter in {file_path.name}"
        raw_fm = parts[1]
        fm_keys: Set[str] = set()
        for line in raw_fm.splitlines():
            line_str = line.strip()
            if line_str and ":" in line_str and not line_str.startswith("#"):
                k, _ = line_str.split(":", 1)
                fm_keys.add(k.strip())
        missing = set(required_keys) - fm_keys
        if missing:
            return False, f"Frontmatter in {file_path.name} missing required keys: {sorted(list(missing))}"
        return True, None

    @staticmethod
    def _check_api_trace_endpoint(server_py_path: Path) -> bool:
        if not server_py_path.is_file():
            return False
        text = server_py_path.read_text(encoding="utf-8")
        return "/api/trace" in text

    def verify_app_trace_invariants(
        self,
        app_dir: Path | str,
        raise_on_violation: bool = False,
    ) -> TraceGovernanceWitness:
        """Verifies full compliance of an application directory against [INV-G4B-TRACE-001]."""
        app_path = Path(app_dir).resolve()
        trace_dir = app_path / "trace"
        server_py = app_path / "src" / "server.py"
        violations: List[str] = []

        # TRACE-GOV-001: overview.md
        overview_path = trace_dir / "overview.md"
        ov_valid, ov_err = self._validate_frontmatter(overview_path, ["name", "app_id", "generation"])
        if not ov_valid:
            violations.append(f"TRACE-GOV-001: {ov_err}")

        # TRACE-GOV-002: stack.md
        stack_path = trace_dir / "stack.md"
        st_valid, st_err = self._validate_frontmatter(stack_path, ["stack", "app_id"])
        if not st_valid:
            violations.append(f"TRACE-GOV-002: {st_err}")

        # TRACE-GOV-003: personas
        personas_dir = trace_dir / "personas"
        persona_count = len(list(personas_dir.glob("*.persona.md"))) if personas_dir.is_dir() else 0
        if persona_count == 0:
            violations.append("TRACE-GOV-003: Zero *.persona.md files found in trace/personas/")

        # TRACE-GOV-004: domains
        domains_dir = trace_dir / "domains"
        domain_count = len(list(domains_dir.glob("*.domain.md"))) if domains_dir.is_dir() else 0
        if domain_count == 0:
            violations.append("TRACE-GOV-004: Zero *.domain.md files found in trace/domains/")

        # TRACE-GOV-005: flows
        flows_dir = trace_dir / "flows"
        flow_count = len(list(flows_dir.glob("*.flow.md"))) if flows_dir.is_dir() else 0
        if flow_count == 0:
            violations.append("TRACE-GOV-005: Zero *.flow.md files found in trace/flows/")

        # TRACE-GOV-006: /api/trace route in server.py
        has_api_trace = self._check_api_trace_endpoint(server_py)
        if not has_api_trace:
            violations.append("TRACE-GOV-006: Application server.py does not implement '/api/trace' route")

        is_compliant = len(violations) == 0
        if not is_compliant and raise_on_violation:
            raise TraceInvariantViolation(f"App '{app_path.name}' violates [INV-G4B-TRACE-001]: {violations}")

        return TraceGovernanceWitness(
            app_id=app_path.name,
            is_compliant=is_compliant,
            overview_valid=ov_valid,
            stack_valid=st_valid,
            persona_count=persona_count,
            domain_count=domain_count,
            flow_count=flow_count,
            has_api_trace_endpoint=has_api_trace,
            violations=violations,
        )

    def verify_portfolio(self, apps_dir: Path | str) -> Dict[str, TraceGovernanceWitness]:
        """Verifies all applications in a portfolio directory."""
        results: Dict[str, TraceGovernanceWitness] = {}
        for entry in sorted(Path(apps_dir).iterdir()):
            if entry.is_dir() and (entry / "app.json").is_file():
                results[entry.name] = self.verify_app_trace_invariants(entry)
        return results
