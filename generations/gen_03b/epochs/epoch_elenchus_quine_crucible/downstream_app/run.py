"""1-Command Executable Entrypoint for contract_soc_epistemic_curiosity_engine."""

import json
from domain_models import *
from contract_service import GeneratedContractService
from statechart_engine import GeneratedStatechartMachine
from topology_verifier import GeneratedTopologyVerifier


def main() -> dict:
    topo = GeneratedTopologyVerifier.load_and_verify()
    machine = GeneratedStatechartMachine()
    for evt in ['PROPOSE_COMPOSITION', 'VERIFY_MORPHISM_LAWS', 'REQUEST_HIGHER_ABSTRACTION', 'PREREQUISITE_SATISFIED', 'ELENCHUS_PASSED', 'ENTER_EXPLORING_FUNCTORS', 'VERIFY_FUNCTORIALITY', 'CERTIFY_ABSTRACTION']:
        machine.send(evt)
    service = GeneratedContractService()
    state = {'objects_and_arrows_mapped': True, 'associativity_axiom_verified': True, 'identity_morphism_verified': True, 'local_rtx4060_qwen_ready': True}
    state = service.TransitionToExploringFunctors(state)
    result = {
        'contract_id': 'contract_soc_epistemic_curiosity_engine',
        'final_machine_state': machine.active_state,
        'final_contract_state': state,
        'topology_nodes': len(topo.get('nodes', {})),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == '__main__':
    main()
