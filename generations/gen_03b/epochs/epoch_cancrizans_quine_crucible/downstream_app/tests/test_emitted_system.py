"""IR-Driven Empirical Verification Test Suite for contract_soc_euclidean_canon_studio."""

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
        instance_ContrapuntalBraidAudit = ContrapuntalBraidAudit()
        self.assertTrue(instance_ContrapuntalBraidAudit.validate_invariants())
        setattr(instance_ContrapuntalBraidAudit, 'consonance_certified', False)
        with self.assertRaises(DomainInvariantViolationError):
            instance_ContrapuntalBraidAudit.validate_invariants()
        instance_EuclideanNecklace = EuclideanNecklace()
        self.assertTrue(instance_EuclideanNecklace.validate_invariants())
        setattr(instance_EuclideanNecklace, 'bjorklund_evenness_verified', False)
        with self.assertRaises(DomainInvariantViolationError):
            instance_EuclideanNecklace.validate_invariants()
        instance_TopologicalCanonManifold = TopologicalCanonManifold()
        self.assertTrue(instance_TopologicalCanonManifold.validate_invariants())
        setattr(instance_TopologicalCanonManifold, 'mobius_closure_valid', False)
        with self.assertRaises(DomainInvariantViolationError):
            instance_TopologicalCanonManifold.validate_invariants()

    def test_compositional_contract_and_functorial_undo(self):
        service = GeneratedContractService()
        initial = {'pulses_and_steps_valid': True, 'coprime_lcm_bounded': True, 'canon_operator_selected': True}
        after = service.CompileAndCertifyTopologicalCanon(initial)
        self.assertTrue(after['bjorklund_evenness_verified'] == True)
        self.assertTrue(after['mobius_closure_valid'] == True)
        self.assertTrue(after['consonance_certified'] == True)
        self.assertTrue(after['workflow_completed'] == True)
        self.assertTrue(after['state_persisted'] == True)
        restored = service.undo(after)
        self.assertEqual(restored, initial)
        with self.assertRaises(PreConditionViolationError):
            service.CompileAndCertifyTopologicalCanon({})

    def test_hierarchical_statechart_transitions(self):
        machine = GeneratedStatechartMachine()
        initial_state = machine.active_state
        for evt in ['INSCRIBE_POLYGON', 'VERIFY_MAXIMAL_EVENNESS', 'FOLD_CANON_MANIFOLD', 'COMPUTE_CRAB_OR_MOEBIUS', 'VERIFY_BRAID_CLOSURE', 'ENTER_CONTRAPUNTAL_AUDIT', 'CERTIFY_CONSONANCE_MATRIX', 'SEAL_CANON_SCORE']:
            machine.send(evt)
        final_state = machine.active_state
        self.assertNotEqual(final_state, initial_state)
        reverted_state = machine.functorial_undo()
        self.assertNotEqual(reverted_state, final_state)
        with self.assertRaises(InvalidStateTransitionError):
            machine.send('__ILLEGAL_UNREGISTERED_EVENT__')

    def test_distributed_topology_fidelity(self):
        topo = GeneratedTopologyVerifier.load_and_verify()
        self.assertEqual(topo['topology_id'], 'topo_soc_euclidean_canon_studio')
        self.assertGreaterEqual(len(topo.get('nodes', {})), 1)


if __name__ == '__main__':
    unittest.main()
