"""1-Command Executable Entrypoint for contract_soc_euclidean_canon_studio."""

import json
from domain_models import *
from contract_service import GeneratedContractService
from statechart_engine import GeneratedStatechartMachine
from topology_verifier import GeneratedTopologyVerifier


def main() -> dict:
    topo = GeneratedTopologyVerifier.load_and_verify()
    machine = GeneratedStatechartMachine()
    for evt in ['INSCRIBE_POLYGON', 'VERIFY_MAXIMAL_EVENNESS', 'FOLD_CANON_MANIFOLD', 'COMPUTE_CRAB_OR_MOEBIUS', 'VERIFY_BRAID_CLOSURE', 'ENTER_CONTRAPUNTAL_AUDIT', 'CERTIFY_CONSONANCE_MATRIX', 'SEAL_CANON_SCORE']:
        machine.send(evt)
    service = GeneratedContractService()
    state = {'pulses_and_steps_valid': True, 'coprime_lcm_bounded': True, 'canon_operator_selected': True}
    state = service.CompileAndCertifyTopologicalCanon(state)
    result = {
        'contract_id': 'contract_soc_euclidean_canon_studio',
        'final_machine_state': machine.active_state,
        'final_contract_state': state,
        'topology_nodes': len(topo.get('nodes', {})),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == '__main__':
    main()
