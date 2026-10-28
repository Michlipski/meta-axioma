"""1-Command Executable Entrypoint for contract_g4b_researcher."""

import json
from domain_models import *
from contract_service import GeneratedContractService
from statechart_engine import GeneratedStatechartMachine
from topology_verifier import GeneratedTopologyVerifier


def main() -> dict:
    topo = GeneratedTopologyVerifier.load_and_verify()
    machine = GeneratedStatechartMachine()
    for evt in ['EV_BOOT_POST', 'EV_BOOT_READY', 'EV_ISLANDS_SEEDED', 'EV_HYPOTHESIS_FORMULATED', 'EV_BOUNDARIES_MAPPED', 'EV_DISCOVERY_CERTIFIED', 'EV_EVALUATE_NOVELTY', 'EV_TABOO_SATISFIED', 'EV_NEGATION_APPLIED', 'EV_STRESS_PASSED', 'EV_PARETO_OPTIMAL', 'EV_EMIT_DELIVERABLES', 'EV_BUILDER_ATTACHED', 'EV_SUBMIT_RFC', 'EV_AMENDMENT_PROVED', 'EV_ALL_RFCS_RESOLVED', 'EV_SEAL_CRUCIBLE']:
        machine.send(evt)
    service = GeneratedContractService()
    state = {'exploratory_token_lease': 60000}
    state = service.ComposeEpistemicDiscovery(state)
    result = {
        'contract_id': 'contract_g4b_researcher',
        'final_machine_state': machine.active_state,
        'final_contract_state': state,
        'topology_nodes': len(topo.get('nodes', {})),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == '__main__':
    main()
