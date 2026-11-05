"""Empirical Test Suite for Governance Invariant Guard [INV-G4B-TRACE-001].

Enforces:
- [INV-G4B-TRACE-001]: Universal TRACE Portfolio Conformance & Introspection Gate.
- [NEG-G1B-001]: Anti-Phantom Emission Gate.
"""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from generations.gen_04b.services.governance.src.trace_invariant_guard import (
    TraceInvariantGuard,
    TraceInvariantViolation,
)


class TestTraceInvariantGuard(unittest.TestCase):
    """Verifies that TraceInvariantGuard correctly certifies or rejects applications."""

    def setUp(self) -> None:
        self.guard = TraceInvariantGuard()
        self.repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent

    def test_certifies_all_five_gen04b_apps(self) -> None:
        """Verifies that all 5 production apps in gen_04b achieve 100% compliance."""
        apps_root = self.repo_root / "generations" / "gen_04b" / "apps"
        target_apps = [
            "axioma_phenoflora",
            "axioma_canvas",
            "axioma_consensus",
            "axioma_crucible",
            "axioma_go",
        ]
        portfolio_results = self.guard.verify_portfolio(apps_root)
        for app_name in target_apps:
            self.assertIn(app_name, portfolio_results, f"App {app_name} missing from portfolio scan")
            witness = portfolio_results[app_name]
            self.assertTrue(
                witness.is_compliant,
                f"App {app_name} failed [INV-G4B-TRACE-001]! Violations: {witness.violations}"
            )
            self.assertTrue(witness.overview_valid)
            self.assertTrue(witness.stack_valid)
            self.assertGreaterEqual(witness.persona_count, 1)
            self.assertGreaterEqual(witness.domain_count, 1)
            self.assertGreaterEqual(witness.flow_count, 1)
            self.assertTrue(witness.has_api_trace_endpoint)

    def test_rejects_missing_overview(self) -> None:
        """Rejects app if trace/overview.md is missing or lacks required keys."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "app.json").write_text("{}", encoding="utf-8")
            (tmp_path / "trace").mkdir()
            (tmp_path / "src").mkdir()
            (tmp_path / "src" / "server.py").write_text("# route /api/trace", encoding="utf-8")

            witness = self.guard.verify_app_trace_invariants(tmp_path)
            self.assertFalse(witness.is_compliant)
            self.assertTrue(any("TRACE-GOV-001" in v for v in witness.violations))

            with self.assertRaises(TraceInvariantViolation):
                self.guard.verify_app_trace_invariants(tmp_path, raise_on_violation=True)

    def test_rejects_missing_api_trace_endpoint(self) -> None:
        """Rejects app if server.py does not define /api/trace route."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "app.json").write_text("{}", encoding="utf-8")
            t_dir = tmp_path / "trace"
            t_dir.mkdir()
            (t_dir / "overview.md").write_text("---\nname: T\napp_id: t\ngeneration: gen_04b\n---\n", encoding="utf-8")
            (t_dir / "stack.md").write_text("---\nstack: S\napp_id: t\n---\n", encoding="utf-8")
            (t_dir / "personas").mkdir()
            (t_dir / "personas" / "a.persona.md").write_text("# A", encoding="utf-8")
            (t_dir / "domains").mkdir()
            (t_dir / "domains" / "a.domain.md").write_text("# A", encoding="utf-8")
            (t_dir / "flows").mkdir()
            (t_dir / "flows" / "a.flow.md").write_text("# A", encoding="utf-8")
            (tmp_path / "src").mkdir()
            (tmp_path / "src" / "server.py").write_text("# No trace endpoint here", encoding="utf-8")

            witness = self.guard.verify_app_trace_invariants(tmp_path)
            self.assertFalse(witness.is_compliant)
            self.assertTrue(any("TRACE-GOV-006" in v for v in witness.violations))


if __name__ == "__main__":
    unittest.main()
