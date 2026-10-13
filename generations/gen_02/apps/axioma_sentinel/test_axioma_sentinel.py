"""Full-Surface Test Suite for Axioma Sentinel (System 07).

Enforcing Invariant NEG-G2-003:
- Tests all user-exposed execution modes (CLI, Core Engine, In-Memory HTTP REST API)
- Asserts domain invariants: zero blast leakage, functorial reversibility,
  capability token integrity, and Landauer dissipation bounds.
"""

import io
import json
import time
import unittest

from g2_compiler.types import CapabilitySecurityFault
from .core import SentinelCoreEngine
from .server import SentinelRequestHandler
from .types import ActionStatus


class InMemoryHttpHarness:
    """Zero-network, sandbox-safe HTTP handler harness."""

    @staticmethod
    def call(handler_class, engine, html_content: str, method: str, path: str, body: bytes = b"", headers: dict = None):
        handler = handler_class.__new__(handler_class)
        handler.engine = engine
        handler.html_content = html_content
        handler.rfile = io.BytesIO(body)
        handler.wfile = io.BytesIO()
        handler.path = path
        handler.command = method
        handler.request_version = "HTTP/1.1"
        handler.headers = headers or {}
        if body and "Content-Length" not in handler.headers:
            handler.headers["Content-Length"] = str(len(body))

        handler._response_code = 200
        handler._response_headers = {}

        def mock_send_response(code, msg=None):
            handler._response_code = code

        def mock_send_header(key, val):
            handler._response_headers[key] = val

        def mock_end_headers():
            pass

        handler.send_response = mock_send_response
        handler.send_header = mock_send_header
        handler.end_headers = mock_end_headers

        if method == "GET":
            handler.do_GET()
        elif method == "POST":
            handler.do_POST()

        return handler._response_code, handler._response_headers, handler.wfile.getvalue()


class TestAxiomaSentinel(unittest.TestCase):
    """Full-flow verification of Axioma Sentinel."""

    def setUp(self) -> None:
        self.engine = SentinelCoreEngine()
        self.test_html = "<html>Axioma Sentinel Test Dashboard</html>"

    def test_token_authority_and_zero_trust_scoping(self) -> None:
        """Verifies L1-G2-004: Introspectable capability scoping & ambient rejection."""
        tokens = self.engine.capability_authority.export_tokens_summary()
        architect_tok = next(t for t in tokens if t["persona"] == "AI_Architect")
        token_id = architect_tok["token_id"]

        # 1. Permitted action succeeds
        action = self.engine.dispatch_agent_action(
            tool_name="read_telemetry",
            parameters={"filter": "live"},
            token_id=token_id,
        )
        self.assertEqual(action.status, ActionStatus.EXECUTED)
        self.assertTrue(len(action.witness_hash) > 0)

        # 2. Unauthorized action fails with CapabilitySecurityFault
        with self.assertRaises(CapabilitySecurityFault):
            self.engine.dispatch_agent_action(
                tool_name="unauthorized_kernel_mutation",
                parameters={},
                token_id=token_id,
            )

        # 3. Ambient execution (no token) strictly fails
        with self.assertRaises(CapabilitySecurityFault):
            self.engine.dispatch_agent_action(
                tool_name="read_telemetry",
                parameters={},
                token_id=None,
            )

    def test_enclave_3_pass_auto_healing_and_zero_leakage(self) -> None:
        """Verifies L1-G2-002: Ephemeral 3-pass self-healing with zero blast leakage."""
        tokens = self.engine.capability_authority.export_tokens_summary()
        architect_tok = next(t for t in tokens if t["persona"] == "AI_Architect")

        # Initial state snapshot
        initial_hash = self.engine._hash_state(self.engine._workspace_state)

        # Dispatch with simulated fault: parameter 'count' is string instead of int
        action = self.engine.dispatch_agent_action(
            tool_name="simulate_breach",
            parameters={"count": "99", "target_key": "healed_node_status"},
            token_id=architect_tok["token_id"],
            simulate_fault=True,
        )

        # Must heal in enclave
        self.assertEqual(action.status, ActionStatus.HEALED)
        self.assertGreater(len(action.remediation_notes), 0)

        # Check incident ledger
        incidents = self.engine.enclave_supervisor.get_incidents_history()
        self.assertGreater(len(incidents), 0)
        self.assertTrue(incidents[0].healed)
        self.assertFalse(incidents[0].blast_leakage_detected, "Domain Invariant: Blast leakage must be FALSE")

    def test_functorial_reversibility_1_click_rollback(self) -> None:
        """Verifies L1-G2-001 & L1-G2-003: 1-Click Rollback restores exact state hash."""
        tokens = self.engine.capability_authority.export_tokens_summary()
        architect_tok = next(t for t in tokens if t["persona"] == "AI_Architect")

        # Record pre-mutation hash
        pre_hash = self.engine._hash_state(self.engine._workspace_state)

        # Perform state mutation
        self.engine.dispatch_agent_action(
            tool_name="inspect_memory",
            parameters={"target_key": "accidental_mutation", "target_value": "CORRUPT"},
            token_id=architect_tok["token_id"],
        )
        post_hash = self.engine._hash_state(self.engine._workspace_state)
        self.assertNotEqual(pre_hash, post_hash)

        # Execute 1-Click Functorial Rollback
        rollback_res = self.engine.rollback_to_last_checkpoint()
        self.assertTrue(rollback_res["success"])

        # Invariant check: Restored state hash matches pristine pre-mutation hash exactly!
        restored_hash = self.engine._hash_state(self.engine._workspace_state)
        self.assertEqual(pre_hash, restored_hash, "Rollback state hash must equal pre-mutation state hash")

    def test_landauer_thermodynamic_accounting(self) -> None:
        """Verifies L1-008: Bit erasure dissipation accounting against Landauer limit."""
        tokens = self.engine.capability_authority.export_tokens_summary()
        tok = tokens[0]["token_id"]

        action = self.engine.dispatch_agent_action(
            tool_name="read_telemetry",
            parameters={"query": "active", "depth": 1},
            token_id=tok,
        )

        self.assertGreater(action.erased_bits, 0)
        self.assertGreater(action.dissipated_joules, 0.0)
        self.assertLess(action.dissipated_joules, 1e-18, "Dissipated energy must remain in micro/nano joule regime")

    def test_http_rest_api_surface(self) -> None:
        """Verifies full HTTP API surface using sandbox-isolated in-memory harness."""
        # 1. GET / (Dashboard HTML)
        code, headers, body = InMemoryHttpHarness.call(
            SentinelRequestHandler, self.engine, self.test_html, "GET", "/"
        )
        self.assertEqual(code, 200)
        self.assertIn("text/html", headers.get("Content-Type", ""))
        self.assertIn("Axioma Sentinel Test Dashboard", body.decode("utf-8"))

        # 2. GET /api/state
        code, headers, body = InMemoryHttpHarness.call(
            SentinelRequestHandler, self.engine, self.test_html, "GET", "/api/state"
        )
        self.assertEqual(code, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertIn("workspace_state", data)
        self.assertIn("tokens", data)
        self.assertIn("timeline", data)

        # 3. POST /api/action
        tokens = self.engine.capability_authority.export_tokens_summary()
        architect_tok = next(t for t in tokens if t["persona"] == "AI_Architect")
        tok_id = architect_tok["token_id"]

        post_body = json.dumps({
            "tool_name": "read_telemetry",
            "parameters": {"test_query": "live"},
            "token_id": tok_id,
        }).encode("utf-8")
        code, headers, body = InMemoryHttpHarness.call(
            SentinelRequestHandler, self.engine, self.test_html, "POST", "/api/action", body=post_body
        )
        self.assertEqual(code, 200)
        res = json.loads(body.decode("utf-8"))
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "EXECUTED")

        # 4. POST /api/simulate-breach
        breach_body = json.dumps({"token_id": tok_id}).encode("utf-8")
        code, headers, body = InMemoryHttpHarness.call(
            SentinelRequestHandler, self.engine, self.test_html, "POST", "/api/simulate-breach", body=breach_body
        )
        self.assertEqual(code, 200)
        res = json.loads(body.decode("utf-8"))
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "HEALED")

        # 5. POST /api/rollback
        code, headers, body = InMemoryHttpHarness.call(
            SentinelRequestHandler, self.engine, self.test_html, "POST", "/api/rollback", body=b"{}"
        )
        self.assertEqual(code, 200)
        res = json.loads(body.decode("utf-8"))
        self.assertTrue(res["success"])

        # 6. POST /api/token/issue
        issue_body = json.dumps({
            "persona": "WorkerDrone",
            "actions": ["read_telemetry", "sync_state"],
        }).encode("utf-8")
        code, headers, body = InMemoryHttpHarness.call(
            SentinelRequestHandler, self.engine, self.test_html, "POST", "/api/token/issue", body=issue_body
        )
        self.assertEqual(code, 200)
        res = json.loads(body.decode("utf-8"))
        self.assertTrue(res["success"])
        self.assertEqual(res["persona"], "WorkerDrone")

        # 7. 404 for unknown endpoint
        code, headers, body = InMemoryHttpHarness.call(
            SentinelRequestHandler, self.engine, self.test_html, "GET", "/api/nonexistent"
        )
        self.assertEqual(code, 404)

        # 8. GET /api/phenomenology
        code, headers, body = InMemoryHttpHarness.call(
            SentinelRequestHandler, self.engine, self.test_html, "GET", "/api/phenomenology"
        )
        self.assertEqual(code, 200)
        phenom_data = json.loads(body.decode("utf-8"))
        self.assertIn("current_attunement", phenom_data)
        self.assertIn("average_transparency_score", phenom_data)

        # 9. POST /api/phenomenology/interaction
        inter_payload = json.dumps({
            "tool_name": "inspect_memory",
            "dwell_seconds": 1.5,
            "undo_count": 0,
        }).encode("utf-8")
        code, headers, body = InMemoryHttpHarness.call(
            SentinelRequestHandler, self.engine, self.test_html, "POST", "/api/phenomenology/interaction", body=inter_payload
        )
        self.assertEqual(code, 200)
        res = json.loads(body.decode("utf-8"))
        self.assertTrue(res["success"])
        self.assertEqual(res["event"]["phenomenological_state"], "ZUHANDEN")

    def test_l1_g2_006_phenomenological_tool_being_attunement(self) -> None:
        """Verifies L1-G2-006: Heideggerian Zuhandenheit vs Vorhandenheit flow disruption scoring."""
        from .phenomenology import SentinelPhenomenologyCircuit

        circuit = SentinelPhenomenologyCircuit()

        # 1. Flow interaction (Ready-to-hand / Zuhanden)
        flow_event = circuit.record_interaction(
            tool_name="quick_search",
            dwell_seconds=1.2,
            undo_count_in_window=0,
            erratic_input_switches=0,
            unhandled_error_shown=False,
        )
        self.assertEqual(flow_event.phenomenological_state, "ZUHANDEN")
        self.assertEqual(flow_event.focus_target, "WORLD_TASK")
        self.assertGreaterEqual(flow_event.transparency_score, 0.80)
        self.assertLess(flow_event.rupture_index, 0.45)

        # 2. Broken interaction (Present-at-hand / Vorhanden)
        rupture_event = circuit.record_interaction(
            tool_name="unresponsive_modal",
            dwell_seconds=8.5,
            undo_count_in_window=2,
            erratic_input_switches=3,
            unhandled_error_shown=True,
        )
        self.assertEqual(rupture_event.phenomenological_state, "VORHANDEN")
        self.assertEqual(rupture_event.focus_target, "TOOL_MECHANISM")
        self.assertLess(rupture_event.transparency_score, 0.30)
        self.assertGreater(rupture_event.rupture_index, 0.70)
        self.assertIn("Conspicuous breakdown", rupture_event.cognitive_diagnosis)

        # Check summary
        summary = circuit.get_summary()
        self.assertEqual(summary["total_evaluated_events"], 2)
        self.assertEqual(summary["ruptures_detected"], 1)

    def test_l1_g2_007_kinetic_chaining_multi_substrate_extremities(self) -> None:
        """Verifies L1-G2-007: Biomechanical kinetic momentum propagation across extremities."""
        from .cli import run_cli
        from .daemon import SentinelEdgeDaemon
        from g2_compiler.kinetic_chain import KineticChainCompiler
        from g2_compiler.types import IntentAST

        # 1. Kinetic Chain Compiler Propagation
        compiler = KineticChainCompiler()
        intent = IntentAST(
            intent_id="intent_kinetic_test",
            action="revert_unauthorized_state",
            target_noun="EnclaveState",
            parameters={"target": "node_01", "scope": "quarantine"},
            constraints=["L1-G2-001", "L1-G2-007"],
        )

        results, audits = compiler.propagate_to_extremities(intent)
        self.assertEqual(len(results), 4)  # CLI, Edge Daemon, Web PWA, Microservice
        for audit in audits:
            self.assertTrue(audit.is_compliant, f"Kinetic joint failed compliance for {audit.substrate.value}")
            self.assertGreater(audit.momentum_retained_ratio, 0.95, "Momentum retention must exceed 95%")
            self.assertLess(audit.impedance_loss, 0.05, "Impedance loss must be under 0.05")

        # 2. Terminal CLI Extremity Execution
        exit_code_status = run_cli(["status"])
        self.assertEqual(exit_code_status, 0)

        exit_code_dispatch = run_cli(["dispatch", "--tool", "read_telemetry"])
        self.assertEqual(exit_code_dispatch, 0)

        exit_code_rollback = run_cli(["rollback"])
        self.assertEqual(exit_code_rollback, 0)

        # 3. Headless Edge Daemon Extremity Execution
        daemon = SentinelEdgeDaemon(engine=self.engine)
        report = daemon.execute_audit_cycle()
        self.assertEqual(report["cycle"], 1)
        self.assertEqual(report["system_status"], "OPERATIONAL")
        self.assertTrue(len(report["state_hash"]) > 0)


if __name__ == "__main__":
    unittest.main()

