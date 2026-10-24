"""IR-Driven Empirical Verification Test Suite for contract_soc_epistemic_curiosity_engine."""

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
        instance_EpistemicValidatorGate = EpistemicValidatorGate()
        self.assertTrue(instance_EpistemicValidatorGate.validate_invariants())
        setattr(instance_EpistemicValidatorGate, 'quorum_valid', False)
        with self.assertRaises(DomainInvariantViolationError):
            instance_EpistemicValidatorGate.validate_invariants()
        instance_ExplorerKnowledgeBoundary = ExplorerKnowledgeBoundary()
        self.assertTrue(instance_ExplorerKnowledgeBoundary.validate_invariants())
        setattr(instance_ExplorerKnowledgeBoundary, 'mastery_of_morphisms', False)
        with self.assertRaises(DomainInvariantViolationError):
            instance_ExplorerKnowledgeBoundary.validate_invariants()
        instance_SocraticProbeSession = SocraticProbeSession()
        self.assertTrue(instance_SocraticProbeSession.validate_invariants())
        setattr(instance_SocraticProbeSession, 'latency_ms', 125)
        with self.assertRaises(DomainInvariantViolationError):
            instance_SocraticProbeSession.validate_invariants()

    def test_compositional_contract_and_functorial_undo(self):
        service = GeneratedContractService()
        initial = {'objects_and_arrows_mapped': True, 'associativity_axiom_verified': True, 'identity_morphism_verified': True, 'local_rtx4060_qwen_ready': True}
        after = service.TransitionToExploringFunctors(initial)
        self.assertTrue(after['mastery_of_morphisms'] == True)
        self.assertTrue(after['exploring_functors_entered'] == True)
        self.assertTrue(after['workflow_completed'] == True)
        self.assertTrue(after['state_persisted'] == True)
        restored = service.undo(after)
        self.assertEqual(restored, initial)
        with self.assertRaises(PreConditionViolationError):
            service.TransitionToExploringFunctors({})

    def test_hierarchical_statechart_transitions(self):
        machine = GeneratedStatechartMachine()
        initial_state = machine.active_state
        for evt in ['PROPOSE_COMPOSITION', 'VERIFY_MORPHISM_LAWS', 'REQUEST_HIGHER_ABSTRACTION', 'PREREQUISITE_SATISFIED', 'ELENCHUS_PASSED', 'ENTER_EXPLORING_FUNCTORS', 'VERIFY_FUNCTORIALITY', 'CERTIFY_ABSTRACTION']:
            machine.send(evt)
        final_state = machine.active_state
        self.assertNotEqual(final_state, initial_state)
        reverted_state = machine.functorial_undo()
        self.assertNotEqual(reverted_state, final_state)
        with self.assertRaises(InvalidStateTransitionError):
            machine.send('__ILLEGAL_UNREGISTERED_EVENT__')

    def test_distributed_topology_fidelity(self):
        topo = GeneratedTopologyVerifier.load_and_verify()
        self.assertEqual(topo['topology_id'], 'topo_soc_epistemic_curiosity_engine')
        self.assertGreaterEqual(len(topo.get('nodes', {})), 1)


if __name__ == '__main__':
    unittest.main()
