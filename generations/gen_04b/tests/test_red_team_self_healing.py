"""Unit & Integration Tests for Blocking Red Team Self-Healing & LOCAL_IPC Bind-Host Reconciliation.

Verifies:
- Structured `RedTeamVerdict` triggers bounded remediation loop (`max_remediation_cycles=2`)
  through `PHASE_3_REMEDIATION -> PHASE_2A_BUILD -> PHASE_2B_GROUNDING -> PHASE_2C_QA -> PHASE_3_AUDIT`.
- Fail-closed certification: unresolved criticals after exhausting cycles record
  `red_team_passed=False`, `critical_vulnerabilities_found > 0`, `governance_certified=False`
  in BOTH `CompilationReport` and `synthesis_manifest.json`.
- Multi-cycle anti-collusion (`cid_qa not in builder_cids`) and QA `tests/` tamper protection.
- Non-contradictory `LOCAL_IPC` (`"0.0.0.0"` allowed, loopback banned) vs `SOVEREIGN_MESH` (`"0.0.0.0"` banned).
"""

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

from generations.gen_04b.compiler import (
    CompilationPhase,
    CompilationRequest,
    RedTeamVerdict,
    SystemG4bCompiler,
)
from generations.gen_04b.protocols.acceptance_spec import DomainArchetype
from generations.gen_04b.protocols.ipc_transport import TransportMode
from generations.gen_04b.services.governance.src.negative_axiom_enforcer import (
    NegativeAxiomEnforcer,
)


class TestRedTeamSelfHealingAndBindHostPolicy(unittest.TestCase):
    """Verifies blocking Red Team self-healing loop, fail-closed certification, and 0.0.0.0 reconciliation."""

    def setUp(self) -> None:
        self.scratch_dir = REPO_ROOT / ".scratch" / f"test_rt_heal_{uuid.uuid4().hex[:8]}"
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        self.compiler = SystemG4bCompiler(transport_mode=TransportMode.LOCAL_IPC, repo_root=REPO_ROOT)

    def tearDown(self) -> None:
        shutil.rmtree(self.scratch_dir, ignore_errors=True)

    def test_01_red_team_verdict_triggers_bounded_remediation_and_succeeds(self) -> None:
        """Red Team failure on cycle 0 triggers Builder->Grounding->Blind QA->Audit remediation and succeeds on cycle 1."""
        out_dir = self.scratch_dir / "remediate_succeed"
        calls: list[tuple[str, str]] = []
        rt_attempt = {"count": 0}

        def invoker(role: str, prompt: str, model: str) -> str:
            calls.append((role, prompt))
            cid = f"{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
            if role == "Dialectical Red Team Architect":
                idx = rt_attempt["count"]
                rt_attempt["count"] += 1
                verdict_path = out_dir / "red_team_verdict.json"
                if idx == 0:
                    verdict_path.write_text(
                        json.dumps({
                            "red_team_pass": False,
                            "critical_vulnerabilities_found": 2,
                            "findings": [
                                "[CRIT-01] OverflowError on 10**400 latency_ms",
                                "[CRIT-02] PEP 475 SIGINT hang on open stdin",
                            ],
                            "cycle": 0,
                        }),
                        encoding="utf-8",
                    )
                else:
                    verdict_path.write_text(
                        json.dumps({
                            "red_team_pass": True,
                            "critical_vulnerabilities_found": 0,
                            "findings": [],
                            "cycle": idx,
                        }),
                        encoding="utf-8",
                    )
            return cid

        req = CompilationRequest(
            app_id="rt_heal_ok",
            app_name="RT Heal OK",
            target_output_dir=out_dir,
            waterloo_soc_prompt="Compile app and self-heal Red Team findings.",
            domain_archetype=DomainArchetype.CLI_SYSTEM_TOOL.value,
            max_remediation_cycles=2,
            subagent_invoker=invoker,
            require_live_subagents=True,
        )
        report = self.compiler.compile(req)

        self.assertTrue(report.success, f"Expected self-healed success, got: {report.error_message}")
        self.assertTrue(report.red_team_passed)
        self.assertEqual(report.critical_vulnerabilities_found, 0)
        self.assertTrue(report.governance_certified)
        self.assertTrue(report.audit_passed)
        self.assertEqual(report.remediation_cycles_executed, 1)
        self.assertIn(CompilationPhase.PHASE_3_REMEDIATION.value, report.phases_executed)

        # Verify Builder received exact concrete Red Team findings on remediation call
        builder_prompts = [p for r, p in calls if r == "Core Engine Synthesizer"]
        self.assertEqual(len(builder_prompts), 2)
        self.assertIn("[CRIT-01] OverflowError on 10**400 latency_ms", builder_prompts[1])
        self.assertIn("[CRIT-02] PEP 475 SIGINT hang on open stdin", builder_prompts[1])

        # Verify fresh Blind QA & Red Team ran twice (initial + 1 remediation)
        self.assertEqual(sum(1 for r, _ in calls if r == "Adversarial Byzantine QA Engineer"), 2)
        self.assertEqual(sum(1 for r, _ in calls if r == "Dialectical Red Team Architect"), 2)

        # Verify manifest persistence
        manifest = json.loads((out_dir / "synthesis_manifest.json").read_text(encoding="utf-8"))
        self.assertIs(manifest["red_team_passed"], True)
        self.assertEqual(manifest["critical_vulnerabilities_found"], 0)
        self.assertIs(manifest["governance_certified"], True)
        self.assertEqual(manifest["remediation_cycles_executed"], 1)

    def test_02_fail_closed_certification_when_criticals_persist_after_max_cycles(self) -> None:
        """Exhausting max_remediation_cycles with open criticals MUST fail closed in report and manifest."""
        out_dir = self.scratch_dir / "remediate_fail_closed"
        rt_calls = {"count": 0}

        def persistent_fail_invoker(role: str, prompt: str, model: str) -> object:
            cid = f"{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
            if role == "Dialectical Red Team Architect":
                c = rt_calls["count"]
                rt_calls["count"] += 1
                return {
                    "conversation_id": cid,
                    "red_team_pass": False,
                    "critical_vulnerabilities_found": 3,
                    "findings": [
                        "[CRIT-01] Split-brain dual leader",
                        "[CRIT-02] Unbounded Content-Length",
                        "[CRIT-03] Truncated body accepted",
                    ],
                    "cycle": c,
                }
            return cid

        req = CompilationRequest(
            app_id="rt_fail_closed",
            app_name="RT Fail Closed",
            target_output_dir=out_dir,
            waterloo_soc_prompt="Compile app where Red Team criticals persist across all remediation cycles.",
            domain_archetype=DomainArchetype.DISTRIBUTED_MESH_BACKEND.value,
            max_remediation_cycles=2,
            subagent_invoker=persistent_fail_invoker,
            require_live_subagents=True,
        )
        report = self.compiler.compile(req)

        # Exhausted exactly 2 remediation cycles (total 3 Red Team audits: cycles 0, 1, 2)
        self.assertEqual(rt_calls["count"], 3)
        self.assertEqual(report.remediation_cycles_executed, 2)

        # Fail-closed certification assertions
        self.assertFalse(report.success)
        self.assertFalse(report.red_team_passed)
        self.assertEqual(report.critical_vulnerabilities_found, 3)
        self.assertFalse(report.governance_certified)
        self.assertFalse(report.audit_passed)
        self.assertIsNotNone(report.error_message)
        self.assertIn("Fail-closed certification blocked", report.error_message or "")

        # Physical synthesis_manifest.json MUST record fail-closed state (never certify True!)
        manifest_path = out_dir / "synthesis_manifest.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertIs(manifest["red_team_passed"], False)
        self.assertEqual(manifest["critical_vulnerabilities_found"], 3)
        self.assertIs(manifest["governance_certified"], False)
        self.assertIs(manifest["audit_passed"], False)
        self.assertEqual(manifest["remediation_cycles_executed"], 2)

    def test_03_remediation_blocks_builder_qa_collusion_and_test_tampering(self) -> None:
        """Verifies remediation rejects Builder/QA CID reuse and blocks Builder deleting QA tests."""
        # Case A: Multi-cycle anti-collusion (QA on cycle 1 reuses Builder's cycle-0 CID)
        out_collude = self.scratch_dir / "rem_collude"
        shared_builder_cid = f"builder_shared_{uuid.uuid4().hex[:8]}"
        qa_count = {"n": 0}

        def collude_invoker(role: str, prompt: str, model: str) -> object:
            if role == "Core Engine Synthesizer":
                return shared_builder_cid
            if role == "Adversarial Byzantine QA Engineer":
                qa_count["n"] += 1
                return f"qa_clean_{uuid.uuid4().hex[:8]}" if qa_count["n"] == 1 else shared_builder_cid
            if role == "Dialectical Red Team Architect":
                return {
                    "conversation_id": f"rt_{uuid.uuid4().hex[:8]}",
                    "red_team_pass": False,
                    "critical_vulnerabilities_found": 1,
                    "findings": ["[CRIT-01] Forced remediation"],
                }
            return f"brain_{uuid.uuid4().hex[:8]}"

        rep_collude = self.compiler.compile(
            CompilationRequest(
                app_id="rem_collude_app",
                app_name="Rem Collude",
                target_output_dir=out_collude,
                waterloo_soc_prompt="Test multi-cycle anti-collusion.",
                max_remediation_cycles=1,
                subagent_invoker=collude_invoker,
                require_live_subagents=True,
            )
        )
        self.assertFalse(rep_collude.success)
        self.assertIn("Anti-collusion violation", rep_collude.error_message or "")

        # Case B: Builder deletes tests/test_smoke.py during remediation
        out_tamper = self.scratch_dir / "rem_tamper"
        b_count = {"n": 0}

        def tamper_invoker(role: str, prompt: str, model: str) -> object:
            if role == "Core Engine Synthesizer":
                b_count["n"] += 1
                if b_count["n"] == 2:
                    smoke_t = out_tamper / "tests" / "test_smoke.py"
                    if smoke_t.exists():
                        smoke_t.unlink()
                return f"builder_{b_count['n']}_{uuid.uuid4().hex[:6]}"
            if role == "Dialectical Red Team Architect":
                return {
                    "conversation_id": f"rt_{uuid.uuid4().hex[:8]}",
                    "red_team_pass": False,
                    "critical_vulnerabilities_found": 1,
                    "findings": ["[CRIT-01] Forced remediation"],
                }
            return f"{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

        rep_tamper = self.compiler.compile(
            CompilationRequest(
                app_id="rem_tamper_app",
                app_name="Rem Tamper",
                target_output_dir=out_tamper,
                waterloo_soc_prompt="Test QA test-suite tamper protection during remediation.",
                max_remediation_cycles=1,
                subagent_invoker=tamper_invoker,
                require_live_subagents=True,
            )
        )
        self.assertFalse(rep_tamper.success)
        self.assertIn("NEG-G4B-TAMPER", rep_tamper.error_message or "")

    def test_04_local_ipc_allows_0000_bind_host_while_sovereign_mesh_bans_it(self) -> None:
        """Resolves 0.0.0.0 bind-host contradiction cleanly between LOCAL_IPC and SOVEREIGN_MESH."""
        enforcer = NegativeAxiomEnforcer(service_endpoint="192.168.40.50:8448")
        wildcard_code = 'DEFAULT_HOST = "0.0.0.0"\n'
        loopback_code = 'DEFAULT_HOST = "127.0.0.1"\n'

        # SOVEREIGN_MESH (default): bans BOTH 0.0.0.0 and 127.0.0.1
        self.assertGreater(len(enforcer.scan_source_code(wildcard_code, "srv.py", runtime_profile="SOVEREIGN_MESH")), 0)
        self.assertGreater(len(enforcer.scan_source_code(loopback_code, "srv.py", runtime_profile="SOVEREIGN_MESH")), 0)

        # LOCAL_IPC: permits clean literal "0.0.0.0", while still banning loopback "127.0.0.1" / "localhost" / "::1"
        self.assertEqual(len(enforcer.scan_source_code(wildcard_code, "srv.py", runtime_profile="LOCAL_IPC")), 0)
        self.assertGreater(len(enforcer.scan_source_code(loopback_code, "srv.py", runtime_profile="LOCAL_IPC")), 0)
        self.assertGreater(len(enforcer.scan_source_code('H = "localhost"\n', "srv.py", runtime_profile="LOCAL_IPC")), 0)

        # End-to-end compile under LOCAL_IPC with literal "0.0.0.0" succeeds without obfuscation
        out_dir = self.scratch_dir / "clean_0000_app"

        def clean_bind_invoker(role: str, prompt: str, model: str) -> str:
            if role == "Core Engine Synthesizer":
                (out_dir / "src").mkdir(parents=True, exist_ok=True)
                (out_dir / "src" / "bind_cfg.py").write_text('DEFAULT_BIND_HOST = "0.0.0.0"\n', encoding="utf-8")
            return f"{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

        report = self.compiler.compile(
            CompilationRequest(
                app_id="clean_0000_bind",
                app_name="Clean 0.0.0.0 Bind",
                target_output_dir=out_dir,
                waterloo_soc_prompt="Verify literal 0.0.0.0 compiles cleanly under LOCAL_IPC.",
                domain_archetype=DomainArchetype.DISTRIBUTED_MESH_BACKEND.value,
                transport_mode=TransportMode.LOCAL_IPC.value,
                subagent_invoker=clean_bind_invoker,
                require_live_subagents=True,
            )
        )
        self.assertTrue(report.success, f"Literal 0.0.0.0 should pass LOCAL_IPC compilation: {report.error_message}")
        self.assertTrue(report.governance_certified)


if __name__ == "__main__":
    unittest.main()
