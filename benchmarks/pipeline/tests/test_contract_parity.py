"""Unit Tests for VanillaSynthesisEngine Contract-Parity Prompting & Manifest Recording."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import unittest
import uuid

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from benchmarks.macro_ablation.archetypes import get_archetype_by_id
from benchmarks.macro_ablation.domain_models import AblationMode
from benchmarks.pipeline.causal_pipeline_runner import (
    BenchmarkTrialConfig,
    CausalPipelineRunner,
)
from benchmarks.pipeline.synthesis_engines import VanillaSynthesisEngine


class TestVanillaContractParity(unittest.TestCase):
    """Verifies contract-parity prompting default, legacy opt-in mode, and manifest/ledger recording."""

    def setUp(self) -> None:
        self.scratch = REPO_ROOT / ".scratch" / f"test_parity_{uuid.uuid4().hex[:8]}"
        self.scratch.mkdir(parents=True, exist_ok=True)
        self.app_data = self.scratch / "app_data"

    def tearDown(self) -> None:
        shutil.rmtree(self.scratch, ignore_errors=True)

    def _create_transcript(self, cid: str) -> None:
        t_dir = self.app_data / "brain" / cid / ".system_generated" / "logs"
        t_dir.mkdir(parents=True, exist_ok=True)
        (t_dir / "transcript.jsonl").write_text('{"step_index":0,"type":"USER_INPUT"}\n', encoding="utf-8")

    def test_01_vanilla_contract_parity_default_true_emits_all_archetype_contracts(self) -> None:
        """VanillaSynthesisEngine defaults contract_parity=True and injects all symbols/transitions/endpoints cleanly."""
        engine = VanillaSynthesisEngine()
        self.assertTrue(engine.contract_parity)

        for arch_id in ("axioma_raft", "axioma_kv", "axioma_resp", "axioma_micro"):
            arch = get_archetype_by_id(arch_id)
            target_dir = self.scratch / f"vanilla_{arch_id}"
            target_dir.mkdir(parents=True, exist_ok=True)
            (target_dir / "run.py").write_text("print('ok')\n", encoding="utf-8")

            captured_prompt = {"text": ""}

            def capture_invoker(role: str, prompt: str, model: str) -> str:
                captured_prompt["text"] = prompt
                return f"cid_vanilla_{arch_id}"

            res = engine.synthesize(arch, target_dir, subagent_invoker=capture_invoker)
            self.assertTrue(res.success)
            prompt = captured_prompt["text"]

            # All expected models, verbs, endpoints, and state transitions must appear in prompt
            for model_name in arch.expected_models:
                self.assertIn(model_name, prompt, f"Missing model '{model_name}' in {arch_id} Vanilla prompt")
            for verb in arch.expected_verbs:
                self.assertIn(verb, prompt, f"Missing verb '{verb}' in {arch_id} Vanilla prompt")
            for ep in arch.expected_endpoints:
                self.assertIn(ep, prompt, f"Missing endpoint '{ep}' in {arch_id} Vanilla prompt")
            for tr in arch.state_transitions:
                self.assertIn(str(tr["action"]), prompt, f"Missing transition action '{tr['action']}' in {arch_id}")
                self.assertIn(str(tr["from"]), prompt)
                self.assertIn(str(tr["to"]), prompt)

            # Standard hygiene constraints present, zero Meta-Axioma internal artifact leakage
            self.assertIn("--smoke-test", prompt)
            self.assertIn("argparse", prompt)
            self.assertIn("/tmp", prompt)
            for forbidden_internal in ("AcceptanceSpecIR", "ResearchDeliverableBundle", "SystemG4bCompiler"):
                self.assertNotIn(forbidden_internal, prompt)

            # Manifest records contract_parity: true
            manifest = json.loads((target_dir / "synthesis_manifest.json").read_text(encoding="utf-8"))
            self.assertIs(manifest["contract_parity"], True)
            self.assertIs(manifest["is_multi_agent"], False)

    def test_02_vanilla_legacy_mode_contract_parity_false_and_runner_ledger(self) -> None:
        """contract_parity=False preserves legacy prose-only mode and records false in manifest & runner ledger."""
        arch = get_archetype_by_id("axioma_kv")
        target_dir = self.scratch / "vanilla_legacy_kv"
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "run.py").write_text(
            "import sys\nif '--smoke-test' in sys.argv:\n    print('OK', flush=True)\n    sys.exit(0)\n",
            encoding="utf-8",
        )
        cid = "cid_legacy_vanilla_1"
        self._create_transcript(cid)

        captured_prompt = {"text": ""}

        def invoker(role: str, prompt: str, model: str) -> str:
            captured_prompt["text"] = prompt
            return cid

        runner = CausalPipelineRunner(
            workspace_root=self.scratch,
            enable_provenance=True,
            reports_dir=self.scratch / "reports",
            vanilla_contract_parity=False,
        )
        runner.gauntlet.provenance_evaluator.app_data_dir = self.app_data

        cfg = BenchmarkTrialConfig(
            system_id="antigravity_vanilla",
            system_name="Vanilla Legacy",
            archetype_id="axioma_kv",
            trial=1,
            target_dir=target_dir,
            mode=AblationMode.FLAT_PROMPT_LLM,
        )
        ledger = runner.run_benchmark_matrix([cfg], subagent_invoker=invoker, report_prefix="parity_legacy")

        self.assertNotIn("Explicit Interface Contract", captured_prompt["text"])
        self.assertNotIn("KeyValueEntry", captured_prompt["text"])

        manifest = json.loads((target_dir / "synthesis_manifest.json").read_text(encoding="utf-8"))
        self.assertIs(manifest["contract_parity"], False)
        self.assertIs(ledger["vanilla_contract_parity"], False)
        self.assertIs(ledger["runs"][0]["contract_parity"], False)


if __name__ == "__main__":
    unittest.main()
