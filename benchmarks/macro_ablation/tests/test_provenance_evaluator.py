"""Unit tests for Pass 0: Multi-Agent Provenance & Context Separation Evaluator."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from benchmarks.macro_ablation.domain_models import AblationMode
from benchmarks.macro_ablation.evaluators.provenance_evaluator import (
    ProvenanceEvaluator,
    MonolithicSimulationViolation,
    AgentCollusionViolation,
    FabricatedWitnessViolation,
)


class TestProvenanceEvaluator(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_prov_"))
        self.app_data_dir = self.test_dir / "app_data"
        self.app_dir = self.test_dir / "candidate_app"
        self.app_dir.mkdir(parents=True, exist_ok=True)

        self.evaluator = ProvenanceEvaluator(weight=0.15, app_data_dir=self.app_data_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_mock_transcript(self, conversation_id: str) -> Path:
        t_dir = self.app_data_dir / "brain" / conversation_id / ".system_generated" / "logs"
        t_dir.mkdir(parents=True, exist_ok=True)
        t_file = t_dir / "transcript.jsonl"
        t_file.write_text('{"step_index": 0, "type": "USER_INPUT"}\n{"step_index": 1, "type": "PLANNER_RESPONSE"}\n', encoding="utf-8")
        return t_file

    def test_missing_manifest_fails_for_multi_agent_mode(self):
        """A candidate claiming FULL_G4B without any manifest must fail with 0.0."""
        res = self.evaluator.evaluate(self.app_dir, mode=AblationMode.FULL_G4B)
        self.assertFalse(res.passed)
        self.assertEqual(res.raw_score, 0.0)
        self.assertIn("MISSING_PROVENANCE_MANIFEST", res.details["violations"])

    def test_monolithic_bypass_rejected(self):
        """A candidate claiming multi-agent but having only 1 conversation context must be rejected."""
        cid = "cid_mono_001"
        self._create_mock_transcript(cid)

        manifest = {
            "is_multi_agent": True,
            "subagents": [
                {"role": "Monolithic Synthesizer", "conversation_id": cid}
            ]
        }
        res = self.evaluator.evaluate(self.app_dir, mode=AblationMode.FULL_G4B, provenance_manifest=manifest)
        self.assertFalse(res.passed)
        self.assertEqual(res.raw_score, 0.0)
        self.assertTrue(any("INSUFFICIENT_SUBAGENTS" in v for v in res.details["violations"]))

    def test_builder_tester_collusion_rejected(self):
        """Builder and QA agents sharing the same conversation ID must be rejected for self-grading collusion."""
        cid_brain = "cid_brain_001"
        cid_shared = "cid_shared_collusion_002"
        self._create_mock_transcript(cid_brain)
        self._create_mock_transcript(cid_shared)

        manifest = {
            "is_multi_agent": True,
            "subagents": [
                {"role": "Domain Ontologist", "cognitive_role": "DOMAIN_ONTOLOGIST", "conversation_id": cid_brain},
                {"role": "Core Engine Synthesizer", "cognitive_role": "CORE_ENGINE_SYNTHESIZER", "conversation_id": cid_shared},
                {"role": "Adversarial QA Engineer", "cognitive_role": "ADVERSARIAL_QA_ENGINEER", "conversation_id": cid_shared},
            ]
        }
        res = self.evaluator.evaluate(self.app_dir, mode=AblationMode.FULL_G4B, provenance_manifest=manifest)
        self.assertFalse(res.passed)
        self.assertEqual(res.raw_score, 0.0)
        self.assertTrue(any("SELF_GRADING_COLLUSION" in v or "COLLUSION_DETECTED" in v for v in res.details["violations"]))

    def test_fabricated_uuid_fails_liveness(self):
        """Conversation IDs without physical transcript files on disk must fail."""
        manifest = {
            "is_multi_agent": True,
            "subagents": [
                {"role": "Brain", "conversation_id": "fake_uuid_1"},
                {"role": "Synthesizer", "conversation_id": "fake_uuid_2"},
                {"role": "QA", "conversation_id": "fake_uuid_3"},
            ]
        }
        res = self.evaluator.evaluate(self.app_dir, mode=AblationMode.FULL_G4B, provenance_manifest=manifest)
        self.assertFalse(res.passed)
        self.assertEqual(res.raw_score, 0.0)
        self.assertTrue(any("MISSING_TRANSCRIPT" in v for v in res.details["violations"]))

    def test_genuine_orthogonal_subagents_pass(self):
        """Genuine multi-agent pipeline with >= 3 distinct subagents and physical transcripts passes with 100.0."""
        c1 = "cid_brain_valid_1"
        c2 = "cid_synth_valid_2"
        c3 = "cid_qa_valid_3"
        c4 = "cid_redteam_valid_4"
        for c in (c1, c2, c3, c4):
            self._create_mock_transcript(c)

        manifest = {
            "is_multi_agent": True,
            "subagents": [
                {"role": "Domain Ontologist", "cognitive_role": "DOMAIN_ONTOLOGIST", "conversation_id": c1},
                {"role": "Core Engine Synthesizer", "cognitive_role": "CORE_ENGINE_SYNTHESIZER", "conversation_id": c2},
                {"role": "Adversarial QA Engineer", "cognitive_role": "ADVERSARIAL_QA_ENGINEER", "conversation_id": c3},
                {"role": "Dialectical Red Team Architect", "cognitive_role": "SOCRATIC_RED_TEAM", "conversation_id": c4},
            ]
        }
        res = self.evaluator.evaluate(self.app_dir, mode=AblationMode.FULL_G4B, provenance_manifest=manifest)
        self.assertTrue(res.passed)
        self.assertEqual(res.raw_score, 100.0)
        self.assertEqual(res.weighted_score, round(100.0 * self.evaluator.weight, 2))
        self.assertEqual(len(res.details["violations"]), 0)

    def test_vanilla_single_agent_control_mode_passes(self):
        """Single-agent Vanilla control mode running under FLAT_PROMPT_LLM passes without multi-agent requirements."""
        cid = "cid_vanilla_control_01"
        self._create_mock_transcript(cid)

        manifest = {
            "is_multi_agent": False,
            "subagents": [
                {"role": "Vanilla Developer Agent", "conversation_id": cid}
            ]
        }
        res = self.evaluator.evaluate(self.app_dir, mode=AblationMode.FLAT_PROMPT_LLM, provenance_manifest=manifest)
        self.assertTrue(res.passed)
        self.assertEqual(res.raw_score, 100.0)


if __name__ == "__main__":
    unittest.main()
