"""Comprehensive Test Suite for Machine-Readable Acceptance Contracts (`SPEC-G4B-RESEARCH-001`).

Tests:
1. FalsificationVector algebraic roundtrip, SHA-256 stability, and invariant enforcement.
2. AcceptanceSpecIR algebraic roundtrip, deterministic spec hashing, and invariant validation.
3. ResearchDeliverableBundle backward and forward compatibility with AcceptanceSpecIR.
4. DomainArchetypePresetCatalog validation across all 5 standard application archetypes.
5. AcceptanceSpecEmitter dynamic derivation from Waterloo Tier 1 Situations of Concern.
6. AcceptanceSpecEmitter physical file emission, asserting non-zero byte disk grounding.
7. Builder & Adversarial QA prompt contract generation.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from generations.gen_04b.protocols.acceptance_spec import (
    AcceptanceProtocolViolation,
    AcceptanceSpecIR,
    DomainArchetype,
    FalsificationVector,
    MutationType,
)
from generations.gen_04b.protocols.deliverable_bundle import (
    DeliverableProtocolViolation,
    ResearchDeliverableBundle,
)
from generations.gen_04b.services.research.src.spec_emitter import (
    AcceptanceSpecEmitter,
    DomainArchetypePresetCatalog,
)


class TestAcceptanceSpecContracts(unittest.TestCase):
    """Verifies complete adherence to SPEC-G4B-RESEARCH-001 and Option 2 specifications."""

    def setUp(self) -> None:
        self.sample_vector = FalsificationVector(
            vector_id="FV-TEST-001",
            target_file_relative_path="services/research/src/kernel.py",
            target_symbol_or_pattern="execute_exploration_step",
            mutation_type=MutationType.RETURN_EMPTY.value,
            expected_failure_exception="VerificationSinkFault",
            reversion_witness_required=True,
            description="Defect injection testing state machine verification sink",
        )

        self.sample_spec = AcceptanceSpecIR(
            spec_id="SPEC-TEST-G4B-001",
            feature_name="Dynamic Falsification Gate",
            target_enclave_path="generations/gen_04b/services/research/src/",
            domain_archetype=DomainArchetype.DISTRIBUTED_MESH_BACKEND.value,
            required_runtimes=["python3"],
            banned_ast_patterns=[
                {"pattern": "127.0.0.1", "reason": "No loopback"},
                {"pattern": "time.sleep", "reason": "No synchronous blocking sleep"},
            ],
            falsification_vectors=[self.sample_vector],
            max_latency_per_step_ms=45.0,
            zero_console_panics_required=True,
            min_statechart_coverage_pct=92.5,
            telemetry_digest_required=True,
            metadata={"origin": "unit_test"},
        )

    def test_01_falsification_vector_invariants_and_roundtrip(self) -> None:
        """Verifies FalsificationVector validation, serialization, and deserialization roundtrip."""
        self.sample_vector.validate_invariants()
        v_dict = self.sample_vector.to_dict()
        restored = FalsificationVector.from_dict(v_dict)
        self.assertEqual(restored, self.sample_vector)

        # Invariant checks
        with self.assertRaises(AcceptanceProtocolViolation):
            FalsificationVector(
                vector_id="",
                target_file_relative_path="kernel.py",
                target_symbol_or_pattern="fn",
                mutation_type=MutationType.COMMENT_OUT.value,
                expected_failure_exception="Fault",
            ).validate_invariants()

        with self.assertRaises(AcceptanceProtocolViolation):
            FalsificationVector(
                vector_id="FV-002",
                target_file_relative_path="kernel.py",
                target_symbol_or_pattern="fn",
                mutation_type="INVALID_MUTATION_KIND",
                expected_failure_exception="Fault",
            ).validate_invariants()

    def test_02_acceptance_spec_ir_invariants_and_roundtrip(self) -> None:
        """Verifies AcceptanceSpecIR validation, serialization, and roundtrip."""
        self.sample_spec.validate_invariants()
        spec_dict = self.sample_spec.to_dict()
        restored = AcceptanceSpecIR.from_dict(spec_dict)
        self.assertEqual(restored, self.sample_spec)

        # Invariant: latency must be strictly positive
        with self.assertRaises(AcceptanceProtocolViolation):
            AcceptanceSpecIR(
                spec_id="SPEC-FAIL",
                feature_name="Fail",
                target_enclave_path="path/",
                max_latency_per_step_ms=0.0,
            ).validate_invariants()

        # Invariant: min_statechart_coverage_pct must be in [0, 100]
        with self.assertRaises(AcceptanceProtocolViolation):
            AcceptanceSpecIR(
                spec_id="SPEC-FAIL",
                feature_name="Fail",
                target_enclave_path="path/",
                min_statechart_coverage_pct=105.0,
            ).validate_invariants()

        # Invariant: banned patterns must have 'pattern' and 'reason'
        with self.assertRaises(AcceptanceProtocolViolation):
            AcceptanceSpecIR(
                spec_id="SPEC-FAIL",
                feature_name="Fail",
                target_enclave_path="path/",
                banned_ast_patterns=[{"pattern": "bad"}],  # missing reason
            ).validate_invariants()

    def test_03_acceptance_spec_ir_deterministic_spec_hash(self) -> None:
        """Verifies SHA-256 deterministic spec hashing."""
        hash_1 = self.sample_spec.compute_spec_hash()
        hash_2 = self.sample_spec.compute_spec_hash()
        self.assertEqual(hash_1, hash_2)
        self.assertEqual(len(hash_1), 64)

        # Mutating a field produces a different hash
        modified_spec = AcceptanceSpecIR(
            spec_id=self.sample_spec.spec_id,
            feature_name=self.sample_spec.feature_name,
            target_enclave_path=self.sample_spec.target_enclave_path,
            domain_archetype=self.sample_spec.domain_archetype,
            required_runtimes=self.sample_spec.required_runtimes,
            banned_ast_patterns=self.sample_spec.banned_ast_patterns,
            falsification_vectors=self.sample_spec.falsification_vectors,
            max_latency_per_step_ms=50.0,  # Changed from 45.0
            zero_console_panics_required=self.sample_spec.zero_console_panics_required,
            min_statechart_coverage_pct=self.sample_spec.min_statechart_coverage_pct,
            telemetry_digest_required=self.sample_spec.telemetry_digest_required,
            metadata=self.sample_spec.metadata,
        )
        self.assertNotEqual(hash_1, modified_spec.compute_spec_hash())

    def test_04_deliverable_bundle_backward_compatibility(self) -> None:
        """Verifies ResearchDeliverableBundle works without acceptance_spec (None) for backward compatibility."""
        bundle_legacy = ResearchDeliverableBundle(
            bundle_id="BUNDLE-LEGACY-001",
            target_soc_id="SOC-LEGACY-001",
            hypothesis_id="HYP-001",
            constraint_analysis_id="CONST-001",
            failure_mode_id="FAIL-001",
            tradeoff_matrix_id="TRADE-001",
            reference_architecture_hash="a" * 64,
            merkle_root="b" * 64,
            is_certified=True,
            acceptance_spec=None,
        )
        bundle_legacy.validate_invariants()
        b_dict = bundle_legacy.to_dict()
        self.assertIsNone(b_dict["acceptance_spec"])

        restored = ResearchDeliverableBundle.from_dict(b_dict)
        self.assertIsNone(restored.acceptance_spec)
        self.assertEqual(restored.bundle_id, bundle_legacy.bundle_id)

    def test_05_deliverable_bundle_forward_compatibility_with_acceptance_spec(self) -> None:
        """Verifies ResearchDeliverableBundle preserves and validates embedded AcceptanceSpecIR."""
        bundle_modern = ResearchDeliverableBundle(
            bundle_id="BUNDLE-MODERN-001",
            target_soc_id="SOC-MODERN-001",
            hypothesis_id="HYP-002",
            constraint_analysis_id="CONST-002",
            failure_mode_id="FAIL-002",
            tradeoff_matrix_id="TRADE-002",
            reference_architecture_hash="c" * 64,
            merkle_root="d" * 64,
            is_certified=True,
            acceptance_spec=self.sample_spec,
        )
        bundle_modern.validate_invariants()
        b_dict = bundle_modern.to_dict()
        self.assertIsNotNone(b_dict["acceptance_spec"])

        restored = ResearchDeliverableBundle.from_dict(b_dict)
        self.assertIsNotNone(restored.acceptance_spec)
        self.assertEqual(restored.acceptance_spec, self.sample_spec)

    def test_06_domain_archetype_preset_catalog(self) -> None:
        """Verifies that DomainArchetypePresetCatalog provides profiles for all 5 archetypes."""
        archetypes = DomainArchetypePresetCatalog.list_archetypes()
        self.assertIn("WEB_CANVAS_INTERACTIVE", archetypes)
        self.assertIn("DISTRIBUTED_MESH_BACKEND", archetypes)
        self.assertIn("CLI_SYSTEM_TOOL", archetypes)
        self.assertIn("FORMAL_VERIFICATION_KERNEL", archetypes)
        self.assertIn("CUSTOM", archetypes)

        web_preset = DomainArchetypePresetCatalog.get_preset(DomainArchetype.WEB_CANVAS_INTERACTIVE)
        self.assertIn("node", web_preset["required_runtimes"])
        self.assertTrue(any("dom" in p["pattern"].lower() for p in web_preset["banned_ast_patterns"]))

        mesh_preset = DomainArchetypePresetCatalog.get_preset(DomainArchetype.DISTRIBUTED_MESH_BACKEND)
        self.assertTrue(any("127.0.0.1" in p["pattern"] for p in mesh_preset["banned_ast_patterns"]))
        self.assertTrue(any("time.sleep" in p["pattern"] for p in mesh_preset["banned_ast_patterns"]))

        cli_preset = DomainArchetypePresetCatalog.get_preset(DomainArchetype.CLI_SYSTEM_TOOL)
        self.assertIn("bash", cli_preset["required_runtimes"])
        self.assertTrue(any("sys.exit" in p["pattern"] for p in cli_preset["banned_ast_patterns"]))

        formal_preset = DomainArchetypePresetCatalog.get_preset(DomainArchetype.FORMAL_VERIFICATION_KERNEL)
        self.assertEqual(formal_preset["min_statechart_coverage_pct"], 100.0)

    def test_07_acceptance_spec_emitter_create_from_preset(self) -> None:
        """Verifies AcceptanceSpecEmitter creates compliant specs from presets."""
        emitter = AcceptanceSpecEmitter(researcher_id="test_emitter")
        spec = emitter.create_from_preset(
            archetype=DomainArchetype.WEB_CANVAS_INTERACTIVE,
            spec_id="SPEC-WEB-001",
            feature_name="Canvas Surface",
            target_enclave_path="apps/test_web/static/",
            custom_falsification_vectors=[self.sample_vector],
        )
        self.assertEqual(spec.domain_archetype, DomainArchetype.WEB_CANVAS_INTERACTIVE.value)
        self.assertIn("node", spec.required_runtimes)
        self.assertEqual(len(spec.falsification_vectors), 1)

    def test_08_acceptance_spec_emitter_derive_from_soc(self) -> None:
        """Verifies dynamic contract derivation from a mock Waterloo Tier 1 Situation of Concern."""
        mock_soc = {
            "soc_id": "SOC-MESH-CONSENSUS-001",
            "title": "Axioma Mesh Quorum Consensus",
            "narrative": "Distributed consensus requiring non-loopback network topologies across sovereign nodes.",
            "constraints": [
                {"description": "Enforce anti-loopback interface binding strictly across all nodes"},
                {"description": "No mock objects in operational testing enclaves"},
            ],
            "frictions": [
                {"title": "Network Partition Recovery Deadlock"},
                {"title": "Consensus Split Brain Anomaly"},
            ],
        }

        emitter = AcceptanceSpecEmitter()
        spec = emitter.derive_from_soc(
            soc=mock_soc,
            target_enclave_path="generations/gen_04b/services/audit/src/",
        )
        self.assertEqual(spec.spec_id, "SPEC-SOC-MESH-CONSENSUS-001")
        self.assertEqual(spec.domain_archetype, DomainArchetype.DISTRIBUTED_MESH_BACKEND.value)
        self.assertGreaterEqual(len(spec.banned_ast_patterns), 2)
        self.assertEqual(len(spec.falsification_vectors), 2)

    def test_09_physical_disk_emission_and_grounding(self) -> None:
        """Verifies emit_to_file creates a non-empty, parseable JSON contract on disk."""
        emitter = AcceptanceSpecEmitter()
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = Path(tmp_dir) / "acceptance_spec.json"
            emitted_path = emitter.emit_to_file(self.sample_spec, out_file)
            self.assertTrue(emitted_path.exists())
            self.assertGreater(emitted_path.stat().st_size, 0)

            # Reload and verify equality
            content = json.loads(emitted_path.read_text(encoding="utf-8"))
            reloaded = AcceptanceSpecIR.from_dict(content)
            self.assertEqual(reloaded, self.sample_spec)

    def test_10_prompt_contract_generation(self) -> None:
        """Verifies Builder and QA prompt string generation."""
        emitter = AcceptanceSpecEmitter()
        builder_contract = emitter.generate_builder_prompt_contract(self.sample_spec)
        self.assertIn("AcceptanceSpecIR: SPEC-TEST-G4B-001", builder_contract)
        self.assertIn("127.0.0.1", builder_contract)
        self.assertIn("FV-TEST-001", builder_contract)
        self.assertIn("SHA-256", builder_contract)

        qa_contract = emitter.generate_qa_falsification_contract(self.sample_spec)
        self.assertIn("SPEC-TEST-G4B-001", qa_contract)
        self.assertIn("Runtime Verification", qa_contract)
        self.assertIn("Physical Mutation Injections", qa_contract)


if __name__ == "__main__":
    unittest.main()
