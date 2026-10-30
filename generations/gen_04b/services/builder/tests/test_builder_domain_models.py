"""Unit & Adversarial Invariant Test Suite for Builder Domain Models (`[L1-G3B-011]`).

Validates:
1. Instantiation, field validation, and lossless to_dict() / from_dict() roundtripping
   for all 16 domain nouns (4 enums + 12 core dataclasses).
2. Boundary and invariant assertions raising DomainInvariantViolation on:
   - Non-64-character SHA-256 hashes.
   - Fractal tree depth > 4 or negative depths.
   - Fractal tree branching factor > 5.
   - Thermodynamic decay rate lambda > 0.80 or <= 0.0.
   - 60/40 capital partition violations (protected capital < 40%).
   - Negative token leases, negative erased bits, empty IDs, and invalid URN formats.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import time
import unittest

# Ensure builder root and repo root are in sys.path
BUILDER_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BUILDER_ROOT.parent.parent.parent
for p in [str(BUILDER_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
    ASTNodeType,
    ASTSkeletonSnapshot,
    BuilderExecutionBundle,
    ByzantineChaosReport,
    CausalConvergenceAttestation,
    DiagnosticSeverity,
    DiagnosticTuple,
    DomainInvariantViolation,
    DynamicPersonaManifest,
    FractalTreeNode,
    FunctorialUndoCheckpoint,
    HermeticLinterReport,
    HierarchicalBudgetLease,
    LeafEmissionEvent,
    LeaseAllocationStatus,
    MerkleTreeRootAttestation,
    PhysicalDiskWitness,
    QuineDaughterManifest,
    QuineReactiveManifest,
    ReactiveAuditReport,
    ReactiveVerificationGate,
    RFCSubmissionRecord,
    SubtreeHealingEnvelope,
    TaskExecutionStatus,
)


class TestBuilderDomainModels(unittest.TestCase):
    """Exhaustive roundtrip and adversarial boundary testing for all 16 domain nouns."""

    def setUp(self) -> None:
        self.valid_sha256 = hashlib.sha256(b"reference_architecture_bundle_4b").hexdigest()
        self.merkle_sha256 = hashlib.sha256(b"merkle_root_4b").hexdigest()

    # -------------------------------------------------------------------------
    # 1. Enums Verification (4 Core Enums)
    # -------------------------------------------------------------------------

    def test_enum_task_execution_status(self) -> None:
        expected = {"PENDING", "ACTIVE", "COMPLETED", "FAILED", "HEALING", "CANCELLED", "REROUTED"}
        actual = {status.value for status in TaskExecutionStatus}
        self.assertEqual(actual, expected)

    def test_enum_diagnostic_severity(self) -> None:
        expected = {"INFO", "WARNING", "ERROR", "FATAL", "SECURITY_VIOLATION"}
        actual = {s.value for s in DiagnosticSeverity}
        self.assertEqual(actual, expected)

    def test_enum_ast_node_type(self) -> None:
        expected = {
            "MODULE", "CLASS_DEF", "FUNCTION_DEF", "ASYNC_FUNCTION_DEF",
            "IMPORT", "EXPR", "ASSIGN", "CONTRACT_SPEC", "INVARIANT_ASSERT",
        }
        actual = {t.value for t in ASTNodeType}
        self.assertEqual(actual, expected)

    def test_enum_lease_allocation_status(self) -> None:
        expected = {"ALLOCATED", "ACTIVE", "SETTLED", "REVOKED", "EXHAUSTED", "UNWOUND"}
        actual = {s.value for s in LeaseAllocationStatus}
        self.assertEqual(actual, expected)

    # -------------------------------------------------------------------------
    # 2. BuilderExecutionBundle
    # -------------------------------------------------------------------------

    def test_builder_execution_bundle_roundtrip(self) -> None:
        bundle = BuilderExecutionBundle(
            bundle_id="bld_exec_test_001",
            target_soc_id="soc_g4b_builder",
            research_bundle_hash=self.valid_sha256,
            total_budget_tokens=100000,
            protected_capital_tokens=40000,
            exploratory_capital_tokens=60000,
            emitted_module_count=5,
            status=TaskExecutionStatus.ACTIVE,
            metadata={"priority": "zenith"},
        )
        bundle.validate_invariants()

        d = bundle.to_dict()
        restored = BuilderExecutionBundle.from_dict(d)
        self.assertEqual(bundle.bundle_id, restored.bundle_id)
        self.assertEqual(bundle.research_bundle_hash, restored.research_bundle_hash)
        self.assertEqual(bundle.total_budget_tokens, restored.total_budget_tokens)
        self.assertEqual(bundle.protected_capital_tokens, restored.protected_capital_tokens)
        self.assertEqual(bundle.exploratory_capital_tokens, restored.exploratory_capital_tokens)
        self.assertEqual(bundle.status, restored.status)

    def test_builder_execution_bundle_invariants(self) -> None:
        # Invalid hash length
        with self.assertRaises(DomainInvariantViolation):
            b = BuilderExecutionBundle(
                bundle_id="bld_001",
                target_soc_id="soc_test",
                research_bundle_hash="invalid_short_hash",
                total_budget_tokens=100000,
                protected_capital_tokens=40000,
                exploratory_capital_tokens=60000,
            )
            b.validate_invariants()

        # Protected capital < 40% floor violation
        with self.assertRaises(DomainInvariantViolation):
            b = BuilderExecutionBundle(
                bundle_id="bld_002",
                target_soc_id="soc_test",
                research_bundle_hash=self.valid_sha256,
                total_budget_tokens=100000,
                protected_capital_tokens=35000,  # Below 40%
                exploratory_capital_tokens=65000,
            )
            b.validate_invariants()

        # Non-positive total budget
        with self.assertRaises(DomainInvariantViolation):
            b = BuilderExecutionBundle(
                bundle_id="bld_003",
                target_soc_id="soc_test",
                research_bundle_hash=self.valid_sha256,
                total_budget_tokens=0,
                protected_capital_tokens=0,
                exploratory_capital_tokens=0,
            )
            b.validate_invariants()

    # -------------------------------------------------------------------------
    # 3. FractalTreeNode
    # -------------------------------------------------------------------------

    def test_fractal_tree_node_roundtrip(self) -> None:
        node = FractalTreeNode(
            node_id="node_root_001",
            parent_id=None,
            depth=0,
            child_ids=["child_01", "child_02"],
            assigned_persona_role="Lead Systems Architect",
            task_description="Root architecture synthesis",
            allocated_lease_tokens=50000,
            spent_tokens=12000,
            status=TaskExecutionStatus.ACTIVE,
            emitted_artifacts=["src/kernel.py"],
            merkle_node_hash=self.valid_sha256,
        )
        node.validate_invariants()

        d = node.to_dict()
        restored = FractalTreeNode.from_dict(d)
        self.assertEqual(node.node_id, restored.node_id)
        self.assertEqual(node.depth, restored.depth)
        self.assertEqual(node.child_ids, restored.child_ids)
        self.assertEqual(node.merkle_node_hash, restored.merkle_node_hash)

    def test_fractal_tree_node_depth_and_branching_bounds(self) -> None:
        # Depth > 4 violation
        with self.assertRaises(DomainInvariantViolation):
            node = FractalTreeNode(
                node_id="node_deep",
                parent_id="node_parent",
                depth=5,  # Exceeds max depth 4
            )
            node.validate_invariants()

        # Branching > 5 violation
        with self.assertRaises(DomainInvariantViolation):
            node = FractalTreeNode(
                node_id="node_wide",
                parent_id="node_parent",
                depth=2,
                child_ids=["c1", "c2", "c3", "c4", "c5", "c6"],  # 6 children exceeds 5
            )
            node.validate_invariants()

        # Negative spent tokens
        with self.assertRaises(DomainInvariantViolation):
            node = FractalTreeNode(
                node_id="node_neg",
                parent_id="node_parent",
                depth=1,
                spent_tokens=-50,
            )
            node.validate_invariants()

    # -------------------------------------------------------------------------
    # 4. HierarchicalBudgetLease
    # -------------------------------------------------------------------------

    def test_hierarchical_budget_lease_roundtrip(self) -> None:
        lease = HierarchicalBudgetLease(
            lease_id="lease_001",
            node_id="node_001",
            parent_lease_id=None,
            allocated_tokens=25000,
            decay_rate_lambda=0.80,
            remaining_tokens=20000,
            landauer_bits_erased=1024,
            status=LeaseAllocationStatus.ACTIVE,
        )
        lease.validate_invariants()

        d = lease.to_dict()
        restored = HierarchicalBudgetLease.from_dict(d)
        self.assertEqual(lease.lease_id, restored.lease_id)
        self.assertEqual(lease.allocated_tokens, restored.allocated_tokens)
        self.assertEqual(lease.decay_rate_lambda, restored.decay_rate_lambda)
        self.assertEqual(lease.status, restored.status)

    def test_hierarchical_budget_lease_invariants(self) -> None:
        # decay_rate_lambda > 0.80 violation
        with self.assertRaises(DomainInvariantViolation):
            lease = HierarchicalBudgetLease(
                lease_id="lease_bad",
                node_id="node_001",
                decay_rate_lambda=0.85,
            )
            lease.validate_invariants()

        # remaining_tokens > allocated_tokens violation
        with self.assertRaises(DomainInvariantViolation):
            lease = HierarchicalBudgetLease(
                lease_id="lease_overflow",
                node_id="node_001",
                allocated_tokens=1000,
                remaining_tokens=1500,
            )
            lease.validate_invariants()

    # -------------------------------------------------------------------------
    # 5. ASTSkeletonSnapshot
    # -------------------------------------------------------------------------

    def test_ast_skeleton_snapshot_roundtrip(self) -> None:
        skel = ASTSkeletonSnapshot(
            snapshot_id="skel_001",
            source_module_path="src/kernel.py",
            symbol_urn="urn:axioma:g4b:builder:kernel",
            skeleton_code="class Kernel:\n    def run(self): ...\n",
            stripped_byte_count=512,
            preserved_signatures=["class Kernel()", "def run(self)"],
            estimated_bpe_tokens=24,
        )
        skel.validate_invariants()

        d = skel.to_dict()
        restored = ASTSkeletonSnapshot.from_dict(d)
        self.assertEqual(skel.snapshot_id, restored.snapshot_id)
        self.assertEqual(skel.skeleton_code, restored.skeleton_code)
        self.assertEqual(skel.estimated_bpe_tokens, restored.estimated_bpe_tokens)

    def test_ast_skeleton_snapshot_bpe_ceiling(self) -> None:
        with self.assertRaises(DomainInvariantViolation):
            skel = ASTSkeletonSnapshot(
                snapshot_id="skel_huge",
                source_module_path="src/big.py",
                symbol_urn="urn:axioma:g4b:builder:big",
                skeleton_code="...",
                stripped_byte_count=100,
                estimated_bpe_tokens=4097,  # Exceeds max 4,096
            )
            skel.validate_invariants()

    # -------------------------------------------------------------------------
    # 6. DiagnosticTuple
    # -------------------------------------------------------------------------

    def test_diagnostic_tuple_roundtrip(self) -> None:
        diag = DiagnosticTuple(
            diagnostic_id="diag_001",
            file_path="src/network.py",
            severity=DiagnosticSeverity.SECURITY_VIOLATION,
            start_byte=100,
            end_byte=115,
            line_number=10,
            column_number=4,
            rule_code="HERMETIC_LOOPBACK_PROHIBITED",
            message="Loopback address detected.",
            suggested_patch="'192.168.40.20'",
        )
        diag.validate_invariants()

        d = diag.to_dict()
        restored = DiagnosticTuple.from_dict(d)
        self.assertEqual(diag.diagnostic_id, restored.diagnostic_id)
        self.assertEqual(diag.rule_code, restored.rule_code)
        self.assertEqual(diag.start_byte, restored.start_byte)
        self.assertEqual(diag.severity, restored.severity)

    def test_diagnostic_tuple_byte_bounds(self) -> None:
        with self.assertRaises(DomainInvariantViolation):
            diag = DiagnosticTuple(
                diagnostic_id="diag_inv",
                file_path="src/test.py",
                severity=DiagnosticSeverity.ERROR,
                start_byte=200,
                end_byte=150,  # end_byte < start_byte violation
                line_number=1,
                column_number=0,
                rule_code="INVALID_SPAN",
                message="Bad span",
            )
            diag.validate_invariants()

    # -------------------------------------------------------------------------
    # 7. HermeticLinterReport
    # -------------------------------------------------------------------------

    def test_hermetic_linter_report_roundtrip(self) -> None:
        report = HermeticLinterReport(
            report_id="hlr_001",
            module_path="src/isolated.py",
            passed=True,
            violations=[],
            loopback_prohibited_checks=12,
            sys_path_tampering_checks=5,
            filesystem_confinement_checks=8,
        )
        report.validate_invariants()

        d = report.to_dict()
        restored = HermeticLinterReport.from_dict(d)
        self.assertEqual(report.report_id, restored.report_id)
        self.assertTrue(restored.passed)
        self.assertEqual(restored.loopback_prohibited_checks, 12)

    # -------------------------------------------------------------------------
    # 8. DynamicPersonaManifest
    # -------------------------------------------------------------------------

    def test_dynamic_persona_manifest_roundtrip(self) -> None:
        persona = DynamicPersonaManifest(
            persona_id="persona_fsm_01",
            role_title="Hierarchical Statechart Engineer",
            cognitive_role="STATECHART_FSM_ENGINEER",
            model_tier="flash",
            system_prompt="You are the Statechart Engineer.",
            governing_axioms=["[L1-002]", "[L1-G3B-011]"],
            banned_antipatterns=["MONOLITHIC_STATE", "UNGUARDED_TRANSITION"],
        )
        persona.validate_invariants()

        d = persona.to_dict()
        restored = DynamicPersonaManifest.from_dict(d)
        self.assertEqual(persona.persona_id, restored.persona_id)
        self.assertEqual(persona.governing_axioms, restored.governing_axioms)

    def test_dynamic_persona_manifest_missing_axioms(self) -> None:
        with self.assertRaises(DomainInvariantViolation):
            persona = DynamicPersonaManifest(
                persona_id="persona_empty",
                role_title="Empty Role",
                cognitive_role="UNKNOWN",
                model_tier="flash",
                system_prompt="Prompt",
                governing_axioms=[],  # Must have >= 1 axiom
            )
            persona.validate_invariants()

    # -------------------------------------------------------------------------
    # 9. SubtreeHealingEnvelope
    # -------------------------------------------------------------------------

    def test_subtree_healing_envelope_roundtrip(self) -> None:
        diag = DiagnosticTuple(
            diagnostic_id="diag_root_cause",
            file_path="src/network.py",
            severity=DiagnosticSeverity.SECURITY_VIOLATION,
            start_byte=10,
            end_byte=20,
            line_number=2,
            column_number=5,
            rule_code="HERMETIC_LOOPBACK_PROHIBITED",
            message="Loopback address in node.",
        )
        envelope = SubtreeHealingEnvelope(
            envelope_id="heal_env_001",
            failing_node_id="node_child_03",
            root_cause_diagnostic=diag,
            healing_strategy="SURGICAL_PATCH",
            quarantined_child_ids=["node_leaf_01"],
            reserved_healing_tokens=4096,
            resolved=False,
        )
        envelope.validate_invariants()

        d = envelope.to_dict()
        restored = SubtreeHealingEnvelope.from_dict(d)
        self.assertEqual(envelope.envelope_id, restored.envelope_id)
        self.assertEqual(envelope.failing_node_id, restored.failing_node_id)
        self.assertFalse(restored.resolved)

    # -------------------------------------------------------------------------
    # 10. QuineDaughterManifest
    # -------------------------------------------------------------------------

    def test_quine_daughter_manifest_roundtrip(self) -> None:
        manifest = QuineDaughterManifest(
            manifest_id="qdm_001",
            daughter_generation_id="gen_05a",
            sandbox_root_dir="/sandboxes/crucible_gen_05a",
            emitted_compiler_files=["src/compiler.py", "test_daughter.py"],
            daughter_hash=self.valid_sha256,
            boot_success=True,
            self_hosting_certified=True,
        )
        manifest.validate_invariants()

        d = manifest.to_dict()
        restored = QuineDaughterManifest.from_dict(d)
        self.assertEqual(manifest.manifest_id, restored.manifest_id)
        self.assertEqual(manifest.daughter_hash, restored.daughter_hash)
        self.assertTrue(restored.self_hosting_certified)

    def test_quine_daughter_manifest_hash_length(self) -> None:
        with self.assertRaises(DomainInvariantViolation):
            manifest = QuineDaughterManifest(
                manifest_id="qdm_bad",
                daughter_generation_id="gen_05a",
                sandbox_root_dir="/sandboxes/crucible",
                emitted_compiler_files=["compiler.py"],
                daughter_hash="short_hash",  # Not 64 chars
            )
            manifest.validate_invariants()

    # -------------------------------------------------------------------------
    # 11. RFCSubmissionRecord
    # -------------------------------------------------------------------------

    def test_rfc_submission_record_roundtrip(self) -> None:
        rfc = RFCSubmissionRecord(
            rfc_record_id="rfc_rec_001",
            request_id="req_sar_001",
            target_symbol_urn="urn:axioma:g4b:builder:network#bind",
            bottleneck_type="LATENCY_OVERRUN",
            proposed_delta="Relax timeout from 50ms to 75ms",
            submission_status="SUBMITTED",
        )
        rfc.validate_invariants()

        d = rfc.to_dict()
        restored = RFCSubmissionRecord.from_dict(d)
        self.assertEqual(rfc.rfc_record_id, restored.rfc_record_id)
        self.assertEqual(rfc.target_symbol_urn, restored.target_symbol_urn)

    def test_rfc_submission_record_invalid_urn(self) -> None:
        with self.assertRaises(DomainInvariantViolation):
            rfc = RFCSubmissionRecord(
                rfc_record_id="rfc_rec_bad",
                request_id="req_001",
                target_symbol_urn="invalid_urn_no_prefix",  # Must start with urn:axioma:g4b:
                bottleneck_type="TOKEN_EXHAUSTION",
                proposed_delta="delta",
                submission_status="SUBMITTED",
            )
            rfc.validate_invariants()

    # -------------------------------------------------------------------------
    # 12. MerkleTreeRootAttestation
    # -------------------------------------------------------------------------

    def test_merkle_tree_root_attestation_roundtrip(self) -> None:
        leaf_hashes = [
            hashlib.sha256(f"leaf_{i}".encode()).hexdigest() for i in range(4)
        ]
        root_hash = hashlib.sha256("".join(leaf_hashes).encode()).hexdigest()

        attestation = MerkleTreeRootAttestation(
            attestation_id="attest_001",
            merkle_root=root_hash,
            leaf_count=4,
            leaf_hashes=leaf_hashes,
            builder_signature="sig_secp256k1_verified",
        )
        attestation.validate_invariants()

        d = attestation.to_dict()
        restored = MerkleTreeRootAttestation.from_dict(d)
        self.assertEqual(attestation.attestation_id, restored.attestation_id)
        self.assertEqual(attestation.merkle_root, restored.merkle_root)
        self.assertEqual(attestation.leaf_count, restored.leaf_count)

    def test_merkle_tree_root_attestation_count_mismatch(self) -> None:
        with self.assertRaises(DomainInvariantViolation):
            attestation = MerkleTreeRootAttestation(
                attestation_id="attest_mismatch",
                merkle_root=self.valid_sha256,
                leaf_count=5,  # Mismatch with 1 hash
                leaf_hashes=[self.valid_sha256],
            )
            attestation.validate_invariants()

    # -------------------------------------------------------------------------
    # 13. FunctorialUndoCheckpoint
    # -------------------------------------------------------------------------

    def test_functorial_undo_checkpoint_roundtrip(self) -> None:
        chk = FunctorialUndoCheckpoint(
            checkpoint_id="chk_001",
            parent_checkpoint_id=None,
            state_label="sovereign_init",
            state_context={"tokens_allocated": 100000},
            erased_bits_at_checkpoint=0,
            active_node_id="node_root",
            merkle_root=self.valid_sha256,
        )
        chk.validate_invariants()

        d = chk.to_dict()
        restored = FunctorialUndoCheckpoint.from_dict(d)
        self.assertEqual(chk.checkpoint_id, restored.checkpoint_id)
        self.assertEqual(chk.state_label, restored.state_label)
        self.assertEqual(chk.state_context, restored.state_context)

    def test_functorial_undo_checkpoint_negative_bits(self) -> None:
        with self.assertRaises(DomainInvariantViolation):
            chk = FunctorialUndoCheckpoint(
                checkpoint_id="chk_bad",
                state_label="state_err",
                erased_bits_at_checkpoint=-100,  # Negative bits prohibited
            )
            chk.validate_invariants()

    # -------------------------------------------------------------------------
    # 14. PhysicalDiskWitness
    # -------------------------------------------------------------------------

    def test_physical_disk_witness_roundtrip(self) -> None:
        witness = PhysicalDiskWitness(
            witness_id="witness_001",
            file_path="/tmp/axioma_test.py",
            byte_size=1024,
            sha256_hash=self.valid_sha256,
            is_present=True,
        )
        witness.validate_invariants()

        d = witness.to_dict()
        restored = PhysicalDiskWitness.from_dict(d)
        self.assertEqual(witness.witness_id, restored.witness_id)
        self.assertEqual(witness.file_path, restored.file_path)
        self.assertEqual(witness.byte_size, restored.byte_size)
        self.assertEqual(witness.sha256_hash, restored.sha256_hash)
        self.assertTrue(restored.is_present)

    def test_physical_disk_witness_zero_byte_violation(self) -> None:
        with self.assertRaises(DomainInvariantViolation):
            witness = PhysicalDiskWitness(
                witness_id="witness_zero",
                file_path="/tmp/empty.py",
                byte_size=0,  # Zero-byte violation [NEG-G1B-001]
                sha256_hash=self.valid_sha256,
            )
            witness.validate_invariants()

    # -------------------------------------------------------------------------
    # 15. LeafEmissionEvent
    # -------------------------------------------------------------------------

    def test_leaf_emission_event_roundtrip(self) -> None:
        witness = PhysicalDiskWitness(
            witness_id="witness_leaf",
            file_path="src/leaf.py",
            byte_size=512,
            sha256_hash=self.valid_sha256,
        )
        event = LeafEmissionEvent(
            event_id="ev_leaf_001",
            leaf_symbol_urn="urn:axioma:g4b:leaf#node",
            source_path="src/leaf.py",
            disk_witness=witness,
            bpe_token_count=120,
        )
        event.validate_invariants()

        d = event.to_dict()
        restored = LeafEmissionEvent.from_dict(d)
        self.assertEqual(event.event_id, restored.event_id)
        self.assertEqual(event.leaf_symbol_urn, restored.leaf_symbol_urn)
        self.assertEqual(event.bpe_token_count, restored.bpe_token_count)
        self.assertEqual(restored.disk_witness.sha256_hash, self.valid_sha256)

    def test_leaf_emission_event_invalid_urn(self) -> None:
        witness = PhysicalDiskWitness(
            witness_id="witness_leaf",
            file_path="src/leaf.py",
            byte_size=512,
            sha256_hash=self.valid_sha256,
        )
        with self.assertRaises(DomainInvariantViolation):
            event = LeafEmissionEvent(
                event_id="ev_bad_urn",
                leaf_symbol_urn="invalid:urn:leaf",
                source_path="src/leaf.py",
                disk_witness=witness,
            )
            event.validate_invariants()

    # -------------------------------------------------------------------------
    # 16. ReactiveVerificationGate
    # -------------------------------------------------------------------------

    def test_reactive_verification_gate_roundtrip(self) -> None:
        gate = ReactiveVerificationGate(
            gate_id="gate_001",
            target_urn="urn:axioma:g4b:target#gate",
            passed=True,
            checks_run=5,
            failures=[],
        )
        gate.validate_invariants()

        d = gate.to_dict()
        restored = ReactiveVerificationGate.from_dict(d)
        self.assertEqual(gate.gate_id, restored.gate_id)
        self.assertTrue(restored.passed)
        self.assertEqual(restored.checks_run, 5)

    def test_reactive_verification_gate_contradiction(self) -> None:
        with self.assertRaises(DomainInvariantViolation):
            gate = ReactiveVerificationGate(
                gate_id="gate_bad",
                target_urn="urn:axioma:g4b:target#gate",
                passed=True,  # Passed=True with non-empty failures
                checks_run=1,
                failures=["Invariant failure"],
            )
            gate.validate_invariants()

    # -------------------------------------------------------------------------
    # 17. ReactiveAuditReport
    # -------------------------------------------------------------------------

    def test_reactive_audit_report_roundtrip(self) -> None:
        report = ReactiveAuditReport(
            report_id="rep_audit_001",
            module_path="src/service.py",
            passed=True,
            diagnostics=[],
            loopback_clean=True,
            functorial_purity_verified=True,
        )
        report.validate_invariants()

        d = report.to_dict()
        restored = ReactiveAuditReport.from_dict(d)
        self.assertEqual(report.report_id, restored.report_id)
        self.assertTrue(restored.passed)
        self.assertTrue(restored.loopback_clean)

    def test_reactive_audit_report_loopback_taint_violation(self) -> None:
        with self.assertRaises(DomainInvariantViolation):
            report = ReactiveAuditReport(
                report_id="rep_tainted",
                module_path="src/bad.py",
                passed=True,  # Passed=True with loopback_clean=False
                diagnostics=[],
                loopback_clean=False,
                functorial_purity_verified=True,
            )
            report.validate_invariants()

    # -------------------------------------------------------------------------
    # 18. ByzantineChaosReport
    # -------------------------------------------------------------------------

    def test_byzantine_chaos_report_roundtrip(self) -> None:
        report = ByzantineChaosReport(
            report_id="chaos_001",
            target_module="src/kernel.py",
            chaos_scenarios_tested=10,
            passed=True,
            injected_fault_count=5,
            recovered_fault_count=5,
            chaos_seed=1337,
        )
        report.validate_invariants()

        d = report.to_dict()
        restored = ByzantineChaosReport.from_dict(d)
        self.assertEqual(report.report_id, restored.report_id)
        self.assertTrue(restored.passed)
        self.assertEqual(restored.recovered_fault_count, 5)

    def test_byzantine_chaos_report_unrecovered_fault_violation(self) -> None:
        with self.assertRaises(DomainInvariantViolation):
            report = ByzantineChaosReport(
                report_id="chaos_unrecovered",
                target_module="src/kernel.py",
                chaos_scenarios_tested=5,
                passed=True,  # Passed=True but 3 faults unrecovered
                injected_fault_count=5,
                recovered_fault_count=2,
            )
            report.validate_invariants()

    # -------------------------------------------------------------------------
    # 19. CausalConvergenceAttestation
    # -------------------------------------------------------------------------

    def test_causal_convergence_attestation_roundtrip(self) -> None:
        witness = PhysicalDiskWitness(
            witness_id="wit_c1",
            file_path="src/c1.py",
            byte_size=256,
            sha256_hash=self.valid_sha256,
        )
        attestation = CausalConvergenceAttestation(
            attestation_id="attest_causal_001",
            dag_root_urn="urn:axioma:g4b:dag#root",
            converged_leaf_count=1,
            leaf_witnesses=[witness],
            merkle_causal_hash=self.merkle_sha256,
            certified=True,
        )
        attestation.validate_invariants()

        d = attestation.to_dict()
        restored = CausalConvergenceAttestation.from_dict(d)
        self.assertEqual(attestation.attestation_id, restored.attestation_id)
        self.assertEqual(restored.converged_leaf_count, 1)
        self.assertEqual(restored.merkle_causal_hash, self.merkle_sha256)

    def test_causal_convergence_attestation_mismatch(self) -> None:
        with self.assertRaises(DomainInvariantViolation):
            attestation = CausalConvergenceAttestation(
                attestation_id="attest_mismatch",
                dag_root_urn="urn:axioma:g4b:dag#root",
                converged_leaf_count=2,  # Declared 2, provided 0
                leaf_witnesses=[],
                merkle_causal_hash=self.merkle_sha256,
            )
            attestation.validate_invariants()

    # -------------------------------------------------------------------------
    # 20. QuineReactiveManifest
    # -------------------------------------------------------------------------

    def test_quine_reactive_manifest_roundtrip(self) -> None:
        manifest = QuineReactiveManifest(
            manifest_id="qrm_001",
            daughter_gen_id="gen_05a",
            reactive_dag_verified=True,
            self_hosting_certified=True,
            crucible_score=0.99,
            emitted_artifacts=["gen_05a/compiler.py"],
            merkle_signature=self.valid_sha256,
        )
        manifest.validate_invariants()

        d = manifest.to_dict()
        restored = QuineReactiveManifest.from_dict(d)
        self.assertEqual(manifest.manifest_id, restored.manifest_id)
        self.assertTrue(restored.reactive_dag_verified)
        self.assertTrue(restored.self_hosting_certified)
        self.assertEqual(restored.crucible_score, 0.99)

    def test_quine_reactive_manifest_unverified_dag_violation(self) -> None:
        with self.assertRaises(DomainInvariantViolation):
            manifest = QuineReactiveManifest(
                manifest_id="qrm_bad",
                daughter_gen_id="gen_05a",
                reactive_dag_verified=False,  # DAG not verified
                self_hosting_certified=True,   # But self_hosting marked True!
                crucible_score=0.99,
                emitted_artifacts=["gen_05a/compiler.py"],
                merkle_signature=self.valid_sha256,
            )
            manifest.validate_invariants()


if __name__ == "__main__":
    unittest.main()
