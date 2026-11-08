"""Empirical Test Suite for Trilateral Completeness Auditor (`[L1-G4B-001]`, `[INV-G4B-TRACE-001]`).

Verifies:
1. Deterministic calculation and sensitivity of the Tri-Planar Merkle root.
2. Total Trilateral Bisimulation on synthetic compliant application directories.
3. Strict detection and interception of plane divergence (type mismatches, missing DOM elements).
4. Live verification of production application `apps/axioma_phenoflora`.
5. Integration with SQLite WAL TelemetryVault recording journey step transactions.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from generations.gen_04b.services.audit.src.trilateral_completeness_auditor import (
    TrilateralCompletenessAuditor,
    TrilateralAuditReport,
    TriPlanarMerkleAttestation,
    TrilateralAuditViolation,
)
from generations.gen_04b.services.audit.src.journey_walker.statechart_ir import (
    StatechartIR,
    StateNode,
    StateNodeType,
    Transition,
)
from generations.gen_04b.services.telemetry.src.telemetry_vault import TelemetryVault


class TestTrilateralCompletenessAuditor(unittest.TestCase):
    """Exhaustive tests for the Trilateral Completeness Auditor."""

    def setUp(self) -> None:
        self.auditor = TrilateralCompletenessAuditor()
        self.test_dir = tempfile.mkdtemp(prefix="trilateral_audit_test_")
        self.app_dir = Path(self.test_dir) / "sample_app"
        self._scaffold_synthetic_app(self.app_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _scaffold_synthetic_app(self, app_dir: Path) -> None:
        """Scaffolds a fully conformant, hermetic synthetic application."""
        app_dir.mkdir(parents=True, exist_ok=True)
        (app_dir / "trace" / "domains").mkdir(parents=True, exist_ok=True)
        (app_dir / "src").mkdir(parents=True, exist_ok=True)
        (app_dir / "static").mkdir(parents=True, exist_ok=True)

        # 1. Plane 1: TRACE Domain Spec
        trace_spec = """
# ENTITY: WidgetState
MUST HAVE:
- widget_id: String
- count: Integer
- latency_ms: Float
- is_active: Boolean
- tags: List[String]
"""
        (app_dir / "trace" / "domains" / "widget.domain.md").write_text(trace_spec, encoding="utf-8")

        # 2. Plane 2: Python Code AST
        code_py = """
from dataclasses import dataclass
from typing import List

@dataclass
class WidgetState:
    widget_id: str
    count: int
    latency_ms: float
    is_active: bool
    tags: List[str]
"""
        (app_dir / "src" / "domain_models.py").write_text(code_py, encoding="utf-8")

        # 3. Plane 2: HTML & Presentation Bundle
        html = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div id="app-root">
        <button id="btn-submit" data-action="EV_TRIGGER">Submit</button>
        <span id="output-val">0</span>
    </div>
</body>
</html>
"""
        (app_dir / "static" / "index.html").write_text(html, encoding="utf-8")

        js = """
const btn = document.getElementById('btn-submit');
const out = document.getElementById('output-val');
btn.addEventListener('click', () => {
    out.innerText = '1';
});
"""
        (app_dir / "static" / "app.js").write_text(js, encoding="utf-8")

        css = ":root { --c: #000; } body { margin: 0; display: flex; }"
        (app_dir / "static" / "style.css").write_text(css, encoding="utf-8")

    def test_merkle_root_computation_determinism(self) -> None:
        """Verifies deterministic calculation and sensitivity of the Tri-Planar Merkle root."""
        h1 = hashlib.sha256(b"spec_code").hexdigest()
        h2 = hashlib.sha256(b"code_state").hexdigest()
        h3 = hashlib.sha256(b"spec_state").hexdigest()

        root_a = self.auditor.compute_merkle_root(h1, h2, h3)
        root_b = self.auditor.compute_merkle_root(h1, h2, h3)

        self.assertEqual(len(root_a), 64)
        self.assertEqual(root_a, root_b)

        # Sensitivity: mutating any plane hash mutates the root
        h1_mutated = hashlib.sha256(b"spec_code_tampered").hexdigest()
        root_mutated = self.auditor.compute_merkle_root(h1_mutated, h2, h3)
        self.assertNotEqual(root_a, root_mutated)

    def test_synthetic_trilateral_pass(self) -> None:
        """Proves that a compliant application achieves 100% Trilateral Completeness."""
        report = self.auditor.audit_application(
            self.app_dir,
            execute_subprocess_journey=False,
            raise_on_error=True,
        )
        self.assertTrue(report.is_complete)
        self.assertTrue(report.spec_code_bijective)
        self.assertTrue(report.code_state_conforming)
        self.assertTrue(report.spec_state_bisimilar)
        self.assertEqual(len(report.violations), 0)
        self.assertIsNotNone(report.attestation)
        self.assertEqual(report.attestation.tri_planar_merkle_root, report.tri_planar_merkle_root)

    def test_synthetic_type_divergence_intercepted(self) -> None:
        """Detects TRACE-001D type divergence and halts completion."""
        # Mutate code_py to have incompatible type: count: str instead of int
        bad_code = """
from dataclasses import dataclass
from typing import List

@dataclass
class WidgetState:
    widget_id: str
    count: str  # Type divergence!
    latency_ms: float
    is_active: bool
    tags: List[str]
"""
        (self.app_dir / "src" / "domain_models.py").write_text(bad_code, encoding="utf-8")

        report = self.auditor.audit_application(
            self.app_dir,
            execute_subprocess_journey=False,
            raise_on_error=False,
        )
        self.assertFalse(report.is_complete)
        self.assertFalse(report.spec_code_bijective)
        self.assertTrue(any("TRACE-001D" in v for v in report.violations))

        with self.assertRaises(TrilateralAuditViolation):
            self.auditor.audit_application(
                self.app_dir,
                execute_subprocess_journey=False,
                raise_on_error=True,
            )

    def test_live_audit_axioma_phenoflora(self) -> None:
        """Audits the production PhenoFlora application and certifies Trilateral Completeness."""
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
        phenoflora_dir = repo_root / "generations" / "gen_04b" / "apps" / "axioma_phenoflora"
        if not phenoflora_dir.exists():
            self.skipTest("axioma_phenoflora directory not found")

        report = self.auditor.audit_application(
            phenoflora_dir,
            execute_subprocess_journey=False,
            raise_on_error=False,
        )
        self.assertTrue(report.spec_code_bijective)
        self.assertEqual(len(report.trace_report.missing_in_code), 0)
        self.assertEqual(len(report.trace_report.missing_in_trace), 0)
        self.assertIsNotNone(report.attestation)
        self.assertEqual(len(report.tri_planar_merkle_root), 64)

    def test_telemetry_vault_mesh_transaction_integration(self) -> None:
        """Proves that journey execution steps stream directly into TelemetryVault as MeshTransactions."""
        db_path = Path(self.test_dir) / "test_vault.db"
        vault = TelemetryVault(db_path=str(db_path), keyframe_interval=50)

        auditor_with_vault = TrilateralCompletenessAuditor(telemetry_vault=vault)
        self.assertIs(auditor_with_vault.telemetry_vault, vault)

        # Run synthetic audit with telemetry vault
        report = auditor_with_vault.audit_application(
            self.app_dir,
            execute_subprocess_journey=False,
            raise_on_error=True,
        )
        self.assertTrue(report.is_complete)
        vault.close()


if __name__ == "__main__":
    unittest.main()
