"""Unit & Integration tests for CausalPipelineRunner and SynthesisEngines."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from benchmarks.macro_ablation.archetypes import axioma_kv
from benchmarks.macro_ablation.domain_models import AblationMode
from benchmarks.pipeline.synthesis_engines import (
    AxiomaCausalMeshEngine,
    PhantomEmissionViolation,
    VanillaSynthesisEngine,
)
from benchmarks.pipeline.causal_pipeline_runner import (
    BenchmarkTrialConfig,
    CausalPipelineRunner,
)


class TestCausalPipelineRunner(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_pipeline_"))
        self.app_data_dir = self.test_dir / "app_data"
        self.reports_dir = self.test_dir / "reports"
        self.archetype = axioma_kv.get_archetype()

        # Runner with test directories
        self.runner = CausalPipelineRunner(
            workspace_root=self.test_dir,
            enable_provenance=True,
            reports_dir=self.reports_dir,
        )
        self.runner.gauntlet.provenance_evaluator.app_data_dir = self.app_data_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_mock_transcript(self, conversation_id: str) -> Path:
        t_dir = self.app_data_dir / "brain" / conversation_id / ".system_generated" / "logs"
        t_dir.mkdir(parents=True, exist_ok=True)
        t_file = t_dir / "transcript.jsonl"
        t_file.write_text('{"step_index": 0, "type": "USER_INPUT"}\n{"step_index": 1, "type": "PLANNER_RESPONSE"}\n', encoding="utf-8")
        return t_file

    def test_phantom_emission_caught(self):
        """Empty target directory with zero files must trip PhantomEmissionViolation."""
        engine = VanillaSynthesisEngine()
        empty_dir = self.test_dir / "empty_candidate"
        with self.assertRaises(PhantomEmissionViolation):
            engine.compute_disk_grounding(empty_dir)

    def test_vanilla_synthesis_engine_flow(self):
        """VanillaSynthesisEngine emits manifest, records 1 subagent witness, and computes SHA-256."""
        target_dir = self.test_dir / "vanilla_candidate"
        target_dir.mkdir(parents=True, exist_ok=True)

        # Mock physical file creation
        (target_dir / "run.py").write_text("#!/usr/bin/env python3\nprint('hello')\n", encoding="utf-8")
        (target_dir / "src").mkdir()
        (target_dir / "src" / "models.py").write_text("class KeyValueEntry: pass\n", encoding="utf-8")

        cid = "cid_vanilla_test_1"
        self._create_mock_transcript(cid)

        def mock_invoker(role, prompt, model):
            return cid

        engine = VanillaSynthesisEngine()
        result = engine.synthesize(self.archetype, target_dir, subagent_invoker=mock_invoker)
        self.assertTrue(result.success)
        self.assertEqual(len(result.subagent_witnesses), 1)
        self.assertIn("synthesis_manifest.json", [f.name for f in target_dir.glob("*.json")])
        self.assertFalse(result.manifest["is_multi_agent"])

    def test_axioma_causal_mesh_engine_4_phases(self):
        """AxiomaCausalMeshEngine executes 4 orthogonal subagent phases, asserting anti-collusion."""
        target_dir = self.test_dir / "axioma_candidate"
        target_dir.mkdir(parents=True, exist_ok=True)

        (target_dir / "run.py").write_text("#!/usr/bin/env python3\nprint('axioma')\n", encoding="utf-8")
        (target_dir / "src").mkdir()
        (target_dir / "src" / "models.py").write_text("class KeyValueEntry: pass\n", encoding="utf-8")

        cids = {
            "Domain Ontologist & Systems Architect": "cid_brain_441",
            "Core Engine Synthesizer": "cid_synth_442",
            "Adversarial Byzantine QA Engineer": "cid_qa_443",
            "Dialectical Red Team Architect": "cid_redteam_444",
        }
        for c in cids.values():
            self._create_mock_transcript(c)

        def mock_invoker(role, prompt, model):
            return cids[role]

        engine = AxiomaCausalMeshEngine()
        result = engine.synthesize(self.archetype, target_dir, subagent_invoker=mock_invoker)
        self.assertTrue(result.success)
        self.assertEqual(len(result.subagent_witnesses), 4)
        self.assertTrue(result.manifest["is_multi_agent"])

        # Anti-collusion assertion: all 4 conversation IDs must be distinct
        observed_cids = [w["conversation_id"] for w in result.subagent_witnesses]
        self.assertEqual(len(set(observed_cids)), 4)

    def test_full_pipeline_runner_trial_execution(self):
        """CausalPipelineRunner executes full trial, grades all passes including Pass 0 Provenance."""
        target_dir = self.test_dir / "trial_run_axioma"
        target_dir.mkdir(parents=True, exist_ok=True)

        # Populate candidate app files
        (target_dir / "run.py").write_text("#!/usr/bin/env python3\nimport sys\nif '--smoke-test' in sys.argv: sys.exit(0)\n", encoding="utf-8")
        (target_dir / "src").mkdir()
        (target_dir / "src" / "models.py").write_text("class KeyValueEntry: pass\n", encoding="utf-8")

        cids = {
            "Domain Ontologist & Systems Architect": "cid_brain_trial_1",
            "Core Engine Synthesizer": "cid_synth_trial_2",
            "Adversarial Byzantine QA Engineer": "cid_qa_trial_3",
            "Dialectical Red Team Architect": "cid_redteam_trial_4",
        }
        for c in cids.values():
            self._create_mock_transcript(c)

        def mock_invoker(role, prompt, model):
            return cids[role]

        cfg = BenchmarkTrialConfig(
            system_id="meta_axioma_g4b",
            system_name="Meta-Axioma Baseline",
            archetype_id="axioma_kv",
            trial=1,
            target_dir=target_dir,
            mode=AblationMode.FULL_G4B,
        )

        run_result = self.runner.run_trial(cfg, subagent_invoker=mock_invoker)
        self.assertTrue(run_result.synthesis_result.success)

        # Assert Pass 0 Provenance is evaluated and passed
        scorecard = run_result.scorecard
        self.assertIn("provenance", scorecard.pass_results)
        self.assertTrue(scorecard.pass_results["provenance"].passed)
        self.assertEqual(scorecard.pass_results["provenance"].raw_score, 100.0)


if __name__ == "__main__":
    unittest.main()
