"""Quarantined Blind QA Test Suite for Generation 4b Gemini 4 Cognitive Routing.

Verifies:
- Zero-flag invariance (`ENABLE_ARGON` unset, "0", or "1" produces identical routing).
- Zero Argon in active Gen 4b routing (`Gemini 4 Neon` for Brain/Red Team, `Gemini 4 Hydrogen` for Muscle).
- Discovery lite roles resolve to `Gemini4ModelTier.DISCOVERY_LITE` (`agy_model_param="flash_lite"`).
- Role normalization, case-insensitivity, `CognitiveRole` enum support, and `RoutingProtocolViolation` fail-closed guards.
- Strictly stdlib-only AST import hygiene for `generations/gen_04b/protocols/cognitive_routing.py`.
- `DynamicPersonaBuilder` & `CognitiveRole` alignment across Muscle (`"flash"`) and Brain/Auditor/Red-Team (`"pro"`) personas.
- Telemetry dashboard compiler (`schema.py`, `compiler.py`, `subagent_hud.py`) badge styling and historical `"Gemini 3.8 Flash"` / `"Gemini 4 Argon"` compatibility.
- End-to-end `SystemG4bCompiler.compile(...)` routing contract and `subagent_witnesses` verification under `.scratch/`.
"""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import generations.gen_04b.protocols as g4b_protocols
from generations.gen_04b.protocols.cognitive_routing import (
    BRAIN_ROLES,
    DISCOVERY_ROLES,
    MUSCLE_ROLES,
    RED_TEAM_ROLES,
    VALID_AGY_MODEL_PARAMS,
    Gemini4ModelTier,
    RoutingDecision,
    RoutingProtocolViolation,
    is_brain_model_label,
    resolve_role_routing,
)
from generations.gen_04b.compiler.orchestrator import (
    CompilationReport,
    CompilationRequest,
    SystemG4bCompiler,
)
from generations.gen_04b.protocols.acceptance_spec import DomainArchetype
from generations.gen_04b.protocols.ipc_transport import TransportMode
from generations.gen_04b.services.builder.src.domain_models import CognitiveRole
from generations.gen_04b.services.builder.src.dynamic_persona_builder import (
    DynamicPersonaBuilder,
)
from generations.gen_04b.services.telemetry.src.dashboard_compiler.compiler import (
    TelemetryDashboardCompiler,
)
from generations.gen_04b.services.telemetry.src.dashboard_compiler.schema import (
    DashboardAST,
    SubagentWitness,
)
from generations.gen_04b.services.telemetry.src.dashboard_compiler.subagent_hud import (
    render_subagent_hud,
)


class TestCognitiveRoutingProtocol(unittest.TestCase):
    """Tests for `generations/gen_04b/protocols/cognitive_routing.py` and exports."""

    def test_protocol_exports(self) -> None:
        """All cognitive routing symbols are exported cleanly from `protocols/__init__.py`."""
        expected_symbols = [
            "BRAIN_ROLES",
            "DISCOVERY_ROLES",
            "MUSCLE_ROLES",
            "RED_TEAM_ROLES",
            "VALID_AGY_MODEL_PARAMS",
            "Gemini4ModelTier",
            "RoutingDecision",
            "RoutingProtocolViolation",
            "is_brain_model_label",
            "resolve_role_routing",
        ]
        for sym in expected_symbols:
            self.assertTrue(hasattr(g4b_protocols, sym), f"Missing export {sym} in protocols")
            self.assertIn(sym, g4b_protocols.__all__)

    def test_zero_flag_invariance_across_enable_argon_states(self) -> None:
        """`ENABLE_ARGON` env var ('0', '1', or unset) has zero effect on routing decisions."""
        target_roles = (
            list(BRAIN_ROLES)
            + list(MUSCLE_ROLES)
            + list(DISCOVERY_ROLES)
        )
        env_variants = [
            {},  # unset
            {"ENABLE_ARGON": "0"},
            {"ENABLE_ARGON": "1"},
        ]

        baseline_decisions = {}
        for idx, env_patch in enumerate(env_variants):
            with patch.dict(os.environ, env_patch, clear=False):
                if not env_patch:
                    os.environ.pop("ENABLE_ARGON", None)
                for role in target_roles:
                    decision = resolve_role_routing(role)
                    if idx == 0:
                        baseline_decisions[role] = decision
                    else:
                        self.assertEqual(
                            decision,
                            baseline_decisions[role],
                            f"ENABLE_ARGON variant {env_patch} altered routing for {role}",
                        )

        # Explicitly verify Brain, Red Team, and Muscle expectations
        for brain_role in BRAIN_ROLES:
            d = baseline_decisions[brain_role]
            self.assertEqual(d.logical_tier, Gemini4ModelTier.BRAIN_NEON)
            self.assertEqual(d.agy_model_param, "pro")
            self.assertEqual(d.witness_model_label, "Gemini 4 Neon")
            self.assertTrue(d.is_brain)
            expected_tier = (
                "Red Team Gate (Brain)" if brain_role in RED_TEAM_ROLES else "Brain Gate"
            )
            self.assertEqual(d.display_tier, expected_tier)

        for muscle_role in MUSCLE_ROLES:
            d = baseline_decisions[muscle_role]
            self.assertEqual(d.logical_tier, Gemini4ModelTier.MUSCLE_HYDROGEN)
            self.assertEqual(d.agy_model_param, "flash")
            self.assertEqual(d.witness_model_label, "Gemini 4 Hydrogen")
            self.assertFalse(d.is_brain)
            self.assertEqual(d.display_tier, "Muscle")

    def test_zero_argon_in_active_routing(self) -> None:
        """No canonical role in BRAIN_ROLES | MUSCLE_ROLES | DISCOVERY_ROLES resolves to Argon or 3.8 Flash."""
        for tier in Gemini4ModelTier:
            self.assertNotIn("argon", tier.value.lower())
            self.assertNotIn("3.8 flash", tier.value.lower())

        all_canonical_roles = BRAIN_ROLES | MUSCLE_ROLES | DISCOVERY_ROLES
        self.assertGreater(len(all_canonical_roles), 0)
        for role in all_canonical_roles:
            decision = resolve_role_routing(role)
            serialized = json.dumps(decision.to_dict())
            self.assertNotIn("Argon", serialized)
            self.assertNotIn("argon", serialized.lower())
            self.assertNotIn("3.8 Flash", serialized)
            self.assertNotIn("3.8 flash", serialized.lower())
            self.assertIn(decision.agy_model_param, VALID_AGY_MODEL_PARAMS)

    def test_discovery_lite_roles(self) -> None:
        """Discovery roles resolve to DISCOVERY_LITE (`agy_model_param='flash_lite'`)."""
        self.assertGreater(len(DISCOVERY_ROLES), 0)
        for role in DISCOVERY_ROLES:
            decision = resolve_role_routing(role)
            self.assertEqual(decision.logical_tier, Gemini4ModelTier.DISCOVERY_LITE)
            self.assertEqual(decision.agy_model_param, "flash_lite")
            self.assertEqual(decision.witness_model_label, "Gemini 4 Hydrogen (Lite)")
            self.assertEqual(decision.display_tier, "Discovery (Lite)")
            self.assertFalse(decision.is_brain)

    def test_invalid_role_and_invalid_model_param_fail_closed(self) -> None:
        """Invalid role strings and invalid agy_model_param raise RoutingProtocolViolation."""
        for bad_role in ("", "   ", "UNKNOWN_MYSTERY_ROLE", "gemini_argon_override"):
            with self.assertRaises(RoutingProtocolViolation):
                resolve_role_routing(bad_role)

        for bad_param in ("", "Gemini 4 Neon", "argon", "3.8 Flash", "opus", "PRO"):
            with self.assertRaises(RoutingProtocolViolation):
                RoutingDecision(
                    cognitive_role="DOMAIN_ONTOLOGIST",
                    logical_tier=Gemini4ModelTier.BRAIN_NEON,
                    agy_model_param=bad_param,
                    display_tier="Brain Gate",
                    witness_model_label="Gemini 4 Neon",
                    is_brain=True,
                )

        # Valid AGY params succeed
        for valid_param in VALID_AGY_MODEL_PARAMS:
            rd = RoutingDecision(
                cognitive_role="DOMAIN_ONTOLOGIST",
                logical_tier=Gemini4ModelTier.BRAIN_NEON,
                agy_model_param=valid_param,
                display_tier="Brain Gate",
                witness_model_label="Gemini 4 Neon",
                is_brain=True,
            )
            self.assertEqual(rd.agy_model_param, valid_param)

    def test_role_normalization_case_insensitive_and_enum(self) -> None:
        """Case-insensitive strings, whitespace-padded strings, and CognitiveRole enums normalize cleanly."""
        d_lower = resolve_role_routing("domain_ontologist")
        d_padded = resolve_role_routing("  Domain_Ontologist \n")
        d_enum = resolve_role_routing(CognitiveRole.DOMAIN_ONTOLOGIST)
        self.assertEqual(d_lower, d_padded)
        self.assertEqual(d_lower, d_enum)
        self.assertEqual(d_lower.cognitive_role, "DOMAIN_ONTOLOGIST")
        self.assertEqual(d_lower.agy_model_param, "pro")

        d_rt_enum = resolve_role_routing(CognitiveRole.SOCRATIC_RED_TEAM)
        self.assertEqual(d_rt_enum.cognitive_role, "SOCRATIC_RED_TEAM")
        self.assertEqual(d_rt_enum.agy_model_param, "pro")
        self.assertEqual(d_rt_enum.display_tier, "Red Team Gate (Brain)")
        self.assertTrue(d_rt_enum.is_brain)

        d_qa_enum = resolve_role_routing(CognitiveRole.ADVERSARIAL_QA_ENGINEER)
        self.assertEqual(d_qa_enum.agy_model_param, "flash")
        self.assertFalse(d_qa_enum.is_brain)

        # Custom tier_label override is honored without mutating model routing
        d_custom = resolve_role_routing("CORE_ENGINE_SYNTHESIZER", tier_label="Muscle 1")
        self.assertEqual(d_custom.display_tier, "Muscle 1")
        self.assertEqual(d_custom.agy_model_param, "flash")
        self.assertEqual(d_custom.witness_model_label, "Gemini 4 Hydrogen")

    def test_ast_import_hygiene_stdlib_only(self) -> None:
        """`protocols/cognitive_routing.py` must import strictly stdlib (`__future__`, `dataclasses`, `enum`, `typing`)."""
        routing_path = REPO_ROOT / "generations" / "gen_04b" / "protocols" / "cognitive_routing.py"
        tree = ast.parse(routing_path.read_text(encoding="utf-8"), filename=str(routing_path))
        allowed_roots = {"__future__", "dataclasses", "enum", "typing"}
        imported_modules = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0, "Relative imports are prohibited in cognitive_routing.py")
                if node.module:
                    imported_modules.add(node.module.split(".")[0])

        self.assertTrue(imported_modules.issubset(allowed_roots), f"Disallowed imports: {imported_modules - allowed_roots}")
        self.assertNotIn("services", imported_modules)
        self.assertNotIn("generations", imported_modules)
        self.assertNotIn("os", imported_modules)


class TestDynamicPersonaBuilderAlignment(unittest.TestCase):
    """Tests for `DynamicPersonaBuilder` and `CognitiveRole` Gemini 4 routing alignment."""

    def test_muscle_personas_resolve_to_flash(self) -> None:
        """All Muscle builder/QA personas resolve to `model_tier='flash'`."""
        muscle_factories = [
            DynamicPersonaBuilder.create_quarantined_engine_synthesizer_persona,
            DynamicPersonaBuilder.create_adversarial_qa_persona,
            DynamicPersonaBuilder.create_ast_specialist_persona,
            DynamicPersonaBuilder.create_surgical_patcher_persona,
            DynamicPersonaBuilder.create_causal_qa_persona,
        ]
        for factory in muscle_factories:
            manifest = factory()
            manifest.validate_invariants()
            self.assertEqual(
                manifest.model_tier,
                "flash",
                f"{factory.__name__} expected model_tier='flash', got {manifest.model_tier}",
            )

    def test_brain_auditor_quine_red_team_personas_resolve_to_pro(self) -> None:
        """All Brain/Auditor/Quine/Red-Team personas resolve to `model_tier='pro'`."""
        brain_factories = [
            DynamicPersonaBuilder.create_hermetic_auditor_persona,
            DynamicPersonaBuilder.create_reactive_auditor_persona,
            DynamicPersonaBuilder.create_quine_crucible_persona,
            DynamicPersonaBuilder.create_socratic_red_team_persona,
        ]
        for factory in brain_factories:
            manifest = factory()
            manifest.validate_invariants()
            self.assertEqual(
                manifest.model_tier,
                "pro",
                f"{factory.__name__} expected model_tier='pro', got {manifest.model_tier}",
            )

    def test_to_define_subagent_params_preserves_keys_and_model_tier(self) -> None:
        """`to_define_subagent_params()` preserves required keys and includes `model_tier`."""
        required_keys = {
            "name",
            "description",
            "system_prompt",
            "model_tier",
            "enable_write_tools",
            "enable_mcp_tools",
            "enable_subagent_tools",
        }
        red_team_manifest = DynamicPersonaBuilder.create_socratic_red_team_persona()
        params = DynamicPersonaBuilder.to_define_subagent_params(red_team_manifest)
        self.assertTrue(required_keys.issubset(params.keys()))
        self.assertEqual(params["model_tier"], "pro")

        qa_manifest = DynamicPersonaBuilder.create_adversarial_qa_persona()
        qa_params = DynamicPersonaBuilder.to_define_subagent_params(qa_manifest)
        self.assertTrue(required_keys.issubset(qa_params.keys()))
        self.assertEqual(qa_params["model_tier"], "flash")


class TestTelemetryDashboardAndHUD(unittest.TestCase):
    """Tests for Telemetry Dashboard Compiler & Subagent HUD Gemini 4 styling & compatibility."""

    def test_subagent_witness_default_model(self) -> None:
        """`SubagentWitness` defaults `model` to `'Gemini 4 Hydrogen'`."""
        witness = SubagentWitness(
            conversation_id=str(uuid.uuid4()),
            role="Core Engine Synthesizer",
            phase="Phase 2A: Builder Muscle",
        )
        self.assertEqual(witness.model, "Gemini 4 Hydrogen")
        self.assertEqual(witness.tier, "Muscle")

    def test_is_brain_model_label_and_hud_badge_styling(self) -> None:
        """HUD styles Gemini 4 Neon & historical Argon as badge-purple; Hydrogen & 3.8 Flash as badge-cyan."""
        self.assertTrue(is_brain_model_label("Gemini 4 Neon", "Brain Gate"))
        self.assertTrue(is_brain_model_label("Gemini 4 Neon", "Red Team Gate (Brain)"))
        self.assertTrue(is_brain_model_label("Gemini 4 Argon", "Brain Gate"))
        self.assertTrue(is_brain_model_label("Custom", "Red Team Gate (Brain)"))
        self.assertFalse(is_brain_model_label("Gemini 4 Hydrogen", "Muscle"))
        self.assertFalse(is_brain_model_label("Gemini 3.8 Flash", "Muscle 1"))

        w_neon = SubagentWitness(
            conversation_id=str(uuid.uuid4()),
            role="Domain Ontologist & Systems Architect",
            phase="Phase 1: Research Gate",
            tier="Brain Gate",
            model="Gemini 4 Neon",
        )
        w_redteam = SubagentWitness(
            conversation_id=str(uuid.uuid4()),
            role="Dialectical Red Team Architect",
            phase="Phase 3: Red Team Gate",
            tier="Red Team Gate (Brain)",
            model="Gemini 4 Neon",
        )
        w_argon_archive = SubagentWitness(
            conversation_id=str(uuid.uuid4()),
            role="Legacy Brain Architect",
            phase="Phase 1: Historical Archive",
            tier="Brain Gate",
            model="Gemini 4 Argon",
        )
        w_hydrogen = SubagentWitness(
            conversation_id=str(uuid.uuid4()),
            role="Core Engine Synthesizer",
            phase="Phase 2A: Builder Muscle",
            tier="Muscle",
            model="Gemini 4 Hydrogen",
        )
        w_flash_archive = SubagentWitness(
            conversation_id=str(uuid.uuid4()),
            role="Legacy Muscle Synthesizer",
            phase="Phase 2A: Historical Archive",
            tier="Muscle 1",
            model="Gemini 3.8 Flash",
        )

        ast_obj = DashboardAST(
            app_id="hud_routing_probe",
            title="HUD Routing Probe",
            subtitle="Blind QA Verification",
            main_conversation_id=str(uuid.uuid4()),
            subagents=[w_neon, w_redteam, w_argon_archive, w_hydrogen, w_flash_archive],
        )
        hud_html = render_subagent_hud(ast_obj)
        self.assertIn('<span class="badge badge-purple">Gemini 4 Neon</span>', hud_html)
        self.assertIn('<span class="badge badge-purple">Gemini 4 Argon</span>', hud_html)
        self.assertIn('<span class="badge badge-cyan">Gemini 4 Hydrogen</span>', hud_html)
        self.assertIn('<span class="badge badge-cyan">Gemini 3.8 Flash</span>', hud_html)
        self.assertIn("Red Team Gate (Brain)", hud_html)
        self.assertIn("Brain Gate", hud_html)

    def test_historical_gemini_3_8_flash_telemetry_json_parses_cleanly(self) -> None:
        """Historical `telemetry_metrics.json` containing `Gemini 3.8 Flash` compiles cleanly."""
        scratch_root = REPO_ROOT / ".scratch"
        scratch_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch_root, prefix="qa_hist_tel_") as tmp_dir:
            tmp_path = Path(tmp_dir)
            historical_payload = {
                "app_id": "historical_probe",
                "main_conversation_id": str(uuid.uuid4()),
                "main_tokens": {
                    "input_fresh": 120000,
                    "cache_read": 2400000,
                    "output": 32000,
                    "steps": 42,
                },
                "subagents": [
                    {
                        "conversation_id": str(uuid.uuid4()),
                        "role": "Historical Brain",
                        "phase": "Phase 1: Brain Gate",
                        "tier": "Brain Gate",
                        "model": "Gemini 4 Argon",
                        "tokens_in": 40000,
                        "tokens_out": 12000,
                        "steps": 5,
                    },
                    {
                        "conversation_id": str(uuid.uuid4()),
                        "role": "Historical Muscle",
                        "phase": "Phase 2A: Muscle 1",
                        "tier": "Muscle 1",
                        "model": "Gemini 3.8 Flash",
                        "tokens_in": 80000,
                        "tokens_out": 20000,
                        "steps": 12,
                    },
                ],
            }
            (tmp_path / "telemetry_metrics.json").write_text(
                json.dumps(historical_payload, indent=2), encoding="utf-8"
            )

            ast_obj = TelemetryDashboardCompiler.build_ast_from_directory(
                tmp_path, strict_live_witness=True
            )
            self.assertEqual(len(ast_obj.subagents), 2)
            self.assertEqual(ast_obj.subagents[0].model, "Gemini 4 Argon")
            self.assertEqual(ast_obj.subagents[1].model, "Gemini 3.8 Flash")

            compiled_html = TelemetryDashboardCompiler.compile(ast_obj)
            self.assertIn('<span class="badge badge-purple">Gemini 4 Argon</span>', compiled_html)
            self.assertIn('<span class="badge badge-cyan">Gemini 3.8 Flash</span>', compiled_html)


class TestSystemG4bCompilerRoutingE2E(unittest.TestCase):
    """End-to-end `SystemG4bCompiler.compile(...)` routing contract verification."""

    def test_e2e_compile_routing_contract_and_witnesses(self) -> None:
        """Captures (role, model) pairs and verifies Gemini 4 Neon / Hydrogen witness records."""
        scratch_root = REPO_ROOT / ".scratch"
        scratch_root.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(dir=scratch_root, prefix="qa_e2e_routing_") as tmp_dir:
            out_dir = Path(tmp_dir) / "compiled_app"
            captured_calls: list[tuple[str, str]] = []
            role_cids = {
                "Domain Ontologist & Systems Architect": str(uuid.uuid4()),
                "Core Engine Synthesizer": str(uuid.uuid4()),
                "Adversarial Byzantine QA Engineer": str(uuid.uuid4()),
                "Dialectical Red Team Architect": str(uuid.uuid4()),
            }

            def recording_invoker(role: str, prompt: str, model: str) -> str:
                captured_calls.append((role, model))
                return role_cids[role]

            compiler = SystemG4bCompiler(
                transport_mode=TransportMode.LOCAL_IPC,
                repo_root=REPO_ROOT,
            )
            request = CompilationRequest(
                app_id="qa_routing_probe",
                app_name="QA Routing Probe",
                target_output_dir=out_dir,
                waterloo_soc_prompt=(
                    "Verify Gemini 4 Neon Brain/Red-Team and Hydrogen Muscle routing."
                ),
                domain_archetype=DomainArchetype.DISTRIBUTED_MESH_BACKEND.value,
                expected_verbs=["route", "attest"],
                transport_mode=TransportMode.LOCAL_IPC.value,
                subagent_invoker=recording_invoker,
                require_live_subagents=True,
            )

            # Verify zero-flag invariance even when ENABLE_ARGON="0"
            with patch.dict(os.environ, {"ENABLE_ARGON": "0"}, clear=False):
                report = compiler.compile(request)

            self.assertIsInstance(report, CompilationReport)
            self.assertTrue(
                report.success,
                f"Compilation failed unexpectedly: {report.error_message}",
            )
            self.assertTrue(report.audit_passed)
            self.assertTrue(report.governance_certified)

            expected_dispatches = [
                ("Domain Ontologist & Systems Architect", "pro"),
                ("Core Engine Synthesizer", "flash"),
                ("Adversarial Byzantine QA Engineer", "flash"),
                ("Dialectical Red Team Architect", "pro"),
            ]
            self.assertEqual(captured_calls, expected_dispatches)

            witness_by_phase = {w["phase"]: w for w in report.subagent_witnesses}
            self.assertEqual(len(witness_by_phase), 4)

            p1 = witness_by_phase["Phase 1: Research Gate"]
            self.assertEqual(p1["tier"], "Brain Gate")
            self.assertEqual(p1["model"], "Gemini 4 Neon")

            p2a = witness_by_phase["Phase 2A: Builder Muscle"]
            self.assertEqual(p2a["model"], "Gemini 4 Hydrogen")

            p2c = witness_by_phase["Phase 2C: Blind QA Gate"]
            self.assertEqual(p2c["model"], "Gemini 4 Hydrogen")

            p3 = witness_by_phase["Phase 3: Red Team Gate"]
            self.assertEqual(p3["tier"], "Red Team Gate (Brain)")
            self.assertEqual(p3["model"], "Gemini 4 Neon")

            witness_json = json.dumps(report.subagent_witnesses)
            self.assertNotIn("Argon", witness_json)
            self.assertNotIn("3.8 Flash", witness_json)

            dashboard_html = (out_dir / "dashboard.html").read_text(encoding="utf-8")
            self.assertIn('<span class="badge badge-purple">Gemini 4 Neon</span>', dashboard_html)
            self.assertIn('<span class="badge badge-cyan">Gemini 4 Hydrogen</span>', dashboard_html)
            self.assertNotIn("Gemini 4 Argon", dashboard_html)
            self.assertNotIn("Gemini 3.8 Flash", dashboard_html)


if __name__ == "__main__":
    unittest.main()
