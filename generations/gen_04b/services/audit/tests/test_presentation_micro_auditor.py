"""Unit & Adversarial Invariant Test Suite for Tier 1 Presentation Micro-Auditor (`[L1-G4B-015]`).

Validates:
1. Valid UI bundles pass with 0 violations and is_certified == True.
2. Interception of missing DOM IDs queried in JS (HERM-UI-001 -> DOMBijectivityViolation).
3. Whitelisted dynamic prefixes and dynamically registered IDs pass bijectivity.
4. Interception of fixed-pixel 600x400 canvas without responsive CSS (HERM-UI-002 -> ResponsiveCanvasViolation).
5. Interception of missing viewport meta tag (HERM-UI-002).
6. Interception of interactive statechart events lacking DOM triggers (HERM-UI-003 -> StatechartDOMBisimulationViolation).
7. Autonomous system events do not require human DOM triggers.
8. Physical audit of production applications: axioma_phenoflora, axioma_canvas, axioma_go.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

AUDIT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = AUDIT_ROOT.parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from generations.gen_04b.services.audit.src.domain_models import (
    DOMBijectivityViolation,
    ResponsiveCanvasViolation,
    StatechartDOMBisimulationViolation,
)
from generations.gen_04b.services.audit.src.presentation_micro_auditor import PresentationMicroAuditor


class TestPresentationMicroAuditor(unittest.TestCase):
    """Exhaustive tests for Tier 1 Presentation Micro-Auditor."""

    def setUp(self) -> None:
        self.auditor = PresentationMicroAuditor()

    # 1. Clean UI bundle passes
    def test_clean_ui_bundle_passes(self) -> None:
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="style.css">
        </head>
        <body>
            <div id="app">
                <canvas id="main-canvas"></canvas>
                <button id="btn-undo" data-action="TRIGGER_UNDO">Undo</button>
            </div>
        </body>
        </html>
        """
        js = """
        const app = document.getElementById('app');
        const canvas = document.querySelector('#main-canvas');
        const undoBtn = document.getElementById('btn-undo');
        undoBtn.addEventListener('click', () => {
            console.log('undo');
        });
        """
        css = """
        :root { --primary: #00ffaa; }
        #app { display: flex; flex-direction: column; width: 100%; }
        #main-canvas { max-width: 100%; aspect-ratio: 16 / 9; }
        """
        report = self.auditor.audit_static_bundle(
            html_content=html,
            js_content=js,
            css_content=css,
            statechart_events=["TRIGGER_UNDO"],
            app_id="test_clean_app",
            allow_raise=True,
        )
        self.assertTrue(report.is_certified)
        self.assertTrue(report.herm_ui_001_bijectivity_pass)
        self.assertTrue(report.herm_ui_002_responsiveness_pass)
        self.assertTrue(report.herm_ui_003_bisimulation_pass)
        self.assertEqual(len(report.unmapped_dom_queries), 0)

    # 2. Catch missing DOM ID (HERM-UI-001)
    def test_catch_missing_dom_id(self) -> None:
        html = """
        <!DOCTYPE html>
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body><div id="present-element"></div></body>
        </html>
        """
        js = """
        const present = document.getElementById('present-element');
        const missing = document.getElementById('nonexistent-id');
        """
        css = ":root { --theme: dark; } div { display: flex; }"

        with self.assertRaises(DOMBijectivityViolation) as ctx:
            self.auditor.audit_static_bundle(
                html_content=html,
                js_content=js,
                css_content=css,
                allow_raise=True,
            )
        self.assertIn("nonexistent-id", str(ctx.exception))

    # 3. Dynamic Prefix Whitelist and dynamically created IDs pass
    def test_dynamic_ids_and_whitelists_pass(self) -> None:
        html = """
        <!DOCTYPE html>
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body><div id="container"></div></body>
        </html>
        """
        js = """
        const container = document.getElementById('container');
        // Dynamic construction via setAttribute
        const newEl = document.createElement('div');
        newEl.setAttribute('id', 'dynamic-inspector');
        // Dynamic assignment via .id
        newEl.id = 'dynamic-card';
        // Queried via whitelisted prefix
        const nodeChip = document.getElementById('node-42');
        const ghost = document.getElementById('ghost-preview');
        const val = document.getElementById('val-metric');
        """
        css = ":root { --c: #fff; } div { display: flex; }"
        report = self.auditor.audit_static_bundle(
            html_content=html,
            js_content=js,
            css_content=css,
            allow_raise=True,
        )
        self.assertTrue(report.herm_ui_001_bijectivity_pass)
        self.assertEqual(len(report.unmapped_dom_queries), 0)

    # 4. Catch fixed-pixel 600x400 canvas without responsive CSS (HERM-UI-002)
    def test_catch_fixed_pixel_canvas(self) -> None:
        html = """
        <!DOCTYPE html>
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body>
            <canvas id="stage" width="600" height="400"></canvas>
        </body>
        </html>
        """
        js = "const stage = document.getElementById('stage');"
        css = "/* Missing max-width, width: 100%, or aspect-ratio */ body { background: #000; }"

        with self.assertRaises(ResponsiveCanvasViolation) as ctx:
            self.auditor.audit_static_bundle(
                html_content=html,
                js_content=js,
                css_content=css,
                allow_raise=True,
            )
        self.assertIn("stage", str(ctx.exception))
        self.assertIn("600x400", str(ctx.exception))

    # 5. Catch missing viewport meta tag (HERM-UI-002)
    def test_catch_missing_viewport_meta(self) -> None:
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>No Viewport Meta</title></head>
        <body><div id="content">Hello</div></body>
        </html>
        """
        js = "const c = document.getElementById('content');"
        css = ":root { --x: 1; } div { display: flex; }"

        with self.assertRaises(ResponsiveCanvasViolation) as ctx:
            self.auditor.audit_static_bundle(
                html_content=html,
                js_content=js,
                css_content=css,
                allow_raise=True,
            )
        self.assertIn("viewport", str(ctx.exception))

    # 6. Catch statechart event without matching DOM trigger (HERM-UI-003)
    def test_catch_missing_statechart_dom_trigger(self) -> None:
        html = """
        <!DOCTYPE html>
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body>
            <button id="btn-undo" data-action="TRIGGER_UNDO">Undo</button>
        </body>
        </html>
        """
        js = "const b = document.getElementById('btn-undo');"
        css = ":root { --c: #000; } button { display: flex; }"

        with self.assertRaises(StatechartDOMBisimulationViolation) as ctx:
            self.auditor.audit_static_bundle(
                html_content=html,
                js_content=js,
                css_content=css,
                statechart_events=["TRIGGER_UNDO", "APPLY_REMEDIATION_UNLINKED"],
                allow_raise=True,
            )
        self.assertIn("APPLY_REMEDIATION_UNLINKED", str(ctx.exception))

    # 7. Autonomous statechart events bypass human trigger requirement
    def test_autonomous_statechart_events_pass(self) -> None:
        html = """
        <!DOCTYPE html>
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body><div id="status">Active</div></body>
        </html>
        """
        js = "const s = document.getElementById('status');"
        css = ":root { --a: 1; } div { display: flex; }"
        report = self.auditor.audit_static_bundle(
            html_content=html,
            js_content=js,
            css_content=css,
            statechart_events=["BOOT", "SOLVER_SAT", "TOKEN_MOVED"],
            allow_raise=True,
        )
        self.assertTrue(report.herm_ui_003_bisimulation_pass)
        self.assertEqual(len(report.bisimulation_violations), 0)

    # 8. Physical Audit of Production Application: axioma_phenoflora
    def test_audit_axioma_phenoflora_static_directory(self) -> None:
        app_path = REPO_ROOT / "generations" / "gen_04b" / "apps" / "axioma_phenoflora"
        if not app_path.exists():
            app_path = REPO_ROOT / "apps" / "axioma_phenoflora"

        self.assertTrue(app_path.exists(), f"axioma_phenoflora not found at {app_path}")
        report = self.auditor.audit_app_directory(
            app_dir=app_path,
            statechart_events=["TRIGGER_UNDO", "EV_SELECT_STRATUM"],
            allow_raise=False,
        )
        self.assertTrue(report.herm_ui_001_bijectivity_pass)
        self.assertTrue(report.herm_ui_002_responsiveness_pass)
        self.assertGreater(report.total_static_ids_in_html, 30)

    # 9. Physical Audit of Production Application: axioma_canvas
    def test_audit_axioma_canvas_static_directory(self) -> None:
        app_path = REPO_ROOT / "generations" / "gen_04b" / "apps" / "axioma_canvas"
        if not app_path.exists():
            app_path = REPO_ROOT / "apps" / "axioma_canvas"

        self.assertTrue(app_path.exists(), f"axioma_canvas not found at {app_path}")
        report = self.auditor.audit_app_directory(
            app_dir=app_path,
            allow_raise=False,
        )
        self.assertTrue(report.herm_ui_001_bijectivity_pass)
        self.assertTrue(report.herm_ui_002_responsiveness_pass)
        self.assertGreater(report.total_static_ids_in_html, 40)

    # 10. Physical Audit of Production Application: axioma_go
    def test_audit_axioma_go_static_directory(self) -> None:
        app_path = REPO_ROOT / "generations" / "gen_04b" / "apps" / "axioma_go"
        if not app_path.exists():
            app_path = REPO_ROOT / "apps" / "axioma_go"

        self.assertTrue(app_path.exists(), f"axioma_go not found at {app_path}")
        report = self.auditor.audit_app_directory(
            app_dir=app_path,
            allow_raise=False,
        )
        self.assertTrue(report.herm_ui_001_bijectivity_pass)
        self.assertTrue(report.herm_ui_002_responsiveness_pass)
        self.assertGreater(report.total_static_ids_in_html, 20)


if __name__ == "__main__":
    unittest.main()
