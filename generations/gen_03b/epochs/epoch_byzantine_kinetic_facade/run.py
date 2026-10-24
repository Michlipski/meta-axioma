"""1-Command Executable Entrypoint for contract_byzantine_kinetic_facade."""

import json
from domain_models import *
from contract_service import GeneratedContractService
from statechart_engine import GeneratedStatechartMachine
from topology_verifier import GeneratedTopologyVerifier


def main() -> dict:
    topo = GeneratedTopologyVerifier.load_and_verify()
    machine = GeneratedStatechartMachine()
    for evt in ['HW_OK', 'CALIBRATED', 'MESH_JOINED', 'SHEAR_DETECTED', 'PROPOSAL_BROADCAST', 'QUORUM_PREPARED', 'QUORUM_COMMITTED']:
        machine.send(evt)
    service = GeneratedContractService()
    state = {'optical_encoder_calibrated': True}
    state = service.MitigateAerodynamicShearCycle(state)
    result = {
        'contract_id': 'contract_byzantine_kinetic_facade',
        'final_machine_state': machine.active_state,
        'final_contract_state': state,
        'topology_nodes': len(topo.get('nodes', {})),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == '__main__':
    main()
