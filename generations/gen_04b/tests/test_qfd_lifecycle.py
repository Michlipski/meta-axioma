"""Comprehensive Test Suite for QFD House of Quality Lifecycle, MCDA Ranking, and Consistency Audit.

Enforces:
- [SPEC-G4B-RESEARCH-QFD-001]: Rigorous derivation of engineering characteristics from customer JTBDs.
- [SPEC-G4B-RESEARCH-MCDA-001]: Vector TOPSIS multi-criteria decision analysis and Pareto filtering.
- [L1-G4B-009], [INV-G4B-REDTEAM-001]: Pre-proposal adversarial verification and invariant enforcement.
- [INV-G4B-CAUSAL-001]: Strict temporal causality between sealed research artifacts and project proposals.
- [NEG-G1B-001] Mandatory Physical File Emission & Non-Zero Byte Verification.
- [NEG-G1B-002] Anti-Mock Subprocess Entrypoint Smoke Invariant.
- Mitigation for VULN-QFD-003: Substrate invariant immunity to pruning.
- Mitigation for VULN-QFD-004: Elimination of Pareto-dominated options preventing TOPSIS rank reversal.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from generations.gen_04b.services.research.src.domain_models import DomainInvariantViolation
from generations.gen_04b.services.research.src.qfd_engine import (
    CharacteristicType,
    CorrelationRoofEdge,
    CorrelationType,
    CustomerRequirement,
    EngineeringCharacteristic,
    HouseOfQualityIR,
    OptimizationDirection,
    QFDEngine,
    RelationshipStrength,
)
from generations.gen_04b.services.research.src.mcda_ranker import (
    CandidateOptionVector,
    MCDARanker,
    MCDARankResult,
)
from generations.gen_04b.services.audit.src.qfd_consistency_auditor import (
    OrphanFeatureViolation,
    QFDConsistencyAuditor,
    QFDConsistencyAuditResult,
    RecommendationParityViolation,
    RoofCoverageViolation,
    TemporalCausalityViolation,
)


class TestQFDEngineLifecycle(unittest.TestCase):
    """Unit tests verifying House of Quality mathematical derivation, gating, and Merkle sealing."""

    def setUp(self) -> None:
        self.engine = QFDEngine(relevance_threshold=0.35)

        self.req1 = CustomerRequirement(
            req_id="CR-01",
            description="Ultra-low latency message delivery",
            weight=0.8,
            frictions_addressed=["High network latency"],
        )
        self.req2 = CustomerRequirement(
            req_id="CR-02",
            description="High throughput message indexing",
            weight=0.6,
            frictions_addressed=["Slow query turnaround"],
        )
        self.requirements = [self.req1, self.req2]

        self.ec1 = EngineeringCharacteristic(
            char_id="EC-01",
            name="Throughput",
            char_type=CharacteristicType.USER_FACING_JTBD,
            direction=OptimizationDirection.MAXIMIZE,
            unit="ops/sec",
            target_value=10000.0,
        )
        self.ec2 = EngineeringCharacteristic(
            char_id="EC-02",
            name="Latency",
            char_type=CharacteristicType.USER_FACING_JTBD,
            direction=OptimizationDirection.MINIMIZE,
            unit="ms",
            target_value=5.0,
        )
        self.ec3 = EngineeringCharacteristic(
            char_id="EC-03",
            name="CosmeticAnimationFPS",
            char_type=CharacteristicType.USER_FACING_JTBD,
            direction=OptimizationDirection.MAXIMIZE,
            unit="fps",
            target_value=60.0,
        )
        self.ec4 = EngineeringCharacteristic(
            char_id="EC-04",
            name="HermeticIsolation",
            char_type=CharacteristicType.SUBSTRATE_INVARIANT,
            direction=OptimizationDirection.MAXIMIZE,
            unit="score",
            target_value=1.0,
        )
        self.characteristics = [self.ec1, self.ec2, self.ec3, self.ec4]

        # Relationship tensor:
        # CR-01: EC-01: WEAK (1), EC-02: STRONG (9), EC-03: NONE (0), EC-04: WEAK (1)
        # CR-02: EC-01: STRONG (9), EC-02: MEDIUM (3), EC-03: WEAK (1), EC-04: NONE (0)
        self.relationship_tensor = {
            "CR-01": {
                "EC-01": RelationshipStrength.WEAK,
                "EC-02": RelationshipStrength.STRONG,
                "EC-03": RelationshipStrength.NONE,
                "EC-04": RelationshipStrength.WEAK,
            },
            "CR-02": {
                "EC-01": RelationshipStrength.STRONG,
                "EC-02": RelationshipStrength.MEDIUM,
                "EC-03": RelationshipStrength.WEAK,
                "EC-04": RelationshipStrength.NONE,
            },
        }

        # Roof edges
        self.roof_edge_neg1 = CorrelationRoofEdge(
            char_id_a="EC-01",
            char_id_b="EC-02",
            correlation=CorrelationType.NEGATIVE,
            rationale="Higher throughput increases batching which worsens latency",
        )
        self.roof_edge_neg2 = CorrelationRoofEdge(
            char_id_a="EC-01",
            char_id_b="EC-03",
            correlation=CorrelationType.STRONG_NEGATIVE,
            rationale="Animation rendering competes for CPU cycles with throughput indexing",
        )
        self.roof_edge_pos = CorrelationRoofEdge(
            char_id_a="EC-02",
            char_id_b="EC-04",
            correlation=CorrelationType.POSITIVE,
            rationale="Hermetic isolation prevents noisy neighbors, stabilizing latency",
        )
        self.roof_edges = [self.roof_edge_neg1, self.roof_edge_neg2, self.roof_edge_pos]

    def test_01_create_house_of_quality_structure(self) -> None:
        """Verifies proper creation and structural invariant validation of HouseOfQualityIR."""
        hoq = self.engine.create_house_of_quality(
            matrix_id="HOQ-TEST-001",
            target_soc_id="SOC-TEST-MESH-001",
            requirements=self.requirements,
            characteristics=self.characteristics,
            relationship_tensor=self.relationship_tensor,
            roof_edges=self.roof_edges,
        )

        self.assertEqual(hoq.matrix_id, "HOQ-TEST-001")
        self.assertEqual(hoq.target_soc_id, "SOC-TEST-MESH-001")
        self.assertEqual(len(hoq.requirements), 2)
        self.assertEqual(len(hoq.characteristics), 4)
        self.assertEqual(len(hoq.roof_edges), 3)
        self.assertFalse(hoq.is_sealed)
        self.assertEqual(hoq.merkle_root, "")

        # Test dictionary serialization roundtrip
        hoq_dict = hoq.to_dict()
        restored = HouseOfQualityIR.from_dict(hoq_dict)
        self.assertEqual(restored.matrix_id, hoq.matrix_id)
        self.assertEqual(restored.target_soc_id, hoq.target_soc_id)
        self.assertEqual(len(restored.characteristics), 4)

    def test_02_technical_and_normalized_importance_math(self) -> None:
        """Verifies exact calculation of T_j = sum(W_i * R_ij) and normalized importance \bar{T}_j."""
        hoq = self.engine.create_house_of_quality(
            matrix_id="HOQ-TEST-002",
            target_soc_id="SOC-TEST-MESH-001",
            requirements=self.requirements,
            characteristics=self.characteristics,
            relationship_tensor=self.relationship_tensor,
        )

        # Expected:
        # EC-01: 0.8 * 1 + 0.6 * 9 = 0.8 + 5.4 = 6.2
        # EC-02: 0.8 * 9 + 0.6 * 3 = 7.2 + 1.8 = 9.0
        # EC-03: 0.8 * 0 + 0.6 * 1 = 0.0 + 0.6 = 0.6
        # EC-04: 0.8 * 1 + 0.6 * 0 = 0.8 + 0.0 = 0.8
        self.assertAlmostEqual(hoq.technical_importance["EC-01"], 6.2, places=3)
        self.assertAlmostEqual(hoq.technical_importance["EC-02"], 9.0, places=3)
        self.assertAlmostEqual(hoq.technical_importance["EC-03"], 0.6, places=3)
        self.assertAlmostEqual(hoq.technical_importance["EC-04"], 0.8, places=3)

        # Max T_k is 9.0 (EC-02)
        # Normalized:
        # EC-01: 6.2 / 9.0 = 0.6889
        # EC-02: 9.0 / 9.0 = 1.0000
        # EC-03: 0.6 / 9.0 = 0.0667
        # EC-04: 0.8 / 9.0 = 0.0889
        self.assertAlmostEqual(hoq.normalized_importance["EC-01"], 0.6889, places=3)
        self.assertAlmostEqual(hoq.normalized_importance["EC-02"], 1.0000, places=3)
        self.assertAlmostEqual(hoq.normalized_importance["EC-03"], 0.0667, places=3)
        self.assertAlmostEqual(hoq.normalized_importance["EC-04"], 0.0889, places=3)

    def test_03_relevance_threshold_gating_and_substrate_invariant_immunity(self) -> None:
        """Verifies feature relevance gating (>= 0.35) and VULN-QFD-003 substrate invariant immunity."""
        hoq = self.engine.create_house_of_quality(
            matrix_id="HOQ-TEST-003",
            target_soc_id="SOC-TEST-MESH-001",
            requirements=self.requirements,
            characteristics=self.characteristics,
            relationship_tensor=self.relationship_tensor,
        )

        # EC-01 (0.6889 >= 0.35) -> included
        # EC-02 (1.0000 >= 0.35) -> included
        # EC-03 (0.0667 < 0.35, USER_FACING_JTBD) -> cut
        # EC-04 (0.0889 < 0.35, SUBSTRATE_INVARIANT) -> MUST BE INCLUDED (VULN-QFD-003)
        self.assertIn("EC-01", hoq.included_characteristics)
        self.assertIn("EC-02", hoq.included_characteristics)
        self.assertIn("EC-04", hoq.included_characteristics, "Substrate invariant must be immune to pruning")
        self.assertIn("EC-03", hoq.cut_characteristics)
        self.assertNotIn("EC-04", hoq.cut_characteristics)

    def test_04_extract_negative_roof_contradictions(self) -> None:
        """Verifies extraction of NEGATIVE and STRONG_NEGATIVE correlation roof edges."""
        hoq = self.engine.create_house_of_quality(
            matrix_id="HOQ-TEST-004",
            target_soc_id="SOC-TEST-MESH-001",
            requirements=self.requirements,
            characteristics=self.characteristics,
            relationship_tensor=self.relationship_tensor,
            roof_edges=self.roof_edges,
        )

        negative_edges = self.engine.extract_negative_roof_contradictions(hoq)
        self.assertEqual(len(negative_edges), 2)
        edge_correlations = {e.correlation for e in negative_edges}
        self.assertEqual(edge_correlations, {CorrelationType.NEGATIVE, CorrelationType.STRONG_NEGATIVE})
        self.assertNotIn(CorrelationType.POSITIVE, edge_correlations)

    def test_05_merkle_sealing_integrity(self) -> None:
        """Verifies cryptographic Merkle-DAG sealing with 64-char SHA-256 digest."""
        hoq = self.engine.create_house_of_quality(
            matrix_id="HOQ-TEST-005",
            target_soc_id="SOC-TEST-MESH-001",
            requirements=self.requirements,
            characteristics=self.characteristics,
            relationship_tensor=self.relationship_tensor,
            roof_edges=self.roof_edges,
        )

        self.assertFalse(hoq.is_sealed)
        digest = self.engine.seal_qfd_matrix(hoq)

        self.assertTrue(hoq.is_sealed)
        self.assertEqual(len(digest), 64)
        self.assertEqual(hoq.merkle_root, digest)
        self.assertGreater(hoq.timestamp_unix_ms, 0)

        # Invariant validation must succeed on sealed matrix
        hoq.validate_invariants()

        # Sealed matrix with empty root must raise DomainInvariantViolation
        hoq.merkle_root = ""
        with self.assertRaises(DomainInvariantViolation):
            hoq.validate_invariants()


class TestMCDARanker(unittest.TestCase):
    """Unit tests for Pareto dominance pre-filtering, TOPSIS scoring, recommendation, and tie detection."""

    def setUp(self) -> None:
        self.ranker = MCDARanker()
        self.engine = QFDEngine(relevance_threshold=0.35)

        self.reqs = [
            CustomerRequirement("CR-1", "Throughput need", 0.9),
            CustomerRequirement("CR-2", "Low Latency need", 0.8),
        ]
        self.chars = [
            EngineeringCharacteristic(
                "EC-01", "Throughput", CharacteristicType.USER_FACING_JTBD,
                OptimizationDirection.MAXIMIZE, "ops/s", 1000.0,
            ),
            EngineeringCharacteristic(
                "EC-02", "Latency", CharacteristicType.USER_FACING_JTBD,
                OptimizationDirection.MINIMIZE, "ms", 10.0,
            ),
        ]
        self.tensor = {
            "CR-1": {"EC-01": RelationshipStrength.STRONG, "EC-02": RelationshipStrength.NONE},
            "CR-2": {"EC-01": RelationshipStrength.NONE, "EC-02": RelationshipStrength.STRONG},
        }
        self.hoq = self.engine.create_house_of_quality(
            matrix_id="HOQ-MCDA-001",
            target_soc_id="SOC-001",
            requirements=self.reqs,
            characteristics=self.chars,
            relationship_tensor=self.tensor,
        )
        self.engine.seal_qfd_matrix(self.hoq)

    def test_01_pareto_dominance_prefiltering_eliminates_dominated_vectors(self) -> None:
        """Verifies Pareto dominance pre-filtering eliminates dominated vectors (mitigating VULN-QFD-004)."""
        # Option A: Great throughput, moderate latency, zero roof penalty
        cand_a = CandidateOptionVector(
            option_id="opt_a",
            option_name="Option Alpha",
            performance_vector={"EC-01": 900.0, "EC-02": 50.0},
            roof_penalty=0.0,
        )
        # Option B: Strictly worse than A on all criteria and worse penalty (Dominated by A)
        cand_b = CandidateOptionVector(
            option_id="opt_b",
            option_name="Option Beta (Dominated)",
            performance_vector={"EC-01": 700.0, "EC-02": 40.0},
            roof_penalty=0.1,
        )
        # Option C: Trade-off vector (Higher throughput than A, slightly worse latency)
        cand_c = CandidateOptionVector(
            option_id="opt_c",
            option_name="Option Gamma (Pareto-Optimal)",
            performance_vector={"EC-01": 950.0, "EC-02": 45.0},
            roof_penalty=0.0,
        )

        filtered = self.ranker.filter_pareto_frontier([cand_a, cand_b, cand_c])
        surviving_ids = [c.option_id for c in filtered]

        self.assertIn("opt_a", surviving_ids)
        self.assertIn("opt_c", surviving_ids)
        self.assertNotIn("opt_b", surviving_ids, "Dominated vector must be pruned by Pareto pre-filtering")
        self.assertEqual(len(filtered), 2)

    def test_02_topsis_scoring_and_recommendation_strictly_rank_1(self) -> None:
        """Verifies TOPSIS ranking assigns is_recommended = True strictly to Rank 1."""
        cand_1 = CandidateOptionVector(
            option_id="opt_high_perf",
            option_name="High Performance Cluster",
            performance_vector={"EC-01": 950.0, "EC-02": 8.0},  # High throughput, low latency
            roof_penalty=0.0,
        )
        cand_2 = CandidateOptionVector(
            option_id="opt_low_perf",
            option_name="Basic Standalone",
            performance_vector={"EC-01": 200.0, "EC-02": 50.0},  # Low throughput, high latency
            roof_penalty=0.05,
        )

        results = self.ranker.score_topsis(self.hoq, [cand_1, cand_2])
        self.assertEqual(len(results), 2)

        rank_1 = results[0]
        rank_2 = results[1]

        self.assertEqual(rank_1.rank, 1)
        self.assertEqual(rank_1.option_id, "opt_high_perf")
        self.assertTrue(rank_1.is_recommended)
        self.assertFalse(rank_1.tie_detected)

        self.assertEqual(rank_2.rank, 2)
        self.assertEqual(rank_2.option_id, "opt_low_perf")
        self.assertFalse(rank_2.is_recommended)
        self.assertLess(rank_2.composite_score, rank_1.composite_score)

    def test_03_tie_detection_clears_recommendation(self) -> None:
        """Verifies tie detection when |C_0 - C_1| <= 0.05 clears is_recommended on both options."""
        # Two identical candidate vectors (score difference = 0.0 <= 0.05)
        cand_x = CandidateOptionVector(
            option_id="opt_x",
            option_name="Option X",
            performance_vector={"EC-01": 800.0, "EC-02": 15.0},
            roof_penalty=0.0,
        )
        cand_y = CandidateOptionVector(
            option_id="opt_y",
            option_name="Option Y",
            performance_vector={"EC-01": 800.0, "EC-02": 15.0},
            roof_penalty=0.0,
        )

        results = self.ranker.score_topsis(self.hoq, [cand_x, cand_y], tie_threshold=0.05)
        self.assertEqual(len(results), 2)

        self.assertTrue(results[0].tie_detected, "Tie must be detected on rank 1")
        self.assertTrue(results[1].tie_detected, "Tie must be detected on rank 2")
        self.assertFalse(results[0].is_recommended, "is_recommended must be cleared when tie detected")
        self.assertFalse(results[1].is_recommended)
        self.assertAlmostEqual(abs(results[0].composite_score - results[1].composite_score), 0.0)

        # Three candidates with Rank 1 and Rank 2 within tie threshold, Rank 3 distinct
        cand_z = CandidateOptionVector(
            option_id="opt_z",
            option_name="Option Z",
            performance_vector={"EC-01": 200.0, "EC-02": 60.0},
            roof_penalty=0.0,
        )
        cand_near = CandidateOptionVector(
            option_id="opt_near",
            option_name="Option Near",
            performance_vector={"EC-01": 790.0, "EC-02": 15.2},
            roof_penalty=0.0,
        )
        results3 = self.ranker.score_topsis(self.hoq, [cand_x, cand_near, cand_z], tie_threshold=0.05)
        self.assertEqual(len(results3), 3)
        self.assertTrue(results3[0].tie_detected)
        self.assertTrue(results3[1].tie_detected)
        self.assertFalse(results3[0].is_recommended)
        self.assertFalse(results3[1].is_recommended)
        self.assertFalse(results3[2].tie_detected)


class TestQFDConsistencyAuditor(unittest.TestCase):
    """Unit tests verifying 4-barrier QFD consistency auditor and adversarial falsification vectors."""

    def setUp(self) -> None:
        self.auditor = QFDConsistencyAuditor()
        self.engine = QFDEngine(relevance_threshold=0.35)

        self.req1 = CustomerRequirement("CR-01", "Speed", 0.9)
        self.req2 = CustomerRequirement("CR-02", "Reliability", 0.8)

        self.ec1 = EngineeringCharacteristic(
            "EC-01", "Throughput", CharacteristicType.USER_FACING_JTBD,
            OptimizationDirection.MAXIMIZE, "req/s", 5000.0,
        )
        self.ec2 = EngineeringCharacteristic(
            "EC-02", "Latency", CharacteristicType.USER_FACING_JTBD,
            OptimizationDirection.MINIMIZE, "ms", 10.0,
        )
        self.ec3 = EngineeringCharacteristic(
            "EC-03", "TelemetryMemoryCap", CharacteristicType.SUBSTRATE_INVARIANT,
            OptimizationDirection.MINIMIZE, "MB", 64.0,
        )

        self.tensor = {
            "CR-01": {"EC-01": RelationshipStrength.STRONG, "EC-02": RelationshipStrength.MEDIUM, "EC-03": RelationshipStrength.WEAK},
            "CR-02": {"EC-01": RelationshipStrength.WEAK, "EC-02": RelationshipStrength.STRONG, "EC-03": RelationshipStrength.STRONG},
        }

        self.negative_roof = CorrelationRoofEdge(
            char_id_a="EC-01",
            char_id_b="EC-02",
            correlation=CorrelationType.STRONG_NEGATIVE,
            rationale="Extreme throughput saturation spikes queueing latency",
        )

        self.hoq = self.engine.create_house_of_quality(
            matrix_id="HOQ-AUDIT-001",
            target_soc_id="SOC-AUDIT-001",
            requirements=[self.req1, self.req2],
            characteristics=[self.ec1, self.ec2, self.ec3],
            relationship_tensor=self.tensor,
            roof_edges=[self.negative_roof],
        )
        self.engine.seal_qfd_matrix(self.hoq)

        # Baseline candidates
        self.cand_a = CandidateOptionVector(
            option_id="opt_balanced",
            option_name="Option Balanced",
            performance_vector={"EC-01": 4500.0, "EC-02": 12.0, "EC-03": 50.0},
            roof_penalty=0.0,
        )
        self.cand_b = CandidateOptionVector(
            option_id="opt_basic",
            option_name="Option Basic",
            performance_vector={"EC-01": 1000.0, "EC-02": 80.0, "EC-03": 60.0},
            roof_penalty=0.1,
        )
        self.candidates = [self.cand_a, self.cand_b]

    def test_01_clean_pass_on_valid_sealed_qfd_and_conforming_proposal(self) -> None:
        """Verifies clean pass when proposal strictly conforms to sealed QFD across all 4 barriers."""
        proposal_timestamp = self.hoq.timestamp_unix_ms + 10000
        declared_features = ["EC-01", "Throughput", "EC-02", "Latency", "EC-03"]
        proposal_text = (
            "We propose Option Balanced. We address the negative roof contradiction between "
            "EC-01 (Throughput) and EC-02 (Latency) by implementing adaptive backpressure "
            "and bounded ring buffers to prevent queue saturation."
        )

        result = self.auditor.audit_proposal(
            hoq=self.hoq,
            proposal_timestamp_ms=proposal_timestamp,
            declared_features=declared_features,
            proposal_text=proposal_text,
            recommended_option_id="opt_balanced",
            candidate_options=self.candidates,
            raise_on_error=True,
        )

        self.assertTrue(result.passed)
        self.assertEqual(len(result.violations), 0)
        self.assertEqual(result.checked_features_count, 5)
        self.assertEqual(result.qfd_merkle_root, self.hoq.merkle_root)
        self.assertGreater(result.audit_timestamp_ms, 0)

    def test_02_falsification_1_temporal_causality_violation(self) -> None:
        """Falsification 1: trips TemporalCausalityViolation if QFD is unsealed or timestamp is >= proposal timestamp."""
        # Case A: QFD is unsealed
        unsealed_hoq = self.engine.create_house_of_quality(
            matrix_id="HOQ-UNSEALED-001",
            target_soc_id="SOC-AUDIT-001",
            requirements=[self.req1],
            characteristics=[self.ec1],
            relationship_tensor={"CR-01": {"EC-01": RelationshipStrength.STRONG}},
        )
        with self.assertRaises(TemporalCausalityViolation) as ctx:
            self.auditor.audit_proposal(
                hoq=unsealed_hoq,
                proposal_timestamp_ms=int(time.time() * 1000),
                declared_features=["EC-01"],
                proposal_text="EC-01 Throughput text",
                raise_on_error=True,
            )
        self.assertIn("NOT cryptographically sealed", str(ctx.exception))

        # Case B: Proposal timestamp is older than QFD seal timestamp (time travel)
        past_proposal_timestamp = self.hoq.timestamp_unix_ms - 5000
        with self.assertRaises(TemporalCausalityViolation) as ctx:
            self.auditor.audit_proposal(
                hoq=self.hoq,
                proposal_timestamp_ms=past_proposal_timestamp,
                declared_features=["EC-01"],
                proposal_text="EC-01 Throughput and EC-02 Latency",
                raise_on_error=True,
            )
        self.assertIn("not strictly prior to proposal timestamp", str(ctx.exception))

    def test_03_falsification_2_orphan_feature_violation(self) -> None:
        """Falsification 2: trips OrphanFeatureViolation if proposal declares features with no QFD lineage."""
        proposal_timestamp = self.hoq.timestamp_unix_ms + 10000
        # "EC-99_unapproved_fancy_feature" has no grounding in hoq.included_characteristics
        rogue_features = ["EC-01", "EC-99_unapproved_fancy_feature"]
        proposal_text = "EC-01 Throughput and EC-02 Latency trade-offs are handled."

        with self.assertRaises(OrphanFeatureViolation) as ctx:
            self.auditor.audit_proposal(
                hoq=self.hoq,
                proposal_timestamp_ms=proposal_timestamp,
                declared_features=rogue_features,
                proposal_text=proposal_text,
                raise_on_error=True,
            )
        self.assertIn("Orphan Feature Violation", str(ctx.exception))
        self.assertIn("EC-99_unapproved_fancy_feature", str(ctx.exception))

    def test_04_falsification_3_roof_coverage_violation(self) -> None:
        """Falsification 3: trips RoofCoverageViolation if negative roof contradictions are unaddressed."""
        proposal_timestamp = self.hoq.timestamp_unix_ms + 10000
        declared_features = ["EC-01", "EC-02"]
        # Omission of EC-01 or EC-02 contradiction mitigation
        glossed_over_proposal_text = "Everything in this system is fast and reliable with zero trade-offs."

        with self.assertRaises(RoofCoverageViolation) as ctx:
            self.auditor.audit_proposal(
                hoq=self.hoq,
                proposal_timestamp_ms=proposal_timestamp,
                declared_features=declared_features,
                proposal_text=glossed_over_proposal_text,
                raise_on_error=True,
            )
        self.assertIn("Roof Coverage Violation", str(ctx.exception))
        self.assertIn("EC-01", str(ctx.exception))
        self.assertIn("EC-02", str(ctx.exception))

    def test_05_falsification_4_recommendation_parity_violation(self) -> None:
        """Falsification 4: trips RecommendationParityViolation if recommended option does not match MCDA Rank 1."""
        proposal_timestamp = self.hoq.timestamp_unix_ms + 10000
        declared_features = ["EC-01", "Throughput", "EC-02", "Latency"]
        proposal_text = "EC-01 Throughput and EC-02 Latency trade-offs resolved cleanly."

        # MCDA rank 1 will be opt_balanced, but proposal erroneously marks opt_basic
        with self.assertRaises(RecommendationParityViolation) as ctx:
            self.auditor.audit_proposal(
                hoq=self.hoq,
                proposal_timestamp_ms=proposal_timestamp,
                declared_features=declared_features,
                proposal_text=proposal_text,
                recommended_option_id="opt_basic",
                candidate_options=self.candidates,
                raise_on_error=True,
            )
        self.assertIn("Recommendation Parity Violation", str(ctx.exception))
        self.assertIn("opt_basic", str(ctx.exception))
        self.assertIn("opt_balanced", str(ctx.exception))


class TestSubprocessSmokeGate(unittest.TestCase):
    """Subprocess Smoke Gate ([NEG-G1B-002]): boots launcher in isolated OS process."""

    def test_01_gen_04b_cluster_launcher_subprocess_smoke(self) -> None:
        """Programmatically invokes generations/gen_04b/run.py in an isolated subprocess."""
        launcher_path = REPO_ROOT / "generations" / "gen_04b" / "run.py"
        self.assertTrue(launcher_path.exists(), f"Cluster launcher not found: {launcher_path}")
        self.assertGreater(launcher_path.stat().st_size, 0, "Zero-byte cluster launcher")

        start_time = time.perf_counter()
        proc = subprocess.Popen(
            [sys.executable, str(launcher_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(REPO_ROOT),
        )
        stdout, stderr = proc.communicate(timeout=10.0)
        duration = time.perf_counter() - start_time

        self.assertEqual(
            proc.returncode,
            0,
            f"Cluster launcher failed with exit code {proc.returncode}.\nSTDERR:\n{stderr}\nSTDOUT:\n{stdout}",
        )
        self.assertNotIn("ImportError", stderr)
        self.assertNotIn("ModuleNotFoundError", stderr)
        self.assertIn("[STATUS: HEALTHY] Generation 4b Cluster Operational", stdout)
        self.assertLess(duration, 10.0, "Cluster launcher exceeded maximum smoke timeout")


if __name__ == "__main__":
    unittest.main()
