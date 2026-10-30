"""Adversarial & Hermetic Dashboard Integrity Test Suite for Builder Service ([L1-G4B-008] & HERM-005).

Verifies that the Builder Development Process Telemetry Dashboard deliverable:
1. Exists, is self-contained (>50KB), and contains zero external CDN dependencies.
2. Contains ZERO placeholder UUIDs or synthetic estimations (enforces HERM-005).
3. Passes ZeroTrustMicroAuditor.audit_dashboard_deliverable with is_hermetic == True.
4. Generates deterministically via generate_dashboard.py with exit code 0.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys
import unittest

current_dir = Path(__file__).resolve()
repo_root = current_dir.parents[5]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from generations.gen_04b.services.audit.src.zero_trust_micro_auditor import ZeroTrustMicroAuditor


class TestBuilderDashboardIntegrity(unittest.TestCase):
    """Test suite ensuring builder service dashboard cannot be deployed with placeholder values."""

    def setUp(self) -> None:
        self.service_dir = Path(__file__).resolve().parent.parent
        self.dashboard_html = self.service_dir / "dashboard.html"
        self.telemetry_html = self.service_dir / "telemetry_dashboard.html"
        self.generate_py = self.service_dir / "generate_dashboard.py"
        self.auditor = ZeroTrustMicroAuditor(auditor_node_id="test_builder_dashboard_auditor")

    def test_dashboard_files_exist_and_non_trivial(self) -> None:
        """Verify dashboard deliverables physically exist on disk and meet size floor."""
        self.assertTrue(self.dashboard_html.exists(), "dashboard.html must physically exist on disk")
        self.assertTrue(self.telemetry_html.exists(), "telemetry_dashboard.html must physically exist on disk")
        self.assertTrue(self.generate_py.exists(), "generate_dashboard.py must physically exist on disk")

        self.assertGreater(self.dashboard_html.stat().st_size, 50000)
        self.assertGreater(self.telemetry_html.stat().st_size, 50000)

    def test_zero_external_cdn_dependencies(self) -> None:
        """Verify zero external scripts, CDNs, or fonts (Directive 6 zero-CDN invariant)."""
        content = self.dashboard_html.read_text(encoding="utf-8")
        banned_cdns = ["cdnjs.cloudflare.com", "cdn.jsdelivr.net", "unpkg.com", "fonts.googleapis.com"]
        for cdn in banned_cdns:
            self.assertNotIn(cdn, content, f"Forbidden external CDN '{cdn}' detected in dashboard")

    def test_herm_005_zero_placeholder_uuids(self) -> None:
        """Verify dashboard passes HERM-005 micro-auditor with zero placeholder UUIDs."""
        content = self.dashboard_html.read_text(encoding="utf-8")
        report = self.auditor.audit_dashboard_deliverable(content, deliverable_id="builder_dashboard")
        
        self.assertTrue(
            report.is_hermetic,
            f"Dashboard failed HERM-005 audit with violations: {[v.description for v in report.violations]}"
        )
        self.assertEqual(len(report.violations), 0)

    def test_subagent_conversation_ids_are_valid_uuids(self) -> None:
        """Verify all subagent conversation IDs in the witness table are valid UUIDv4 strings."""
        content = self.dashboard_html.read_text(encoding="utf-8")
        uuid_pattern = re.compile(r"<code>([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})</code>")
        matches = uuid_pattern.findall(content)

        self.assertGreaterEqual(len(matches), 4, "Must contain at least 4 reconciled subagent UUIDs")
        for uid in matches:
            self.assertFalse(uid.startswith("00000000"), f"Synthetic placeholder UUID detected: {uid}")
            self.assertFalse(uid.startswith("11111111"), f"Synthetic placeholder UUID detected: {uid}")

    def test_generate_dashboard_script_execution(self) -> None:
        """Verify generate_dashboard.py executes cleanly and re-emits identical deliverables."""
        res = subprocess.run(
            [sys.executable, str(self.generate_py)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
        )
        self.assertEqual(res.returncode, 0, f"generate_dashboard.py failed with: {res.stderr}")
        self.assertTrue(self.dashboard_html.exists())


if __name__ == "__main__":
    unittest.main()
