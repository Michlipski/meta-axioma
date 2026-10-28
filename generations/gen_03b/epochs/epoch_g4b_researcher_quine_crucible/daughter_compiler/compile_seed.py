"""Isolated Daughter Compiler (G3b') CLI Bootstrap Entrypoint."""

import argparse
import json
import sys
from pathlib import Path

SANDBOX_SRC = Path(__file__).resolve().parent / 'src'
if str(SANDBOX_SRC) not in sys.path:
    sys.path.insert(0, str(SANDBOX_SRC))

from g3b_compiler.soc import SituationOfConcern
from g3b_compiler.compiler import SystemG3bCompiler
from g3b_compiler.routing.router import CognitiveRole, ModelTier, SubagentExecutionWitness


def main():
    parser = argparse.ArgumentParser(description='Boot Daughter Compiler G3b_Prime')
    parser.add_argument('--soc-json', required=True, help='Path to novel Tier 1 SoC JSON')
    parser.add_argument('--output-dir', required=True, help='Target output dir for downstream app')
    parser.add_argument('--budget', type=int, default=None, help='Daughter token budget (None = DynamicBudgetCalibrator)')
    args = parser.parse_args()

    soc_data = json.loads(Path(args.soc_json).read_text(encoding='utf-8'))
    soc = SituationOfConcern.from_dict(soc_data)
    invariants = soc_data.get('required_invariants', ['temperature_celsius <= 8', 'quorum_valid == True'])
    is_multi_node = soc_data.get('is_multi_node_cluster', True)
    domain_spec = soc_data.get('domain_spec')
    inject_fault = bool(soc_data.get('inject_fault_on_first_try', False))
    require_live_subagents = bool(soc_data.get('require_live_subagents', False))
    app_output_dir = soc_data.get('app_output_dir')
    raw_witnesses = soc_data.get('subagent_witnesses') or []
    witnesses = [
        SubagentExecutionWitness(
            task_id=w['task_id'],
            subagent_role=w['subagent_role'],
            cognitive_role=CognitiveRole(w['cognitive_role']),
            assigned_model=ModelTier(w['assigned_model']),
            conversation_id=w['conversation_id'],
            prompt_bpe_tokens=int(w['prompt_bpe_tokens']),
            response_bpe_tokens=int(w['response_bpe_tokens']),
            is_live_agy_subagent=bool(w.get('is_live_agy_subagent', True)),
        )
        for w in raw_witnesses
    ] if raw_witnesses else None

    daughter_compiler = SystemG3bCompiler(
        compiler_id='SystemG3b_Daughter_Prime',
        total_budget=args.budget,
    )
    report = daughter_compiler.compile(
        seed_input=soc,
        target_output_dir=Path(args.output_dir),
        soc_id=soc.soc_id,
        is_multi_node_cluster=is_multi_node,
        required_invariants=invariants,
        inject_fault_on_first_try=inject_fault,
        domain_spec=domain_spec,
        subagent_witnesses=witnesses,
        require_live_subagents=require_live_subagents,
        app_output_dir=Path(app_output_dir) if app_output_dir else None,
    )
    print(json.dumps({
        'status': 'DAUGHTER_COMPILATION_CERTIFIED',
        'daughter_compiler_id': daughter_compiler.compiler_id,
        'downstream_soc_id': soc.soc_id,
        'chain_head_hash': report['telemetry']['chain_head_hash'],
        'test_witness': report['emission']['test_witness'],
    }))


if __name__ == '__main__':
    main()
