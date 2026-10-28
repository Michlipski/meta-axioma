"""IR-Driven Empirical Verification Test Suite for contract_g4b_researcher."""

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from domain_models import *
from contract_service import GeneratedContractService, PreConditionViolationError
from statechart_engine import GeneratedStatechartMachine, InvalidStateTransitionError
from topology_verifier import GeneratedTopologyVerifier, TopologicalFidelityError


class TestEmittedSystem(unittest.TestCase):

    def test_domain_noun_invariants(self):
        instance_ByzantineFuzzVector = ByzantineFuzzVector()
        self.assertTrue(instance_ByzantineFuzzVector.validate_invariants())
        instance_ConstraintAnalysis = ConstraintAnalysis()
        self.assertTrue(instance_ConstraintAnalysis.validate_invariants())
        setattr(instance_ConstraintAnalysis, 'physical_latency_budget_ms', -100)
        with self.assertRaises(DomainInvariantViolationError):
            instance_ConstraintAnalysis.validate_invariants()
        instance_DialecticalNegationSeed = DialecticalNegationSeed()
        self.assertTrue(instance_DialecticalNegationSeed.validate_invariants())
        instance_EmpiricalTelemetryReport = EmpiricalTelemetryReport()
        self.assertTrue(instance_EmpiricalTelemetryReport.validate_invariants())
        setattr(instance_EmpiricalTelemetryReport, 'substrate_test_exit_code', -100)
        with self.assertRaises(DomainInvariantViolationError):
            instance_EmpiricalTelemetryReport.validate_invariants()
        instance_EpistemicCrucibleTarget = EpistemicCrucibleTarget()
        self.assertTrue(instance_EpistemicCrucibleTarget.validate_invariants())
        setattr(instance_EpistemicCrucibleTarget, 'required_island_count', -97)
        with self.assertRaises(DomainInvariantViolationError):
            instance_EpistemicCrucibleTarget.validate_invariants()
        instance_ExtremeBoundaryArchetype = ExtremeBoundaryArchetype()
        self.assertTrue(instance_ExtremeBoundaryArchetype.validate_invariants())
        setattr(instance_ExtremeBoundaryArchetype, 'stress_magnitude', -100.0)
        with self.assertRaises(DomainInvariantViolationError):
            instance_ExtremeBoundaryArchetype.validate_invariants()
        instance_FailureModeModel = FailureModeModel()
        self.assertTrue(instance_FailureModeModel.validate_invariants())
        instance_FormalProofArtifact = FormalProofArtifact()
        self.assertTrue(instance_FormalProofArtifact.validate_invariants())
        instance_FunctorialUndoCheckpoint = FunctorialUndoCheckpoint()
        self.assertTrue(instance_FunctorialUndoCheckpoint.validate_invariants())
        instance_HypothesisDefinition = HypothesisDefinition()
        self.assertTrue(instance_HypothesisDefinition.validate_invariants())
        instance_MerkleDagWitness = MerkleDagWitness()
        self.assertTrue(instance_MerkleDagWitness.validate_invariants())
        instance_NoveltyArchiveEntry = NoveltyArchiveEntry()
        self.assertTrue(instance_NoveltyArchiveEntry.validate_invariants())
        setattr(instance_NoveltyArchiveEntry, 'novelty_score', -100.0)
        with self.assertRaises(DomainInvariantViolationError):
            instance_NoveltyArchiveEntry.validate_invariants()
        instance_ResearchDeliverableBundle = ResearchDeliverableBundle()
        self.assertTrue(instance_ResearchDeliverableBundle.validate_invariants())
        instance_SpecAdjustmentRequest = SpecAdjustmentRequest()
        self.assertTrue(instance_SpecAdjustmentRequest.validate_invariants())
        instance_SpecAmendment = SpecAmendment()
        self.assertTrue(instance_SpecAmendment.validate_invariants())
        instance_TabooDistanceMatrix = TabooDistanceMatrix()
        self.assertTrue(instance_TabooDistanceMatrix.validate_invariants())
        setattr(instance_TabooDistanceMatrix, 'min_distance_threshold', -99.6)
        with self.assertRaises(DomainInvariantViolationError):
            instance_TabooDistanceMatrix.validate_invariants()
        instance_TradeoffMatrix = TradeoffMatrix()
        self.assertTrue(instance_TradeoffMatrix.validate_invariants())
        instance_ZeroContextIslandManifest = ZeroContextIslandManifest()
        self.assertTrue(instance_ZeroContextIslandManifest.validate_invariants())
        setattr(instance_ZeroContextIslandManifest, 'quarantine_token_budget', -100)
        with self.assertRaises(DomainInvariantViolationError):
            instance_ZeroContextIslandManifest.validate_invariants()

    def test_compositional_contract_and_functorial_undo(self):
        service = GeneratedContractService()
        initial = {'exploratory_token_lease': 60000}
        after = service.ComposeEpistemicDiscovery(initial)
        self.assertTrue(after['is_certified'] == True)
        restored = service.undo(after)
        self.assertEqual(restored, initial)
        with self.assertRaises(PreConditionViolationError):
            service.ComposeEpistemicDiscovery({})

    def test_hierarchical_statechart_transitions(self):
        machine = GeneratedStatechartMachine()
        initial_state = machine.active_state
        for evt in ['EV_BOOT_POST', 'EV_BOOT_READY', 'EV_ISLANDS_SEEDED', 'EV_HYPOTHESIS_FORMULATED', 'EV_BOUNDARIES_MAPPED', 'EV_DISCOVERY_CERTIFIED', 'EV_EVALUATE_NOVELTY', 'EV_TABOO_SATISFIED', 'EV_NEGATION_APPLIED', 'EV_STRESS_PASSED', 'EV_PARETO_OPTIMAL', 'EV_EMIT_DELIVERABLES', 'EV_BUILDER_ATTACHED', 'EV_SUBMIT_RFC', 'EV_AMENDMENT_PROVED', 'EV_ALL_RFCS_RESOLVED', 'EV_SEAL_CRUCIBLE']:
            machine.send(evt)
        final_state = machine.active_state
        self.assertNotEqual(final_state, initial_state)
        reverted_state = machine.functorial_undo()
        self.assertNotEqual(reverted_state, final_state)
        with self.assertRaises(InvalidStateTransitionError):
            machine.send('__ILLEGAL_UNREGISTERED_EVENT__')

    def test_distributed_topology_fidelity(self):
        topo = GeneratedTopologyVerifier.load_and_verify()
        self.assertEqual(topo['topology_id'], 'topology_g4b_researcher')
        self.assertGreaterEqual(len(topo.get('nodes', {})), 1)


if __name__ == '__main__':
    unittest.main()
