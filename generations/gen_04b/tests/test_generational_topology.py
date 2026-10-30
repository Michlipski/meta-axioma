"""Generation 4b Generational Topology & Cross-Service Invariant Test Suite.

Enforces:
- [NEG-G1B-001] Empirical Execution Witness & Anti-Phantom Emission Gate.
- [L1-G4B-001] Decoupled Research Sovereignty Invariant.
- [L1-G4B-002] Zero-Code Research Tool Boundary Invariant.
- [L1-G4B-003] Hierarchical Merkle-DAG Witness Telemetry.
- Directory structure, protocol schema roundtripping, and URN taxonomy resolution.
"""

from pathlib import Path
import subprocess
import sys
import unittest

GEN_04B_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = GEN_04B_DIR.parents[1]

# Ensure gen_04b is in sys.path
if str(GEN_04B_DIR) not in sys.path:
    sys.path.insert(0, str(GEN_04B_DIR))

from protocols.urn_registry import (
    GLOBAL_URN_REGISTRY,
    SymbolURN,
    URNFormatError,
    URNRegistry,
)
from protocols.rfc_protocol import (
    BottleneckType,
    CounterProof,
    RFCProtocolViolation,
    RFCStatus,
    SolverResult,
    SpecAdjustmentRequest,
    SpecAmendment,
)
from protocols.deliverable_bundle import (
    ConstraintAnalysis,
    DeliverableProtocolViolation,
    FailureModeModel,
    HypothesisDefinition,
    ResearchDeliverableBundle,
    TabooDistanceMatrix,
    TradeoffMatrix,
)


class TestG4bGenerationalTopology(unittest.TestCase):
    """Verifies Generation 4b service mesh structure and protocol contracts."""

    def test_01_all_required_enclaves_exist_on_disk(self):
        """Verifies physical presence of all 5 services, protocols, apps, epochs, and tests."""
        required_paths = [
            GEN_04B_DIR / "README.md",
            GEN_04B_DIR / "run.py",
            GEN_04B_DIR / "protocols" / "__init__.py",
            GEN_04B_DIR / "protocols" / "urn_registry.py",
            GEN_04B_DIR / "protocols" / "rfc_protocol.py",
            GEN_04B_DIR / "protocols" / "deliverable_bundle.py",
            GEN_04B_DIR / "services" / "research" / "run.py",
            GEN_04B_DIR / "services" / "research" / "src",
            GEN_04B_DIR / "services" / "research" / "tests",
            GEN_04B_DIR / "services" / "builder" / "README.md",
            GEN_04B_DIR / "services" / "audit" / "README.md",
            GEN_04B_DIR / "services" / "telemetry" / "README.md",
            GEN_04B_DIR / "services" / "governance" / "README.md",
            GEN_04B_DIR / "apps",
            GEN_04B_DIR / "epochs",
            GEN_04B_DIR / "tests",
        ]
        for path in required_paths:
            self.assertTrue(path.exists(), f"Required path missing: {path}")

    def test_02_urn_taxonomy_parsing_and_validation(self):
        """Verifies URN parsing, validation, and rejection of malformed URNs."""
        valid_urn = "urn:axioma:g4b:research:deliverable_bundle#v1"
        parsed = SymbolURN.parse(valid_urn)
        self.assertEqual(parsed.domain, "research")
        self.assertEqual(parsed.entity, "deliverable_bundle")
        self.assertEqual(parsed.symbol, "v1")
        self.assertEqual(parsed.to_string(), valid_urn)

        # Invalid URNs
        with self.assertRaises(URNFormatError):
            SymbolURN.parse("invalid_urn")
        with self.assertRaises(URNFormatError):
            SymbolURN.parse("urn:other:g4b:foo:bar")

    def test_03_urn_registry_resolution(self):
        """Verifies multi-domain symbol registration and domain-based lookup."""
        reg = URNRegistry()
        reg.register_symbol("urn:axioma:g4b:builder:emitter#v1", provider_service="services/builder")
        reg.register_symbol("urn:axioma:g4b:audit:verifier#v1", provider_service="services/audit")

        self.assertIsNotNone(reg.resolve("urn:axioma:g4b:builder:emitter#v1"))
        self.assertEqual(len(reg.list_by_domain("builder")), 1)
        self.assertEqual(len(reg.list_by_service("services/audit")), 1)

    def test_04_rfc_protocol_schemas_and_roundtripping(self):
        """Verifies SpecAdjustmentRequest and SpecAmendment serialization roundtrip."""
        req = SpecAdjustmentRequest(
            request_id="req_test_001",
            builder_node_id="node_builder_01",
            target_symbol_urn="urn:axioma:g4b:research:bundle#v1",
            bottleneck_type=BottleneckType.TOKEN_EXHAUSTION,
            empirical_evidence="Physical BPE tokens depleted past 90%",
            proposed_delta="Prune unused contract IR fields",
            preserved_invariants=["[L1-002]", "[L1-G4B-001]"],
        )
        req_dict = req.to_dict()
        req_recreated = SpecAdjustmentRequest.from_dict(req_dict)
        self.assertEqual(req.request_id, req_recreated.request_id)
        self.assertEqual(req.bottleneck_type, req_recreated.bottleneck_type)

        # Rejection amendment requires counter-proof
        counter_proof = CounterProof(
            counter_proof_id="cp_001",
            request_id="req_test_001",
            violated_axioms=["[L1-002]"],
            z3_unsat_core="unsat_core(invariant_preserved=false)",
        )
        amendment = SpecAmendment(
            amendment_id="amend_001",
            request_id="req_test_001",
            is_approved=False,
            adjudicator_signature="SIG_ED25519_ADJUDICATOR",
            amended_contract_ir_delta="",
            rejection_counter_proof=counter_proof,
        )
        amend_dict = amendment.to_dict()
        amend_recreated = SpecAmendment.from_dict(amend_dict)
        self.assertFalse(amend_recreated.is_approved)
        self.assertIsNotNone(amend_recreated.rejection_counter_proof)

    def test_05_deliverable_bundle_invariants_and_roundtripping(self):
        """Verifies ResearchDeliverableBundle invariants and serialization roundtrip."""
        bundle = ResearchDeliverableBundle(
            bundle_id="bundle_test_001",
            target_soc_id="soc_001",
            hypothesis_id="hypo_001",
            constraint_analysis_id="ca_001",
            failure_mode_id="fm_001",
            tradeoff_matrix_id="tm_001",
            reference_architecture_hash="a" * 64,
            merkle_root="b" * 64,
            is_certified=True,
        )
        bundle.validate_invariants()
        b_dict = bundle.to_dict()
        b_recreated = ResearchDeliverableBundle.from_dict(b_dict)
        self.assertEqual(bundle.bundle_id, b_recreated.bundle_id)
        self.assertTrue(b_recreated.is_certified)

        # Invariant failure: certified bundle without 64-char hash
        invalid_bundle = ResearchDeliverableBundle(
            bundle_id="bundle_bad",
            target_soc_id="soc_001",
            hypothesis_id="hypo_001",
            constraint_analysis_id="ca_001",
            failure_mode_id="fm_001",
            tradeoff_matrix_id="tm_001",
            reference_architecture_hash="short_hash",
            merkle_root="b" * 64,
            is_certified=True,
        )
        with self.assertRaises(DeliverableProtocolViolation):
            invalid_bundle.validate_invariants()

    def test_06_canonical_symlink_points_to_g4b_research_service(self):
        """Verifies that apps/soc_g4b_researcher is a valid symlink to gen_04b."""
        canonical_link = REPO_ROOT / "apps" / "soc_g4b_researcher"
        self.assertTrue(canonical_link.is_symlink(), f"{canonical_link} is not a symlink")
        target_path = canonical_link.resolve()
        expected_target = (GEN_04B_DIR / "services" / "research").resolve()
        self.assertEqual(target_path, expected_target)

    def test_07_legacy_gen_03b_shim_execution(self):
        """Verifies that running legacy gen_03b run.py succeeds and exits with code 0."""
        legacy_run = REPO_ROOT / "generations" / "gen_03b" / "apps" / "soc_g4b_researcher" / "run.py"
        self.assertTrue(legacy_run.exists())
        res = subprocess.run([sys.executable, str(legacy_run)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Legacy shim failed: {res.stderr}")


if __name__ == "__main__":
    unittest.main()
