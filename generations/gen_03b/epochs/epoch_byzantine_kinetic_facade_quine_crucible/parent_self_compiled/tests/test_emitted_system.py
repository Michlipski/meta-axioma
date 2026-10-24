"""IR-Driven Empirical Verification Test Suite for contract_soc_system_g3b_facade_quine."""

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
        instance_CoreEntity = CoreEntity()
        self.assertTrue(instance_CoreEntity.validate_invariants())
        setattr(instance_CoreEntity, 'daughter_exit_code', -100)
        with self.assertRaises(DomainInvariantViolationError):
            instance_CoreEntity.validate_invariants()

    def test_compositional_contract_and_functorial_undo(self):
        service = GeneratedContractService()
        initial = {'input_validated': True}
        after = service.ExecuteWorkflow(initial)
        self.assertTrue(after['workflow_completed'] == True)
        self.assertTrue(after['state_persisted'] == True)
        restored = service.undo(after)
        self.assertEqual(restored, initial)
        with self.assertRaises(PreConditionViolationError):
            service.ExecuteWorkflow({})

    def test_hierarchical_statechart_transitions(self):
        machine = GeneratedStatechartMachine()
        initial_state = machine.active_state
        for evt in ['START', 'FINISH']:
            machine.send(evt)
        final_state = machine.active_state
        self.assertNotEqual(final_state, initial_state)
        reverted_state = machine.functorial_undo()
        self.assertNotEqual(reverted_state, final_state)
        with self.assertRaises(InvalidStateTransitionError):
            machine.send('__ILLEGAL_UNREGISTERED_EVENT__')

    def test_distributed_topology_fidelity(self):
        topo = GeneratedTopologyVerifier.load_and_verify()
        self.assertEqual(topo['topology_id'], 'topo_soc_system_g3b_facade_quine')
        self.assertGreaterEqual(len(topo.get('nodes', {})), 1)


if __name__ == '__main__':
    unittest.main()
