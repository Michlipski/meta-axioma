"""IR-Driven Empirical Verification Test Suite for contract_byzantine_kinetic_facade."""

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
        instance_GossipPacket = GossipPacket()
        self.assertTrue(instance_GossipPacket.validate_invariants())
        setattr(instance_GossipPacket, 'epoch_round', -100)
        with self.assertRaises(DomainInvariantViolationError):
            instance_GossipPacket.validate_invariants()
        instance_LouverNode = LouverNode()
        self.assertTrue(instance_LouverNode.validate_invariants())
        setattr(instance_LouverNode, 'optical_encoder_calibrated', False)
        with self.assertRaises(DomainInvariantViolationError):
            instance_LouverNode.validate_invariants()
        instance_QuorumConsensusWitness = QuorumConsensusWitness()
        self.assertTrue(instance_QuorumConsensusWitness.validate_invariants())
        setattr(instance_QuorumConsensusWitness, 'active_neighbors_count', -98)
        with self.assertRaises(DomainInvariantViolationError):
            instance_QuorumConsensusWitness.validate_invariants()
        instance_WindShearTelemetry = WindShearTelemetry()
        self.assertTrue(instance_WindShearTelemetry.validate_invariants())
        setattr(instance_WindShearTelemetry, 'is_valid', False)
        with self.assertRaises(DomainInvariantViolationError):
            instance_WindShearTelemetry.validate_invariants()

    def test_compositional_contract_and_functorial_undo(self):
        service = GeneratedContractService()
        initial = {'optical_encoder_calibrated': True}
        after = service.MitigateAerodynamicShearCycle(initial)
        self.assertTrue(after['flat_lock_engaged'] == True)
        self.assertTrue(after['blade_angle_deg'] == 0)
        restored = service.undo(after)
        self.assertEqual(restored, initial)
        with self.assertRaises(PreConditionViolationError):
            service.MitigateAerodynamicShearCycle({})

    def test_hierarchical_statechart_transitions(self):
        machine = GeneratedStatechartMachine()
        initial_state = machine.active_state
        for evt in ['HW_OK', 'CALIBRATED', 'MESH_JOINED', 'SHEAR_DETECTED', 'PROPOSAL_BROADCAST', 'QUORUM_PREPARED', 'QUORUM_COMMITTED']:
            machine.send(evt)
        final_state = machine.active_state
        self.assertNotEqual(final_state, initial_state)
        reverted_state = machine.functorial_undo()
        self.assertNotEqual(reverted_state, final_state)
        with self.assertRaises(InvalidStateTransitionError):
            machine.send('__ILLEGAL_UNREGISTERED_EVENT__')

    def test_distributed_topology_fidelity(self):
        topo = GeneratedTopologyVerifier.load_and_verify()
        self.assertEqual(topo['topology_id'], 'topology_byzantine_kinetic_facade')
        self.assertGreaterEqual(len(topo.get('nodes', {})), 1)


if __name__ == '__main__':
    unittest.main()
