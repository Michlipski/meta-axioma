"""
Adversarial QA & Byzantine Verification Test Suite for Axioma Evolution Dashboard.

Enforces:
- [NEG-G1B-001] Anti-Phantom Emission Gate
- [L1-G3B-016] Zero-Trust Micro-Auditing
- [L1-008] Landauer Thermodynamic Heat Conservation

Test Coverage:
1. Malformed JSON payloads to POST /api/feedback (empty strings, syntax corruption, non-dict payloads, non-integer & out-of-range ratings, huge payloads).
2. Concurrent client flooding over AsyncIO StreamReader/StreamWriter (100 parallel clients, stream contention, race condition resistance).
3. Boundary & fuzz queries on /api/stages/invalid_id, /api/transformations/unknown, /api/components/fake, /api/simulations/unknown, path traversal fuzzing.
4. Generational diff engine edge cases (identity diffing, unknown generation fallback, parameter omission, anti-symmetry).
5. Physical Landauer calculation boundary invariants (bits=0, bits=50,000, non-negative heat dissipation, monotonic increase, negative bits rejection, REST endpoint validation).
6. Dashboard HTML static inspection (non-empty physical emission, zero unrendered template brackets, embedding of all 8 stages, Landauer UI controls).
"""

from __future__ import annotations

import asyncio
import json
import math
import re
import sys
import unittest
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from src.data_store import EvolutionDataStore
from server import process_http_request, handle_async_http_client


class DummyAsyncWriter:
    """Mock StreamWriter for AsyncIO testing without external socket binding."""

    def __init__(self) -> None:
        self.data = bytearray()
        self.closed = False

    def write(self, b: bytes) -> None:
        self.data.extend(b)

    async def drain(self) -> None:
        await asyncio.sleep(0)

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        await asyncio.sleep(0)


class TestAdversarialFeedbackAndMalformedPayloads(unittest.TestCase):
    """Adversarial testing of POST /api/feedback and malformed JSON ingestion."""

    def setUp(self) -> None:
        self.store = EvolutionDataStore()

    def test_empty_string_payload_rejected(self) -> None:
        """Verify empty byte string or whitespace payloads yield HTTP 400."""
        for empty_body in [b"", b"   ", b"\n\t\r"]:
            status, headers, body = process_http_request(
                "POST",
                "/api/feedback",
                {"Content-Type": "application/json"},
                empty_body,
                self.store,
            )
            self.assertEqual(status, 400, f"Expected 400 for empty body: {empty_body!r}")
            resp = json.loads(body.decode("utf-8"))
            self.assertIn("error", resp)

    def test_corrupted_json_syntax_rejected(self) -> None:
        """Verify malformed JSON syntax yields HTTP 400."""
        malformed_inputs = [
            b"{not valid json",
            b'{"author": "Alice", "rating": }',
            b'{"unclosed string',
            b"<xml>not json</xml>",
            b"\x00\x01\x02binary corrupt",
        ]
        for malformed in malformed_inputs:
            status, headers, body = process_http_request(
                "POST",
                "/api/feedback",
                {"Content-Type": "application/json"},
                malformed,
                self.store,
            )
            self.assertEqual(status, 400, f"Expected 400 for malformed: {malformed!r}")
            resp = json.loads(body.decode("utf-8"))
            self.assertIn("error", resp)

    def test_non_dict_json_payloads_rejected(self) -> None:
        """Verify array, primitive, or scalar JSON payloads yield HTTP 400."""
        non_dicts = [
            b"[1, 2, 3]",
            b'"just a string"',
            b"12345",
            b"true",
            b"null",
        ]
        for payload in non_dicts:
            status, headers, body = process_http_request(
                "POST",
                "/api/feedback",
                {"Content-Type": "application/json"},
                payload,
                self.store,
            )
            self.assertEqual(status, 400, f"Expected 400 for non-dict: {payload!r}")
            resp = json.loads(body.decode("utf-8"))
            self.assertIn("error", resp)

    def test_non_integer_ratings_rejected(self) -> None:
        """Verify non-integer rating types (strings, null, dicts, arrays) yield HTTP 400."""
        bad_ratings = [
            {"rating": "five", "comment": "Good"},
            {"rating": "superb", "comment": "Good"},
            {"rating": None, "comment": "Good"},
            {"rating": [1, 2], "comment": "Good"},
            {"rating": {"stars": 5}, "comment": "Good"},
            {"rating": "1.2.3", "comment": "Good"},
        ]
        for bad in bad_ratings:
            payload = json.dumps(bad).encode("utf-8")
            status, headers, body = process_http_request(
                "POST",
                "/api/feedback",
                {"Content-Type": "application/json"},
                payload,
                self.store,
            )
            self.assertEqual(status, 400, f"Expected 400 for bad rating: {bad}")
            resp = json.loads(body.decode("utf-8"))
            self.assertIn("error", resp)

    def test_out_of_bounds_ratings_rejected(self) -> None:
        """Verify integer ratings outside the [1, 5] interval yield HTTP 400."""
        out_of_bounds = [
            {"rating": 0, "comment": "Too low"},
            {"rating": -1, "comment": "Negative rating"},
            {"rating": -999, "comment": "Extremely negative"},
            {"rating": 6, "comment": "Too high"},
            {"rating": 100, "comment": "Way too high"},
        ]
        for oob in out_of_bounds:
            payload = json.dumps(oob).encode("utf-8")
            status, headers, body = process_http_request(
                "POST",
                "/api/feedback",
                {"Content-Type": "application/json"},
                payload,
                self.store,
            )
            self.assertEqual(status, 400, f"Expected 400 for out of bounds rating: {oob}")
            resp = json.loads(body.decode("utf-8"))
            self.assertIn("error", resp)

    def test_huge_payload_ingestion(self) -> None:
        """Verify server handles large valid JSON payload without memory fault."""
        large_comment = "Adversarial stress test chunk. " * 15000  # ~450 KB
        payload = json.dumps({
            "author": "HighVolumeFuzzer",
            "rating": 4,
            "category": "Stress Test",
            "comment": large_comment,
        }).encode("utf-8")

        status, headers, body = process_http_request(
            "POST",
            "/api/feedback",
            {"Content-Type": "application/json"},
            payload,
            self.store,
        )
        self.assertEqual(status, 201)
        resp = json.loads(body.decode("utf-8"))
        self.assertEqual(resp["status"], "created")
        self.assertEqual(len(resp["entry"]["comment"]), len(large_comment.strip()))


class TestAsyncIOConcurrencyAndFlooding(unittest.TestCase):
    """Stress testing concurrent AsyncIO stream handling against client flooding."""

    def setUp(self) -> None:
        self.store = EvolutionDataStore()

    def test_concurrent_client_flooding_100_requests(self) -> None:
        """Simulate 100 concurrent clients across diverse API endpoints."""
        endpoints = [
            ("GET", "/api/health"),
            ("GET", "/api/stages"),
            ("GET", "/api/transformations"),
            ("GET", "/api/components"),
            ("GET", "/api/diff?a=s0&b=g4b"),
            ("GET", "/api/diff?a=g1&b=g3b"),
            ("GET", "/api/landauer?bits=50000"),
            ("GET", "/api/simulations/axioma_go"),
            ("GET", "/api/philosophy"),
            ("GET", "/api/zenith"),
        ]

        async def run_flood() -> list[tuple[int, bytes]]:
            tasks = []
            writers: list[DummyAsyncWriter] = []

            for i in range(100):
                method, path = endpoints[i % len(endpoints)]
                req_text = f"{method} {path} HTTP/1.1\r\nHost: localhost\r\n\r\n"
                reader = asyncio.StreamReader()
                reader.feed_data(req_text.encode("utf-8"))
                reader.feed_eof()
                writer = DummyAsyncWriter()
                writers.append(writer)
                tasks.append(handle_async_http_client(reader, writer, self.store))

            await asyncio.gather(*tasks)

            results = []
            for w in writers:
                raw_response = bytes(w.data)
                first_line = raw_response.split(b"\r\n")[0].decode("utf-8", errors="replace")
                status_code = int(first_line.split()[1]) if len(first_line.split()) > 1 else 0
                results.append((status_code, raw_response))
            return results

        results = asyncio.run(run_flood())
        self.assertEqual(len(results), 100)
        for idx, (status, data) in enumerate(results):
            self.assertEqual(
                status,
                200,
                f"Client #{idx} failed with status {status}. Response preview: {data[:100]!r}",
            )
            self.assertTrue(len(data) > 0)


class TestBoundaryQueriesAndPathFuzzing(unittest.TestCase):
    """Testing boundary queries, unknown IDs, and path traversal fuzzing."""

    def setUp(self) -> None:
        self.store = EvolutionDataStore()

    def test_boundary_stages_queries(self) -> None:
        """Verify invalid stage IDs return 404."""
        invalid_ids = [
            "invalid_id",
            "unknown_stage_999",
            "g5",
            "s_minus_1",
            "null",
            "DROP TABLE stages",
        ]
        for bad_id in invalid_ids:
            status, headers, body = process_http_request("GET", f"/api/stages/{bad_id}", {}, b"", self.store)
            self.assertEqual(status, 404, f"Expected 404 for stage {bad_id}")
            resp = json.loads(body.decode("utf-8"))
            self.assertIn("error", resp)

    def test_boundary_transformations_queries(self) -> None:
        """Verify invalid transformation IDs return 404."""
        invalid_ids = [
            "unknown",
            "t_fake_to_fake",
            "t_s0_to_s0",
            "t_g4b_to_s0",
            "transformation_infinity",
        ]
        for bad_id in invalid_ids:
            status, headers, body = process_http_request("GET", f"/api/transformations/{bad_id}", {}, b"", self.store)
            self.assertEqual(status, 404, f"Expected 404 for transformation {bad_id}")
            resp = json.loads(body.decode("utf-8"))
            self.assertIn("error", resp)

    def test_boundary_components_queries(self) -> None:
        """Verify invalid component / subsystem lineage IDs return 404."""
        invalid_ids = [
            "fake",
            "nonexistent_subsystem",
            "quantum_flux_capacitor",
            "telemetry_ghost",
        ]
        for bad_id in invalid_ids:
            status, headers, body = process_http_request("GET", f"/api/components/{bad_id}", {}, b"", self.store)
            self.assertEqual(status, 404, f"Expected 404 for component {bad_id}")
            resp = json.loads(body.decode("utf-8"))
            self.assertIn("error", resp)

    def test_boundary_simulation_queries(self) -> None:
        """Verify invalid simulation app IDs return 404."""
        status, headers, body = process_http_request("GET", "/api/simulations/unknown_app", {}, b"", self.store)
        self.assertEqual(status, 404)
        resp = json.loads(body.decode("utf-8"))
        self.assertIn("error", resp)

    def test_path_traversal_protection(self) -> None:
        """Verify directory traversal attempts cannot escape the static boundary."""
        traversal_paths = [
            "/../../../etc/passwd",
            "/..%2f..%2f..%2fetc/passwd",
            "/static/../../server.py",
            "/static/../../../root",
        ]
        for path in traversal_paths:
            status, headers, body = process_http_request("GET", path, {}, b"", self.store)
            # Should be 404 Not Found, never 200 with sensitive system files
            self.assertEqual(status, 404, f"Expected 404 for traversal path: {path}")


class TestGenerationalDiffEdgeCases(unittest.TestCase):
    """Testing edge cases of the generational diff engine."""

    def setUp(self) -> None:
        self.store = EvolutionDataStore()

    def test_identity_diff_same_stage(self) -> None:
        """Diffing a stage with itself must yield zero delta and empty added/retired sets."""
        for stage_id in ["s0", "g1", "g2", "g3", "g1b", "g2b", "g3b", "g4b"]:
            diff = self.store.get_generational_diff(stage_id, stage_id)
            self.assertEqual(diff["stage_a"]["id"], stage_id)
            self.assertEqual(diff["stage_b"]["id"], stage_id)
            self.assertEqual(diff["nodes_delta"], 0, f"Identity diff for {stage_id} must have nodes_delta == 0")
            self.assertEqual(diff["invariants_added"], [], f"Identity diff for {stage_id} must have no added invariants")
            self.assertEqual(diff["invariants_retired"], [], f"Identity diff for {stage_id} must have no retired invariants")
            self.assertGreaterEqual(len(diff["invariants_retained"]), 0)

    def test_unknown_stage_fallback_in_diff(self) -> None:
        """Unknown stages gracefully fall back to default anchors without server crash."""
        diff = self.store.get_generational_diff("unknown_alpha", "unknown_beta")
        # Stage A defaults to s0, Stage B defaults to g4b
        self.assertEqual(diff["stage_a"]["id"], "s0")
        self.assertEqual(diff["stage_b"]["id"], "g4b")
        self.assertIn("nodes_delta", diff)
        self.assertIn("invariants_added", diff)

    def test_diff_api_endpoint_edge_cases(self) -> None:
        """Verify /api/diff handles omitted query parameters and self-diffs over HTTP."""
        # 1. Parameter omission defaults to s0 vs g4b
        status, headers, body = process_http_request("GET", "/api/diff", {}, b"", self.store)
        self.assertEqual(status, 200)
        diff = json.loads(body.decode("utf-8"))
        self.assertEqual(diff["stage_a"]["id"], "s0")
        self.assertEqual(diff["stage_b"]["id"], "g4b")

        # 2. Self diff over HTTP: /api/diff?a=g4b&b=g4b
        status, headers, body = process_http_request("GET", "/api/diff?a=g4b&b=g4b", {}, b"", self.store)
        self.assertEqual(status, 200)
        diff_self = json.loads(body.decode("utf-8"))
        self.assertEqual(diff_self["nodes_delta"], 0)
        self.assertEqual(diff_self["invariants_added"], [])

    def test_diff_anti_symmetry(self) -> None:
        """Diffing A->B vs B->A must have reversed node deltas and complementary added/retired sets."""
        diff_fwd = self.store.get_generational_diff("s0", "g4b")
        diff_rev = self.store.get_generational_diff("g4b", "s0")

        self.assertEqual(diff_fwd["nodes_delta"], -diff_rev["nodes_delta"])
        self.assertEqual(set(diff_fwd["invariants_added"]), set(diff_rev["invariants_retired"]))
        self.assertEqual(set(diff_fwd["invariants_retired"]), set(diff_rev["invariants_added"]))
        self.assertEqual(set(diff_fwd["invariants_retained"]), set(diff_rev["invariants_retained"]))


class TestPhysicalLandauerCalculationBoundaryInvariants(unittest.TestCase):
    """
    Testing physical Landauer calculation boundary invariants [L1-008]:
    Q = bits * k_B * T * ln(2)
    where k_B = 1.380649e-23 J/K, T = 300.0 K.
    """

    def setUp(self) -> None:
        self.store = EvolutionDataStore()
        self.kb = 1.380649e-23
        self.t = 300.0
        self.ln2 = math.log(2)

    def test_landauer_zero_bits_erasure(self) -> None:
        """When 0 bits are erased, thermodynamic heat dissipation is exactly 0.0 J."""
        heat = self.store.calculate_landauer_heat(0, self.t)
        self.assertEqual(heat, 0.0)

    def test_landauer_50000_bits_erasure(self) -> None:
        """When 50,000 bits are erased at 300K, Q ~= 1.4354e-16 J."""
        expected = 50000.0 * self.kb * self.t * self.ln2
        heat = self.store.calculate_landauer_heat(50000, self.t)
        self.assertAlmostEqual(heat, expected, places=22)
        # Check that it matches the 1.4354e-16 J scale
        self.assertGreater(heat, 1.435e-16)
        self.assertLess(heat, 1.436e-16)

    def test_landauer_non_negative_heat_dissipation(self) -> None:
        """Invariant [L1-008]: Thermodynamic heat dissipation must be strictly >= 0 for all bits >= 0."""
        test_bit_counts = [0, 1, 10, 100, 1000, 50000, 100000, 1000000]
        previous_heat = -1.0
        for bits in test_bit_counts:
            heat = self.store.calculate_landauer_heat(bits, self.t)
            self.assertGreaterEqual(heat, 0.0, f"Heat must be non-negative for bits={bits}")
            self.assertGreaterEqual(heat, previous_heat, "Heat dissipation must be monotonically non-decreasing")
            previous_heat = heat

    def test_landauer_negative_bits_rejection(self) -> None:
        """Negative bits violate thermodynamic physics and must raise ValueError."""
        with self.assertRaises(ValueError):
            self.store.calculate_landauer_heat(-1, self.t)
        with self.assertRaises(ValueError):
            self.store.calculate_landauer_heat(-50000, self.t)

    def test_landauer_api_endpoint(self) -> None:
        """Verify REST endpoint /api/landauer over wire HTTP."""
        # 1. 50,000 bits query
        status, headers, body = process_http_request("GET", "/api/landauer?bits=50000", {}, b"", self.store)
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertEqual(data["bits"], 50000.0)
        self.assertIn("joules", data)
        self.assertAlmostEqual(data["joules"], 50000.0 * self.kb * self.t * self.ln2, places=22)

        # 2. Negative bits rejected with HTTP 400
        status, headers, body = process_http_request("GET", "/api/landauer?bits=-100", {}, b"", self.store)
        self.assertEqual(status, 400)
        err = json.loads(body.decode("utf-8"))
        self.assertIn("error", err)

        # 3. Non-numeric bits rejected with HTTP 400
        status, headers, body = process_http_request("GET", "/api/landauer?bits=invalid", {}, b"", self.store)
        self.assertEqual(status, 400)


class TestDashboardHtmlStaticVerification(unittest.TestCase):
    """
    Enforces [NEG-G1B-001] (Anti-Phantom Emission Gate) on the primary dashboard deliverable:
    - dashboard.html is non-empty (>50 KB).
    - Contains zero unrendered template brackets (no unrendered {{...}} or {%...%}).
    - Embeds all 8 generational stages.
    - Embeds the interactive Landauer thermodynamic dissipation controls.
    """

    def setUp(self) -> None:
        self.dashboard_path = APP_ROOT / "dashboard.html"

    def test_dashboard_file_physical_emission(self) -> None:
        """Verify dashboard.html exists on the physical filesystem and exceeds 50 KB."""
        self.assertTrue(self.dashboard_path.is_file(), "dashboard.html must exist on physical filesystem")
        file_size = self.dashboard_path.stat().st_size
        self.assertGreater(
            file_size,
            50000,
            f"dashboard.html must be a non-trivial emitted artifact (>50 KB), found {file_size} bytes",
        )

    def test_zero_unrendered_template_brackets(self) -> None:
        """Verify zero unrendered template syntax brackets remain in dashboard.html."""
        content = self.dashboard_path.read_text(encoding="utf-8")
        # Check for unrendered Jinja/Mustache expressions: {{ expression }}
        jinja_mustache_matches = re.findall(r"\{\{\s*[\w\.\-]+\s*\}\}", content)
        self.assertEqual(
            jinja_mustache_matches,
            [],
            f"Found unrendered Jinja/Mustache template brackets in dashboard.html: {jinja_mustache_matches}",
        )

        # Check for unrendered Django/Jinja template tags: {% tag %}
        django_tag_matches = re.findall(r"\{%\s*[\w\.\-]+\s*.*?%\}", content)
        self.assertEqual(
            django_tag_matches,
            [],
            f"Found unrendered Django/Jinja tags in dashboard.html: {django_tag_matches}",
        )

    def test_all_eight_stages_embedded(self) -> None:
        """Verify all 8 stages are embedded directly into dashboard.html."""
        content = self.dashboard_path.read_text(encoding="utf-8")
        expected_stages = ["s0", "g1", "g2", "g3", "g1b", "g2b", "g3b", "g4b"]
        for st in expected_stages:
            found = (
                f'"{st}"' in content
                or f"'{st}'" in content
                or f'id="{st}"' in content
                or f'id: "{st}"' in content
                or f">{st.upper()}<" in content
            )
            self.assertTrue(found, f"Stage '{st}' not found embedded in dashboard.html")

    def test_landauer_thermodynamic_controls_embedded(self) -> None:
        """Verify Landauer calculator UI elements and physical constant are present in dashboard.html."""
        content = self.dashboard_path.read_text(encoding="utf-8")
        self.assertIn("landauer-bits-slider", content)
        self.assertIn("landauer-joules-display", content)
        self.assertIn("1.380649e-23", content)
        self.assertIn("feedback-form", content)


if __name__ == "__main__":
    unittest.main()
