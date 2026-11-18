"""Integration Tests for Benchmarks Pipeline -> SystemG4bCompiler Mesh Bridge.

Verifies:
- `AxiomaCausalMeshEngine.synthesize()` routes end-to-end through `SystemG4bCompiler`.
- Phase 1 `ResearchDeliverableBundle` ID, `AcceptanceSpecIR` ID (`spec_<app_id>`), SpecHash,
  and Brain context ID are dynamically injected into `"Core Engine Synthesizer"` prompt.
- `synthesis_manifest.json` records `g4b_compilation` (`merkle_root`, `acceptance_spec_hash`,
  `research_bundle_id`, `statechart_coverage_pct`) and physically emitted Gen 4b deliverables.
- `ProvenanceEvaluator` (Pass 0) achieves 100.0 score with physical temp `transcript.jsonl` fixtures
  and enforces fail-closed anti-collusion and missing-transcript checks.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from benchmarks.macro_ablation.archetypes import axioma_kv
from benchmarks.macro_ablation.domain_models import AblationMode
from benchmarks.macro_ablation.evaluators.provenance_evaluator import ProvenanceEvaluator
from benchmarks.pipeline.synthesis_engines import (
    AxiomaCausalMeshEngine,
    SynthesisViolation,
)


class TestG4bMeshBridge(unittest.TestCase):
    """Verifies benchmark synthesis bridge through Generation 4b SystemG4bCompiler."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="g4b_mesh_bridge_")).resolve()
        self.app_data_dir = self.temp_dir / "app_data"
        self.archetype = axioma_kv.get_archetype()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_transcript_fixture(self, conversation_id: str, role: str) -> Path:
        t_dir = self.app_data_dir / "brain" / conversation_id / ".system_generated" / "logs"
        t_dir.mkdir(parents=True, exist_ok=True)
        t_file = t_dir / "transcript.jsonl"
        entries = [
            {"step_index": 0, "type": "USER_INPUT", "content": f"Execute role: {role}"},
            {"step_index": 1, "type": "PLANNER_RESPONSE", "content": f"Completed role: {role}"},
        ]
        t_file.write_text("\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")
        return t_file

    def test_01_axioma_causal_mesh_routes_through_g4b_compiler_and_scores_100_provenance(self) -> None:
        """Verifies Phase 1 Bundle/AcceptanceSpec prompt injection, manifest g4b_compilation, and 100.0 Pass 0 score."""
        target_dir = self.temp_dir / "axioma_kv_compiled"
        cids = {
            "Domain Ontologist & Systems Architect": str(uuid.uuid4()),
            "Core Engine Synthesizer": str(uuid.uuid4()),
            "Adversarial Byzantine QA Engineer": str(uuid.uuid4()),
            "Dialectical Red Team Architect": str(uuid.uuid4()),
        }
        for role, cid in cids.items():
            self._create_transcript_fixture(cid, role)

        captured_calls: list[dict[str, str]] = []

        def capturing_invoker(role: str, prompt: str, model: str) -> str:
            captured_calls.append({"role": role, "prompt": prompt, "model": model})
            return cids[role]

        engine = AxiomaCausalMeshEngine()
        result = engine.synthesize(self.archetype, target_dir, subagent_invoker=capturing_invoker)

        self.assertTrue(result.success)
        self.assertEqual(len(captured_calls), 4)

        # Verify causal role ordering: Brain -> Builder -> QA -> Red Team
        self.assertEqual(
            [c["role"] for c in captured_calls],
            [
                "Domain Ontologist & Systems Architect",
                "Core Engine Synthesizer",
                "Adversarial Byzantine QA Engineer",
                "Dialectical Red Team Architect",
            ],
        )

        # Inspect persisted synthesis_manifest.json on disk
        manifest_path = target_dir / "synthesis_manifest.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertIn("g4b_compilation", manifest)
        g4b = manifest["g4b_compilation"]
        for key in ("merkle_root", "acceptance_spec_hash", "research_bundle_id", "statechart_coverage_pct"):
            self.assertIn(key, g4b, f"Missing '{key}' in g4b_compilation")

        self.assertEqual(len(g4b["merkle_root"]), 64)
        self.assertEqual(len(g4b["acceptance_spec_hash"]), 64)
        self.assertTrue(g4b["research_bundle_id"])
        self.assertEqual(g4b["statechart_coverage_pct"], 100.0)

        # Verify dynamic Phase 1 -> Phase 2A prompt injection into Core Engine Synthesizer
        brain_prompt = captured_calls[0]["prompt"]
        synth_prompt = captured_calls[1]["prompt"]
        qa_prompt = captured_calls[2]["prompt"]

        self.assertIn(self.archetype.prompt, brain_prompt)
        expected_spec_id = f"spec_{self.archetype.id}"
        self.assertIn(f"Research Bundle: {g4b['research_bundle_id']}", synth_prompt)
        self.assertIn(f"Acceptance Spec: {expected_spec_id}", synth_prompt)
        self.assertIn(g4b["acceptance_spec_hash"], synth_prompt)
        self.assertIn(cids["Domain Ontologist & Systems Architect"], synth_prompt)

        # Verify blind QA prompt context separation (no Phase 1 bundle dump or brain context leakage)
        self.assertNotIn(g4b["research_bundle_id"], qa_prompt)
        self.assertNotIn(cids["Domain Ontologist & Systems Architect"], qa_prompt)

        # Verify physical Gen 4b deliverables on disk and entrypoint smoke execution
        for rel in (
            "run.py",
            "src/engine.py",
            "tests/test_smoke.py",
            ".telemetry_vault.sqlite",
            "telemetry_ledger.json",
            "telemetry_metrics.json",
            "dashboard.html",
            "telemetry_dashboard.html",
            "synthesis_manifest.json",
        ):
            artifact = target_dir / rel
            self.assertTrue(artifact.exists(), f"Missing artifact: {rel}")
            self.assertGreater(artifact.stat().st_size, 0, f"Empty artifact: {rel}")

        smoke_proc = subprocess.run(
            [sys.executable, "-u", str(target_dir / "run.py"), "--smoke-test"],
            capture_output=True,
            text=True,
            timeout=10.0,
            cwd=str(target_dir),
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        self.assertEqual(smoke_proc.returncode, 0, f"Emitted app smoke failed:\n{smoke_proc.stderr}")

        # Pass 0 ProvenanceEvaluator must score 100.0 against physical temp transcript.jsonl fixtures
        evaluator = ProvenanceEvaluator(weight=0.15, app_data_dir=self.app_data_dir)
        eval_result = evaluator.evaluate(
            app_dir=target_dir,
            archetype=self.archetype,
            mode=AblationMode.FULL_G4B,
        )
        self.assertTrue(eval_result.passed, f"ProvenanceEvaluator failed: {eval_result.details}")
        self.assertEqual(eval_result.raw_score, 100.0)
        self.assertEqual(eval_result.weighted_score, 15.0)
        self.assertEqual(eval_result.details["violations"], [])
        self.assertEqual(len(eval_result.details["transcript_checks"]), 4)
        self.assertTrue(all(tc["found"] and tc["bytes"] > 0 for tc in eval_result.details["transcript_checks"]))

    def test_02_mesh_bridge_requires_live_invoker_and_rejects_collusion(self) -> None:
        """Verifies AxiomaCausalMeshEngine fails closed without invoker or under Builder/QA collusion."""
        engine = AxiomaCausalMeshEngine()

        with self.assertRaises(SynthesisViolation):
            engine.synthesize(self.archetype, self.temp_dir / "missing_invoker", subagent_invoker=None)

        colluding_cid = str(uuid.uuid4())
        colluding_map = {
            "Domain Ontologist & Systems Architect": str(uuid.uuid4()),
            "Core Engine Synthesizer": colluding_cid,
            "Adversarial Byzantine QA Engineer": colluding_cid,
            "Dialectical Red Team Architect": str(uuid.uuid4()),
        }
        with self.assertRaises(SynthesisViolation) as ctx:
            engine.synthesize(
                self.archetype,
                self.temp_dir / "colluding_run",
                subagent_invoker=lambda role, prompt, model: colluding_map[role],
            )
        self.assertIn("Anti-collusion violation", str(ctx.exception))

    def test_03_provenance_evaluator_rejects_missing_transcript_on_disk(self) -> None:
        """Verifies ProvenanceEvaluator detects missing transcript.jsonl even after g4b compilation."""
        target_dir = self.temp_dir / "missing_transcript_run"
        cids = {
            "Domain Ontologist & Systems Architect": str(uuid.uuid4()),
            "Core Engine Synthesizer": str(uuid.uuid4()),
            "Adversarial Byzantine QA Engineer": str(uuid.uuid4()),
            "Dialectical Red Team Architect": str(uuid.uuid4()),
        }
        # Omit creating transcript for QA agent
        for role, cid in cids.items():
            if role != "Adversarial Byzantine QA Engineer":
                self._create_transcript_fixture(cid, role)

        engine = AxiomaCausalMeshEngine()
        result = engine.synthesize(
            self.archetype,
            target_dir,
            subagent_invoker=lambda role, prompt, model: cids[role],
        )
        self.assertTrue(result.success)

        evaluator = ProvenanceEvaluator(weight=0.15, app_data_dir=self.app_data_dir)
        eval_result = evaluator.evaluate(
            app_dir=target_dir,
            archetype=self.archetype,
            mode=AblationMode.FULL_G4B,
        )
        self.assertFalse(eval_result.passed)
        self.assertEqual(eval_result.raw_score, 0.0)
        self.assertTrue(
            any("MISSING_TRANSCRIPT" in v for v in eval_result.details["violations"]),
            f"Expected MISSING_TRANSCRIPT violation, got: {eval_result.details['violations']}",
        )

    def test_04_legacy_dead_prompt_helpers_removed_and_strict_defaults(self) -> None:
        """Verifies legacy dead helpers are absent and AxiomaCausalMeshEngine defaults to strict AcceptanceGate."""
        for legacy_helper in ("build_brain_prompt", "build_synthesizer_prompt", "build_qa_prompt"):
            self.assertFalse(
                hasattr(AxiomaCausalMeshEngine, legacy_helper),
                f"Legacy dead helper '{legacy_helper}' should not exist on AxiomaCausalMeshEngine",
            )

        engine = AxiomaCausalMeshEngine()
        self.assertFalse(engine.lenient_acceptance_gate)

        target_dir = self.temp_dir / "strict_clean_run"
        cids = {
            "Domain Ontologist & Systems Architect": str(uuid.uuid4()),
            "Core Engine Synthesizer": str(uuid.uuid4()),
            "Adversarial Byzantine QA Engineer": str(uuid.uuid4()),
            "Dialectical Red Team Architect": str(uuid.uuid4()),
        }
        result = engine.synthesize(
            self.archetype,
            target_dir,
            subagent_invoker=lambda role, prompt, model: cids[role],
        )
        self.assertTrue(result.success)
        g4b = result.manifest["g4b_compilation"]
        self.assertIs(g4b["audit_passed"], True)
        self.assertIs(g4b["governance_certified"], True)
        self.assertIs(g4b["acceptance_gate_passed"], True)
        self.assertEqual(g4b["acceptance_gate_violations"], [])

    def test_05_strict_acceptance_gate_fails_closed_on_banned_ast_pattern(self) -> None:
        """Verifies default lenient_acceptance_gate=False raises SynthesisViolation when Builder emits MockStreamWriter."""
        target_dir = self.temp_dir / "strict_banned_ast_run"
        cids = {
            "Domain Ontologist & Systems Architect": str(uuid.uuid4()),
            "Core Engine Synthesizer": str(uuid.uuid4()),
            "Adversarial Byzantine QA Engineer": str(uuid.uuid4()),
            "Dialectical Red Team Architect": str(uuid.uuid4()),
        }

        def banned_builder_invoker(role: str, prompt: str, model: str) -> str:
            if role == "Core Engine Synthesizer":
                bad_file = target_dir / "src" / "bad_stream.py"
                bad_file.parent.mkdir(parents=True, exist_ok=True)
                bad_file.write_text(
                    "class MockStreamWriter:\n    def write(self, data: bytes) -> int:\n        return len(data)\n",
                    encoding="utf-8",
                )
            return cids[role]

        engine = AxiomaCausalMeshEngine()
        self.assertFalse(engine.lenient_acceptance_gate)

        with self.assertRaises(SynthesisViolation) as ctx:
            engine.synthesize(self.archetype, target_dir, subagent_invoker=banned_builder_invoker)

        err_msg = str(ctx.exception)
        self.assertIn("SystemG4bCompiler execution failed", err_msg)
        self.assertIn("MockStreamWriter", err_msg)

    def test_06_lenient_acceptance_gate_records_false_and_non_empty_violations(self) -> None:
        """Verifies lenient_acceptance_gate=True surfaces audit_passed=False & non-empty violations (not hardcoded True)."""
        target_dir = self.temp_dir / "lenient_banned_ast_run"
        cids = {
            "Domain Ontologist & Systems Architect": str(uuid.uuid4()),
            "Core Engine Synthesizer": str(uuid.uuid4()),
            "Adversarial Byzantine QA Engineer": str(uuid.uuid4()),
            "Dialectical Red Team Architect": str(uuid.uuid4()),
        }

        def banned_builder_invoker(role: str, prompt: str, model: str) -> str:
            if role == "Core Engine Synthesizer":
                bad_file = target_dir / "src" / "bad_stream.py"
                bad_file.parent.mkdir(parents=True, exist_ok=True)
                bad_file.write_text(
                    "class MockStreamWriter:\n    def write(self, data: bytes) -> int:\n        return len(data)\n",
                    encoding="utf-8",
                )
            return cids[role]

        engine = AxiomaCausalMeshEngine(lenient_acceptance_gate=True)
        result = engine.synthesize(self.archetype, target_dir, subagent_invoker=banned_builder_invoker)

        self.assertTrue(result.success)
        g4b = result.manifest["g4b_compilation"]
        self.assertIs(g4b["audit_passed"], False)
        self.assertIs(g4b["governance_certified"], False)
        self.assertIs(g4b["acceptance_gate_passed"], False)
        self.assertGreater(len(g4b["acceptance_gate_violations"]), 0)
        self.assertTrue(
            any("MockStreamWriter" in v for v in g4b["acceptance_gate_violations"]),
            f"Expected MockStreamWriter in violations, got: {g4b['acceptance_gate_violations']}",
        )

    def test_07_builder_and_qa_prompts_include_contracts_without_brain_leakage(self) -> None:
        """Verifies Phase 2A includes AcceptanceSpecIR BANNED AST PATTERN and Phase 2C includes QA Falsification Protocol without Brain leakage."""
        target_dir = self.temp_dir / "prompt_contract_run"
        cids = {
            "Domain Ontologist & Systems Architect": f"brain-{uuid.uuid4()}",
            "Core Engine Synthesizer": f"builder-{uuid.uuid4()}",
            "Adversarial Byzantine QA Engineer": f"qa-{uuid.uuid4()}",
            "Dialectical Red Team Architect": f"redteam-{uuid.uuid4()}",
        }
        captured: dict[str, str] = {}

        def capture_invoker(role: str, prompt: str, model: str) -> str:
            captured[role] = prompt
            return cids[role]

        engine = AxiomaCausalMeshEngine()
        result = engine.synthesize(self.archetype, target_dir, subagent_invoker=capture_invoker)
        self.assertTrue(result.success)

        builder_prompt = captured["Core Engine Synthesizer"]
        qa_prompt = captured["Adversarial Byzantine QA Engineer"]
        g4b = result.manifest["g4b_compilation"]

        self.assertIn("AcceptanceSpecIR", builder_prompt)
        self.assertIn("BANNED AST PATTERN", builder_prompt)
        self.assertIn("MockStreamWriter", builder_prompt)

        self.assertIn("Adversarial QA Falsification Protocol", qa_prompt)
        self.assertNotIn(cids["Domain Ontologist & Systems Architect"], qa_prompt)
        self.assertNotIn(g4b["research_bundle_id"], qa_prompt)
        self.assertNotIn("Brain Context:", qa_prompt)


if __name__ == "__main__":
    unittest.main()
