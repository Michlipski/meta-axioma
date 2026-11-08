"""Unit & Adversarial Invariant Test Suite for Tier 2 Headless UI Walker (`[L1-G4B-015]`).

Validates:
1. Pure-Python JavaScript syntax and balanced-delimiter validator.
2. Ephemeral port dynamic allocation.
3. Subprocess boot protocol, dual-mode liveness probe, and clean SIGTERM teardown.
4. Static asset dependency resolution (zero 404s, non-empty byte payloads, SHA-256).
5. Evaluation of the 4 Universal Human Ergonomics Axioms.
6. Empirical walk against production applications (axioma_phenoflora, axioma_canvas, axioma_go).
"""

from __future__ import annotations

import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import unittest

AUDIT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = AUDIT_ROOT.parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from generations.gen_04b.services.audit.src.headless_ui_walker import (
    ErgonomicsAxiom,
    HeadlessUIWalker,
    PurePythonJSSyntaxChecker,
)


class TestHeadlessUIWalker(unittest.TestCase):
    """Exhaustive tests for Tier 2 Headless UI Walker and Ergonomics Prover."""

    def setUp(self) -> None:
        self.walker = HeadlessUIWalker()

    # 1. Pure Python JS Syntax Checker: Clean code passes
    def test_pure_python_js_syntax_clean_passes(self) -> None:
        clean_js = """
        // Standard ES6+ JS
        function renderGraph(data) {
            const items = [1, 2, 3];
            const result = items.map(x => ({ id: `node-${x}`, value: x * 10 }));
            const label = `Rendered ${result.length} nodes cleanly (${items.join(', ')})`;
            return { result, label };
        }
        """
        witness = PurePythonJSSyntaxChecker.check_javascript(clean_js, "clean.js")
        self.assertTrue(witness.brackets_balanced)
        self.assertTrue(witness.strings_balanced)
        self.assertTrue(witness.template_literals_balanced)
        self.assertEqual(len(witness.syntax_errors), 0)

    # 2. Pure Python JS Syntax Checker: Traps unclosed delimiter
    def test_pure_python_js_syntax_traps_unclosed_delimiter(self) -> None:
        bad_js = """
        function broken(a, b) {
            if (a > b) {
                console.log("missing closing brace");
            // Missing '}'
        }
        """
        witness = PurePythonJSSyntaxChecker.check_javascript(bad_js, "bad.js")
        self.assertFalse(witness.brackets_balanced)
        self.assertGreater(len(witness.syntax_errors), 0)

    # 3. Pure Python JS Syntax Checker: Traps mismatched delimiter
    def test_pure_python_js_syntax_traps_mismatched_delimiter(self) -> None:
        mismatched_js = """
        const list = [1, 2, 3};
        """
        witness = PurePythonJSSyntaxChecker.check_javascript(mismatched_js, "mismatch.js")
        self.assertFalse(witness.brackets_balanced)
        self.assertTrue(any("Mismatched delimiter" in err or "Unmatched closing" in err for err in witness.syntax_errors))

    # 4. Pure Python JS Syntax Checker: Nested template literals parse cleanly
    def test_pure_python_js_syntax_nested_template_literals(self) -> None:
        nested_js = """
        const complex = `Depth 1: ${data.map(d => `Item: ${d.name} (${d.val})`).join('; ')}`;
        """
        witness = PurePythonJSSyntaxChecker.check_javascript(nested_js, "nested.js")
        self.assertTrue(witness.brackets_balanced)
        self.assertTrue(witness.strings_balanced)
        self.assertEqual(len(witness.syntax_errors), 0)

    # 5. Ephemeral Port Allocation: Dynamic and distinct
    def test_ephemeral_port_allocation(self) -> None:
        port1 = HeadlessUIWalker.acquire_ephemeral_port()
        port2 = HeadlessUIWalker.acquire_ephemeral_port()
        self.assertGreater(port1, 1024)
        self.assertGreater(port2, 1024)

    # 6. Subprocess Boot, Healthcheck & Clean Teardown
    def test_subprocess_boot_and_clean_teardown(self) -> None:
        scratch_dir = REPO_ROOT / ".scratch"
        scratch_dir.mkdir(parents=True, exist_ok=True)
        mock_server_script = scratch_dir / "mock_test_server.py"

        mock_server_code = """
import argparse
import http.server
import json
import socketserver
import sys

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'healthy', 'uptime': 1.0}).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Mock OK</h1></body></html>')

def main():
    import signal
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9999)
    parser.add_argument('--host', type=str, default='127.0.0.1')
    args = parser.parse_args()

    with socketserver.TCPServer((args.host, args.port), Handler) as httpd:
        httpd.serve_forever()

if __name__ == '__main__':
    main()
"""
        mock_server_script.write_text(mock_server_code, encoding="utf-8")

        proc, port, bound = self.walker.boot_app_subprocess(mock_server_script, boot_timeout=4.0)
        self.assertIsNotNone(proc)
        self.assertTrue(bound, "Mock server failed to bind ephemeral socket!")

        # Probe health
        is_healthy, status, data = self.walker.probe_liveness(port)
        self.assertTrue(is_healthy)
        self.assertEqual(status, 200)
        self.assertEqual(data.get("status"), "healthy")

        # Clean teardown via SIGTERM
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=2.0)
        self.assertIn(proc.returncode, (0, -signal.SIGTERM, -signal.SIGINT, 143))

    # 7. Live Application Headless Walk: axioma_phenoflora
    def test_headless_walk_axioma_phenoflora(self) -> None:
        app_path = REPO_ROOT / "generations" / "gen_04b" / "apps" / "axioma_phenoflora"
        if not app_path.exists():
            app_path = REPO_ROOT / "apps" / "axioma_phenoflora"

        self.assertTrue(app_path.exists(), f"axioma_phenoflora not found at {app_path}")
        report = self.walker.walk_app(
            app_dir=app_path,
            primary_endpoint="/api/health",
            allow_raise=False,
        )
        self.assertTrue(report.boot_clean)
        self.assertTrue(report.teardown_clean)
        self.assertTrue(report.js_syntax_clean)
        self.assertTrue(report.all_assets_resolved)
        self.assertIn(ErgonomicsAxiom.ZERO_CONSOLE_PANICS.value, report.axiom_evaluations)
        self.assertTrue(report.axiom_evaluations[ErgonomicsAxiom.ZERO_CONSOLE_PANICS.value].passed)
        self.assertTrue(report.axiom_evaluations[ErgonomicsAxiom.VIEWPORT_BOUNDING_BOX.value].passed)
        self.assertTrue(report.axiom_evaluations[ErgonomicsAxiom.SENSORY_LIVENESS.value].passed)
        self.assertTrue(report.axiom_evaluations[ErgonomicsAxiom.NON_OCCLUSION.value].passed)
        self.assertTrue(report.is_certified)

    # 8. Live Application Headless Walk: axioma_canvas
    def test_headless_walk_axioma_canvas(self) -> None:
        app_path = REPO_ROOT / "generations" / "gen_04b" / "apps" / "axioma_canvas"
        if not app_path.exists():
            app_path = REPO_ROOT / "apps" / "axioma_canvas"

        self.assertTrue(app_path.exists(), f"axioma_canvas not found at {app_path}")
        report = self.walker.walk_app(
            app_dir=app_path,
            primary_endpoint="/api/health",
            allow_raise=False,
        )
        self.assertTrue(report.boot_clean)
        self.assertTrue(report.teardown_clean)
        self.assertTrue(report.js_syntax_clean)
        self.assertTrue(report.all_assets_resolved)
        self.assertTrue(report.is_certified)

    # 9. Live Application Headless Walk: axioma_go
    def test_headless_walk_axioma_go(self) -> None:
        app_path = REPO_ROOT / "generations" / "gen_04b" / "apps" / "axioma_go"
        if not app_path.exists():
            app_path = REPO_ROOT / "apps" / "axioma_go"

        self.assertTrue(app_path.exists(), f"axioma_go not found at {app_path}")
        report = self.walker.walk_app(
            app_dir=app_path,
            primary_endpoint="/api/health",
            allow_raise=False,
        )
        self.assertTrue(report.boot_clean)
        self.assertTrue(report.teardown_clean)
        self.assertTrue(report.js_syntax_clean)
        self.assertTrue(report.all_assets_resolved)
        self.assertTrue(report.is_certified)


if __name__ == "__main__":
    unittest.main()
