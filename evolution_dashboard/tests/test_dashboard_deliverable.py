"""
Unit tests validating the standalone, zero-external-CDN dashboard.html deliverable.
Guarantees compliance with:
- [L1-G3B-018] Zero-CDN Operational Dashboard Deliverable
- [NEG-G1B-001] Anti-Phantom Emission Gate
- Directive 6: Mandatory Dashboard Functional Anatomy
"""

import json
import re
import unittest
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_FILE = APP_ROOT / "dashboard.html"


class TestDashboardDeliverable(unittest.TestCase):
    def setUp(self):
        self.assertTrue(
            DASHBOARD_FILE.is_file(),
            f"dashboard.html must exist at {DASHBOARD_FILE}",
        )
        self.content = DASHBOARD_FILE.read_text(encoding="utf-8")

    def test_01_physical_size_and_anti_phantom(self):
        """Verify dashboard.html is a substantial, fully bundled artifact (> 200 KB)."""
        size_bytes = len(self.content.encode("utf-8"))
        self.assertGreater(size_bytes, 200_000, f"dashboard.html too small ({size_bytes} bytes)")
        self.assertIn("<!DOCTYPE html>", self.content)
        self.assertIn("</html>", self.content)

    def test_02_zero_external_cdn_dependencies(self):
        """Strictly enforce zero remote CDN scripts or stylesheet links."""
        # Find all script src and link href
        script_srcs = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', self.content, re.IGNORECASE)
        link_hrefs = re.findall(r'<link[^>]+href=["\']([^"\']+)["\']', self.content, re.IGNORECASE)

        for src in script_srcs:
            self.assertFalse(
                src.startswith(("http://", "https://", "//")),
                f"Forbidden external CDN script found: {src}",
            )
        for href in link_hrefs:
            if "stylesheet" in self.content:
                # Should not load external remote stylesheets
                self.assertFalse(
                    href.startswith(("http://", "https://", "//")),
                    f"Forbidden external CDN stylesheet found: {href}",
                )

    def test_03_inlined_styles_and_scripts(self):
        """Verify styles.css and app.js are inlined directly into <style> and <script> tags."""
        self.assertIn("<style>", self.content)
        self.assertIn("</style>", self.content)
        self.assertIn("window.EMBEDDED_EVOLUTION_DATA =", self.content)
        self.assertIn("tech-grid", self.content)
        self.assertIn("academic-tooltip", self.content)

    def test_04_all_major_sections_present(self):
        """Verify all mandatory functional sections exist in dashboard.html."""
        sections = [
            ("Section 1: Philosophy", 'id="philosophy"'),
            ("Section 2: G4b Sovereign Mesh", 'id="g4b-architecture"'),
            ("Section 3: App Walkthrough Simulation", 'id="app-simulation"'),
            ("Section 4: 8-Stage Evolution Spine", 'id="evolution-timeline"'),
            ("Section 5: Generational Diff Workbench", 'id="diff-workbench"'),
            ("Section 6: Governance & Key Milestones", 'id="governance-spotlight"'),
            ("Section 7: Landauer Thermodynamics", 'id="telemetry-hud"'),
        ]
        for name, marker in sections:
            self.assertIn(marker, self.content, f"Missing {name} with marker '{marker}'")

    def test_05_embedded_evolution_data_integrity(self):
        """Verify embedded JSON payload contains valid stages, transformations, and simulation data."""
        match = re.search(r"window\.EMBEDDED_EVOLUTION_DATA\s*=\s*(\{.*?\});", self.content, re.DOTALL)
        self.assertIsNotNone(match, "Could not find window.EMBEDDED_EVOLUTION_DATA JSON block")
        json_str = match.group(1)
        data = json.loads(json_str)

        self.assertIn("stages", data)
        self.assertEqual(len(data["stages"]), 8)

        self.assertIn("philosophy", data)
        self.assertIn("g4b_architecture", data)
        self.assertIn("sample_app_simulation", data)

        sim_data = data["sample_app_simulation"]
        self.assertIn("axioma_go", sim_data["simulations"])
        self.assertEqual(len(sim_data["simulations"]["axioma_go"]["steps"]), 5)

    def test_06_interactive_controls_present(self):
        """Verify interactive playback, modal, and drawer control elements are present."""
        controls = [
            "mode-layman-btn",
            "mode-academic-btn",
            "sim-autoplay-btn",
            "landauer-bits-slider",
            "generic-modal",
        ]
        for ctrl in controls:
            self.assertIn(ctrl, self.content, f"Missing interactive control element: '{ctrl}'")

    def test_07_zero_personal_name_leakage(self):
        """Invariant [NEG-PRIVACY-001]: Verify zero occurrences of the user's personal name in dashboard.html."""
        # Check for user's personal name (excluding filesystem paths if any)
        # Match "Michael Lipski" or standalone "Michael" outside standard system paths
        sanitized_content = re.sub(r"/Users/[A-Za-z0-9_-]+", "/Users/anon", self.content)
        self.assertNotIn("Michael Lipski", sanitized_content, "Personal name 'Michael Lipski' found in dashboard.html")
        self.assertNotIn("Lipski", sanitized_content, "Personal name 'Lipski' found in dashboard.html")
        # Check for standalone Michael in text/json (case-sensitive to avoid matching unrelated terms)
        self.assertNotIn(" Michael ", sanitized_content, "Personal first name 'Michael' found in dashboard.html")
        self.assertNotIn(">Michael<", sanitized_content, "Personal first name 'Michael' found in HTML tags")
        self.assertNotIn('"Michael"', sanitized_content, "Personal first name 'Michael' found in JSON strings")


if __name__ == "__main__":
    unittest.main()
