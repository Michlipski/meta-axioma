"""1-Command Executable Entrypoint for contract_soc_heliotropic_microclimate_studio."""

import json
from domain_models import *
from contract_service import GeneratedContractService
from statechart_engine import GeneratedStatechartMachine
from topology_verifier import GeneratedTopologyVerifier


def main() -> dict:
    topo = GeneratedTopologyVerifier.load_and_verify()
    machine = GeneratedStatechartMachine()
    for evt in ['START', 'FINISH']:
        machine.send(evt)
    service = GeneratedContractService()
    state = {'input_validated': True}
    state = service.ExecuteWorkflow(state)
    result = {
        'contract_id': 'contract_soc_heliotropic_microclimate_studio',
        'final_machine_state': machine.active_state,
        'final_contract_state': state,
        'topology_nodes': len(topo.get('nodes', {})),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == '__main__':
    main()
