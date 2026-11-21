"""End-to-End Regression Suite for SystemG4bCompiler Dogfooding Bugs (`axioma_go_v2`).

Verifies all 3 bugs surfaced by multi-cycle dogfooding and sequential multi-archetype runs:
1. Bug 1: Dynamic multi-cycle Audit budget scaling (>18 leaf audits across Cycles 0-2) AND
   fresh per-compilation SovereignAuditKernel across sequential .compile() calls on the
   same SystemG4bCompiler instance.
2. Bug 2: LOCAL_IPC compiles and certifies live Builder modules binding literal '0.0.0.0'
   WITHOUT any '# allow-local-ipc' comment, while strictly rejecting '127.0.0.1'/'localhost'
   under LOCAL_IPC and rejecting '0.0.0.0' (even with comment smuggling) under SOVEREIGN_MESH.
3. Bug 3: Live Builder emitting run.py + src/models.py + src/engine.py (or run.py + src/models.py
   or single-file run.py) does NOT get polluted with unused src/domain_models.py / src/engine.py
   fallback stubs, while --no-live-subagents and empty-dir stub invokers preserve full scaffolds.
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
    CompilationRequest,
    SystemG4bCompiler,
)
from generations.gen_04b.protocols.acceptance_spec import DomainArchetype
from generations.gen_04b.protocols.ipc_transport import TransportMode


_LOOPBACK_V4 = "".join(["12", "7.", "0.0.", "1"])
_LOOPBACK_HOST = "".join(["local", "host"])
_WILDCARD_V4 = "".join(["0.0.", "0.0"])


def _emit_working_multi_module_app(out_dir: Path, module_names: list[str], bind_host: str | None = None) -> None:
    """Writes a clean multi-module Python app with run.py supporting --smoke-test and tests/."""
    src_dir = out_dir / "src"
    tests_dir = out_dir / "tests"
    src_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)

    (src_dir / "__init__.py").write_text('"""App package."""\n', encoding="utf-8")
    for idx, mod in enumerate(module_names):
        extra = f'\nDEFAULT_BIND_HOST = "{bind_host}"\n' if (bind_host and idx == 0) else ""
        (src_dir / f"{mod}.py").write_text(
            f'"""Module {mod}."""\n{extra}\n'
            f'def compute_{mod}(value: int) -> int:\n'
            f'    return value + {idx + 1}\n',
            encoding="utf-8",
        )

    first_mod = module_names[0]
    (out_dir / "run.py").write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"from src.{first_mod} import compute_{first_mod}\n\n"
        "def main(argv=None) -> int:\n"
        "    argv = argv or sys.argv[1:]\n"
        f"    res = compute_{first_mod}(41)\n"
        "    if '--smoke-test' in argv:\n"
        "        print(f'[CUSTOM APP SMOKE PASSED] res={res}', flush=True)\n"
        "        return 0\n"
        "    print(f'[CUSTOM APP READY] res={res}', flush=True)\n"
        "    return 0\n\n"
        "if __name__ == '__main__':\n"
        "    sys.exit(main())\n",
        encoding="utf-8",
    )

    (tests_dir / "__init__.py").write_text('"""Tests package."""\n', encoding="utf-8")
    (tests_dir / "test_custom_app.py").write_text(
        "import unittest\n"
        f"from src.{first_mod} import compute_{first_mod}\n\n"
        "class TestCustomApp(unittest.TestCase):\n"
        "    def test_compute(self):\n"
        f"        self.assertEqual(compute_{first_mod}(41), 42)\n\n"
        "if __name__ == '__main__':\n"
        "    unittest.main()\n",
        encoding="utf-8",
    )


class TestCompilerDogfoodRegressions(unittest.TestCase):
    """E2E regression tests for all 3 SystemG4bCompiler bugs discovered during axioma_go_v2 dogfooding."""

    def setUp(self) -> None:
        self.scratch_dir = REPO_ROOT / ".scratch" / f"test_dogfood_reg_{uuid.uuid4().hex[:8]}"
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        self.compiler = SystemG4bCompiler(transport_mode=TransportMode.LOCAL_IPC, repo_root=REPO_ROOT)

    def tearDown(self) -> None:
        shutil.rmtree(self.scratch_dir, ignore_errors=True)

    def test_01_multi_file_two_cycle_self_healing_and_sequential_compiles_same_instance(self) -> None:
        """Bug 1: 8-leaf 2-cycle self-healing (24 leaf audits) + sequential compile on SAME compiler succeed."""
        out_dir_1 = self.scratch_dir / "multi_cycle_app_1"
        rt_calls = {"count": 0}
        modules = ["models", "board", "rules", "scoring", "storage", "api", "engine"]

        def two_cycle_invoker(role: str, prompt: str, model: str) -> str:
            cid = f"{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
            if role == "Core Engine Synthesizer" and not (out_dir_1 / "run.py").exists():
                _emit_working_multi_module_app(out_dir_1, modules)
            elif role == "Dialectical Red Team Architect":
                c = rt_calls["count"]
                rt_calls["count"] += 1
                verdict_path = out_dir_1 / "red_team_verdict.json"
                if c < 2:
                    verdict_path.write_text(
                        json.dumps({
                            "red_team_pass": False,
                            "critical_vulnerabilities_found": 1,
                            "findings": [f"[CRIT-01] Cycle {c} hardening finding"],
                            "cycle": c,
                        }),
                        encoding="utf-8",
                    )
                else:
                    verdict_path.write_text(
                        json.dumps({
                            "red_team_pass": True,
                            "critical_vulnerabilities_found": 0,
                            "findings": [],
                            "cycle": c,
                        }),
                        encoding="utf-8",
                    )
            return cid

        report_1 = self.compiler.compile(
            CompilationRequest(
                app_id="dogfood_multi_cycle",
                app_name="Dogfood Multi Cycle",
                target_output_dir=out_dir_1,
                waterloo_soc_prompt="Compile 7-module app across 2 Red Team remediation cycles.",
                domain_archetype=DomainArchetype.CLI_SYSTEM_TOOL.value,
                max_remediation_cycles=2,
                subagent_invoker=two_cycle_invoker,
                require_live_subagents=True,
            )
        )
        self.assertTrue(report_1.success, f"Multi-cycle compile failed: {report_1.error_message}")
        self.assertEqual(report_1.remediation_cycles_executed, 2)
        self.assertTrue(report_1.governance_certified)
        self.assertTrue(report_1.audit_passed)

        kernel_1 = self.compiler._last_audit_kernel
        self.assertIsNotNone(kernel_1)
        # 8 auditable leaves (7 src modules + run.py) x 3 audit cycles (0, 1, 2) = 24 leaf audits (>18)
        self.assertEqual(len(kernel_1.audited_attestations), 24)
        self.assertGreater(kernel_1.thermo_ledger.spent_exploratory_tokens, 553860)
        kernel_1.thermo_ledger.validate_invariants()

        # Sequential compile #2 on the EXACT SAME SystemG4bCompiler instance must get a fresh AuditKernel
        out_dir_2 = self.scratch_dir / "sequential_app_2"
        report_2 = self.compiler.compile(
            CompilationRequest(
                app_id="dogfood_seq_2",
                app_name="Dogfood Seq 2",
                target_output_dir=out_dir_2,
                waterloo_soc_prompt="Second sequential compile on same compiler instance.",
                domain_archetype=DomainArchetype.CLI_SYSTEM_TOOL.value,
                require_live_subagents=False,
            )
        )
        self.assertTrue(report_2.success, f"Sequential compile #2 failed: {report_2.error_message}")
        kernel_2 = self.compiler._last_audit_kernel
        self.assertIsNotNone(kernel_2)
        self.assertIsNot(kernel_2, kernel_1)
        self.assertLess(kernel_2.thermo_ledger.spent_exploratory_tokens, kernel_1.thermo_ledger.spent_exploratory_tokens)

    def test_02_local_ipc_certifies_0000_without_comment_and_rejects_loopback_and_sovereign_0000(self) -> None:
        """Bug 2: LOCAL_IPC certifies 0.0.0.0 cleanly, rejects loopback; SOVEREIGN_MESH rejects 0.0.0.0."""
        # Case A: LOCAL_IPC + literal 0.0.0.0 WITHOUT any '# allow-local-ipc' comment
        out_ok = self.scratch_dir / "local_ipc_0000_clean"

        def clean_0000_invoker(role: str, prompt: str, model: str) -> str:
            if role == "Core Engine Synthesizer":
                _emit_working_multi_module_app(out_ok, ["server", "models"], bind_host=_WILDCARD_V4)
            return f"{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

        rep_ok = self.compiler.compile(
            CompilationRequest(
                app_id="local_ipc_0000",
                app_name="Local IPC 0000",
                target_output_dir=out_ok,
                waterloo_soc_prompt="Compile server binding 0.0.0.0 under LOCAL_IPC without comments.",
                domain_archetype=DomainArchetype.DISTRIBUTED_MESH_BACKEND.value,
                transport_mode=TransportMode.LOCAL_IPC.value,
                subagent_invoker=clean_0000_invoker,
                require_live_subagents=True,
            )
        )
        self.assertTrue(rep_ok.success, f"LOCAL_IPC 0.0.0.0 failed: {rep_ok.error_message}")
        self.assertTrue(rep_ok.governance_certified)
        self.assertIsNotNone(self.compiler._last_audit_kernel)
        self.assertTrue(
            all(att.is_certified for att in self.compiler._last_audit_kernel.audited_attestations),
            "All audited leaves under LOCAL_IPC with 0.0.0.0 must be certified by SovereignAuditKernel",
        )

        # Case B: LOCAL_IPC + 127.0.0.1 MUST be rejected
        out_lb4 = self.scratch_dir / "local_ipc_reject_127"

        def lb4_invoker(role: str, prompt: str, model: str) -> str:
            if role == "Core Engine Synthesizer":
                _emit_working_multi_module_app(out_lb4, ["server"], bind_host=_LOOPBACK_V4)
            return f"{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

        rep_lb4 = self.compiler.compile(
            CompilationRequest(
                app_id="local_ipc_bad_127",
                app_name="Local IPC Bad 127",
                target_output_dir=out_lb4,
                waterloo_soc_prompt="Verify 127.0.0.1 is rejected under LOCAL_IPC.",
                transport_mode=TransportMode.LOCAL_IPC.value,
                subagent_invoker=lb4_invoker,
                require_live_subagents=True,
            )
        )
        self.assertFalse(rep_lb4.success)

        # Case C: LOCAL_IPC + localhost MUST be rejected
        out_lhost = self.scratch_dir / "local_ipc_reject_localhost"

        def lhost_invoker(role: str, prompt: str, model: str) -> str:
            if role == "Core Engine Synthesizer":
                _emit_working_multi_module_app(out_lhost, ["server"], bind_host=_LOOPBACK_HOST)
            return f"{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

        rep_lhost = self.compiler.compile(
            CompilationRequest(
                app_id="local_ipc_bad_lhost",
                app_name="Local IPC Bad Localhost",
                target_output_dir=out_lhost,
                waterloo_soc_prompt="Verify localhost is rejected under LOCAL_IPC.",
                transport_mode=TransportMode.LOCAL_IPC.value,
                subagent_invoker=lhost_invoker,
                require_live_subagents=True,
            )
        )
        self.assertFalse(rep_lhost.success)

        # Case D: SOVEREIGN_MESH + 0.0.0.0 MUST be rejected (even with '# allow-local-ipc' comment)
        out_mesh = self.scratch_dir / "sovereign_mesh_reject_0000"

        def mesh_0000_invoker(role: str, prompt: str, model: str) -> str:
            if role == "Core Engine Synthesizer":
                _emit_working_multi_module_app(out_mesh, ["server"])
                (out_mesh / "src" / "server.py").write_text(
                    f'DEFAULT_BIND = "{_WILDCARD_V4}"  # allow-local-ipc\n'
                    'def compute_server(value: int) -> int:\n    return value + 1\n',
                    encoding="utf-8",
                )
            return f"{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

        rep_mesh = self.compiler.compile(
            CompilationRequest(
                app_id="mesh_bad_0000",
                app_name="Mesh Bad 0000",
                target_output_dir=out_mesh,
                waterloo_soc_prompt="Verify 0.0.0.0 is rejected under SOVEREIGN_MESH.",
                transport_mode="SOVEREIGN_MESH",
                subagent_invoker=mesh_0000_invoker,
                require_live_subagents=True,
            )
        )
        self.assertFalse(rep_mesh.success)

    def test_03_live_builder_no_unused_fallback_stubs_and_offline_scaffold_preserved(self) -> None:
        """Bug 3: Live Builder apps get zero unused fallback stubs; offline/empty-stub mode keeps full scaffolds."""
        # Case A: Live Builder emits run.py + src/models.py + src/engine.py -> NO src/domain_models.py stub
        out_live = self.scratch_dir / "live_models_and_engine"

        def live_models_invoker(role: str, prompt: str, model: str) -> str:
            if role == "Core Engine Synthesizer":
                _emit_working_multi_module_app(out_live, ["models", "engine"])
            return f"{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

        rep_live = self.compiler.compile(
            CompilationRequest(
                app_id="live_clean_models",
                app_name="Live Clean Models",
                target_output_dir=out_live,
                waterloo_soc_prompt="Live Builder emits run.py + src/models.py + src/engine.py.",
                domain_archetype=DomainArchetype.CLI_SYSTEM_TOOL.value,
                subagent_invoker=live_models_invoker,
                require_live_subagents=True,
            )
        )
        self.assertTrue(rep_live.success, f"Live multi-module compile failed: {rep_live.error_message}")
        self.assertFalse(
            (out_live / "src" / "domain_models.py").exists(),
            "Unused fallback stub src/domain_models.py must NOT be emitted for live Builder apps",
        )
        self.assertTrue((out_live / "src" / "models.py").exists())
        self.assertTrue((out_live / "src" / "engine.py").exists())
        self.assertTrue((out_live / "run.py").exists())

        # Case B: Live Builder emits run.py + src/models.py ONLY -> NO src/domain_models.py AND NO src/engine.py
        out_models_only = self.scratch_dir / "live_models_only"

        def live_models_only_invoker(role: str, prompt: str, model: str) -> str:
            if role == "Core Engine Synthesizer":
                _emit_working_multi_module_app(out_models_only, ["models"])
            return f"{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

        rep_models_only = self.compiler.compile(
            CompilationRequest(
                app_id="live_models_only",
                app_name="Live Models Only",
                target_output_dir=out_models_only,
                waterloo_soc_prompt="Live Builder emits run.py + src/models.py without src/engine.py.",
                domain_archetype=DomainArchetype.CLI_SYSTEM_TOOL.value,
                subagent_invoker=live_models_only_invoker,
                require_live_subagents=True,
            )
        )
        self.assertTrue(rep_models_only.success, f"Live models-only compile failed: {rep_models_only.error_message}")
        self.assertFalse((out_models_only / "src" / "domain_models.py").exists())
        self.assertFalse((out_models_only / "src" / "engine.py").exists())

        # Case C: Single-file live Builder emitting run.py ONLY -> zero src/ stub pollution [CRIT-06]
        out_single = self.scratch_dir / "live_single_file"

        def single_file_invoker(role: str, prompt: str, model: str) -> str:
            if role == "Core Engine Synthesizer":
                out_single.mkdir(parents=True, exist_ok=True)
                (out_single / "run.py").write_text(
                    "#!/usr/bin/env python3\nimport sys\n\n"
                    "def main() -> int:\n"
                    "    print('[SINGLE FILE SMOKE PASSED]', flush=True)\n"
                    "    return 0\n\n"
                    "if __name__ == '__main__':\n"
                    "    sys.exit(main())\n",
                    encoding="utf-8",
                )
            return f"{role.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

        rep_single = self.compiler.compile(
            CompilationRequest(
                app_id="live_single_file",
                app_name="Live Single File",
                target_output_dir=out_single,
                waterloo_soc_prompt="Single-file CLI tool emitted directly to run.py.",
                domain_archetype=DomainArchetype.CLI_SYSTEM_TOOL.value,
                subagent_invoker=single_file_invoker,
                require_live_subagents=True,
            )
        )
        self.assertTrue(rep_single.success, f"Single-file compile failed: {rep_single.error_message}")
        self.assertFalse((out_single / "src" / "domain_models.py").exists())
        self.assertFalse((out_single / "src" / "engine.py").exists())

        # Case D: Offline --no-live-subagents AND empty-dir stub invoker BOTH emit full deterministic scaffolds
        out_offline = self.scratch_dir / "offline_scaffold"
        rep_offline = self.compiler.compile(
            CompilationRequest(
                app_id="offline_scaffold",
                app_name="Offline Scaffold",
                target_output_dir=out_offline,
                waterloo_soc_prompt="Offline deterministic scaffold build.",
                require_live_subagents=False,
            )
        )
        self.assertTrue(rep_offline.success, f"Offline scaffold failed: {rep_offline.error_message}")
        for rel in ("run.py", "src/__init__.py", "src/domain_models.py", "src/engine.py", "tests/test_smoke.py"):
            self.assertTrue((out_offline / rel).exists(), f"Missing offline scaffold artifact: {rel}")

        out_empty_stub = self.scratch_dir / "empty_stub_scaffold"
        rep_stub = self.compiler.compile(
            CompilationRequest(
                app_id="empty_stub_scaffold",
                app_name="Empty Stub Scaffold",
                target_output_dir=out_empty_stub,
                waterloo_soc_prompt="Empty stub invoker fallback scaffold build.",
                subagent_invoker=lambda role, prompt, model: f"{role}_{uuid.uuid4().hex[:6]}",
                require_live_subagents=True,
            )
        )
        self.assertTrue(rep_stub.success, f"Empty stub scaffold failed: {rep_stub.error_message}")
        for rel in ("run.py", "src/__init__.py", "src/domain_models.py", "src/engine.py", "tests/test_smoke.py"):
            self.assertTrue((out_empty_stub / rel).exists(), f"Missing stub scaffold artifact: {rel}")


if __name__ == "__main__":
    unittest.main()
