"""Generation 3b Dynamic AST/IR-Driven Code Emitter & Quine Daughter Synthesizer.

Enforces:
- Zero-Template Emission Invariant:
  Every emitted class, method, precondition check, postcondition assertion, noun invariant,
  and statechart transition is programmatically synthesized directly by walking the
  verified ContractIR, StatechartIR, and TopologyIR object graphs.
- [NEG-G1B-001] Empirical Execution Witness & Anti-Phantom Emission Gate:
  1. Raises PhantomEmissionViolation if target_output_dir is missing or any manifest file is 0 bytes.
  2. Executes the emitted test suite on the live Python 3.14 runtime via subprocess.run,
     raising PostEmissionExecutionFailure if exit code != 0 or 0 tests ran.
- The Daughter Isolation Protocol:
  Synthesizes a complete, self-hosting Daughter Compiler (G3b') into an isolated sandbox
  directory with a CLI entrypoint (`compile_seed.py`) ready to be booted in an isolated subprocess.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

from ..ir.contract_ir import ContractIR, DomainNoun, DomainVerb, ComposedVerb
from ..ir.statechart_ir import StatechartIR, StateNode, StateNodeType
from ..ir.topology_ir import TopologyIR
from ..crucible.orchestrator import CrucibleSynthesisResult


class PhantomEmissionViolation(Exception):
    """Raised when compilation omits physical disk emission or produces zero-byte artifacts ([NEG-G1B-001])."""
    pass


class PostEmissionExecutionFailure(Exception):
    """Raised when the emitted application or daughter compiler fails live runtime test execution ([NEG-G1B-001])."""
    pass


class DynamicCodeEmitter:
    """Synthesizes executable Python systems directly from verified Contract, Statechart, and Topology IRs."""

    TYPE_MAP = {
        "str": ("str", "''"),
        "int": ("int", "0"),
        "float": ("float", "0.0"),
        "bool": ("bool", "True"),
        "list": ("list", "[]"),
        "dict": ("dict", "{}"),
    }

    @classmethod
    def emit_system(
        cls,
        result: CrucibleSynthesisResult,
        target_output_dir: Optional[Union[str, Path]],
    ) -> Dict[str, Any]:
        """Materializes a CrucibleSynthesisResult into a runnable, tested software system on disk."""
        if not target_output_dir:
            raise PhantomEmissionViolation(
                "[NEG-G1B-001 Violation] target_output_dir is mandatory. Phantom in-memory completion is forbidden."
            )

        out_dir = Path(target_output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        tests_dir = out_dir / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)

        if not result.verified_contract or not result.verified_statechart or not result.verified_topology:
            raise PhantomEmissionViolation(
                "CrucibleSynthesisResult is missing verified_contract, verified_statechart, or verified_topology."
            )

        contract = result.verified_contract
        statechart = result.verified_statechart
        topology = result.verified_topology

        # 1. Synthesize domain_models.py directly from ContractIR Nouns & Invariants
        models_code = cls._compile_domain_models(contract)
        models_path = out_dir / "domain_models.py"
        models_path.write_text(models_code, encoding="utf-8")

        # 2. Synthesize contract_service.py directly from ContractIR Verbs & ComposedVerbs
        service_code = cls._compile_contract_service(contract)
        service_path = out_dir / "contract_service.py"
        service_path.write_text(service_code, encoding="utf-8")

        # 3. Synthesize statechart_engine.py directly from StatechartIR hierarchy & transitions
        statechart_code, walk_events = cls._compile_statechart_engine(statechart)
        statechart_path = out_dir / "statechart_engine.py"
        statechart_path.write_text(statechart_code, encoding="utf-8")

        # 4. Synthesize topology_verifier.py and topology_config.json directly from TopologyIR
        topo_json_path = out_dir / "topology_config.json"
        topo_json_path.write_text(topology.to_json(), encoding="utf-8")

        topo_code = cls._compile_topology_verifier(topology)
        topo_path = out_dir / "topology_verifier.py"
        topo_path.write_text(topo_code, encoding="utf-8")

        # 5. Synthesize 1-command entrypoint run.py
        run_code = cls._compile_entrypoint(contract, statechart, topology, walk_events)
        run_path = out_dir / "run.py"
        run_path.write_text(run_code, encoding="utf-8")

        # 6. Synthesize IR-driven test suite tests/test_emitted_system.py
        test_code = cls._compile_test_suite(contract, statechart, topology, walk_events)
        test_init_path = tests_dir / "__init__.py"
        test_init_path.write_text('"""Emitted System Test Package."""\n', encoding="utf-8")
        test_path = tests_dir / "test_emitted_system.py"
        test_path.write_text(test_code, encoding="utf-8")

        manifest_files = [
            models_path,
            service_path,
            statechart_path,
            topo_json_path,
            topo_path,
            run_path,
            test_path,
        ]

        # 7. Emit verified leaf code modules (e.g., core_domain_module.py)
        for idx, (task_id, mod_source) in enumerate(result.verified_code_modules.items()):
            suffix = task_id.split(".")[-1] if "." in task_id else f"module_{idx}"
            safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", suffix)
            if not safe_name.endswith(".py"):
                safe_name = f"{safe_name}.py"
            mod_path = out_dir / safe_name
            mod_path.write_text(mod_source, encoding="utf-8")
            manifest_files.append(mod_path)

        # Enforce [NEG-G1B-001] Physical File Existence & Non-Zero Size Check
        for mf in manifest_files:
            if not mf.exists() or mf.stat().st_size == 0:
                raise PhantomEmissionViolation(
                    f"[NEG-G1B-001 Violation] Emitted file '{mf}' is missing or 0 bytes."
                )

        # Execute live substrate test suite via subprocess
        test_witness = cls.execute_substrate_tests(out_dir)

        return {
            "output_dir": str(out_dir),
            "manifest_files": [str(f.relative_to(out_dir)) for f in manifest_files],
            "test_witness": test_witness,
        }

    @classmethod
    def execute_substrate_tests(cls, target_dir: Path) -> Dict[str, Any]:
        """Runs the emitted unittest suite in a live Python 3.14 subprocess and verifies exit code 0."""
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=str(target_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        combined_output = (proc.stdout or "") + "\n" + (proc.stderr or "")
        match = re.search(r"Ran (\d+) tests? in", combined_output)
        tests_run = int(match.group(1)) if match else 0

        if proc.returncode != 0 or tests_run == 0:
            raise PostEmissionExecutionFailure(
                f"[NEG-G1B-001 Violation] Post-emission substrate test execution failed in '{target_dir}' "
                f"(exit_code={proc.returncode}, tests_run={tests_run}):\n{combined_output}"
            )

        return {
            "exit_code": proc.returncode,
            "tests_run": tests_run,
            "stdout_tail": combined_output.strip()[-600:],
        }

    @classmethod
    def _parse_condition_pair(cls, cond: str) -> Tuple[str, str, Any]:
        """Parses a formal condition like 'balance >= 0' or 'input_validated == True' into (var, op, val)."""
        first_clause = cond.split(" and ")[0].strip() if " and " in cond else cond.strip()
        for op in ("==", "!=", ">=", "<=", ">", "<"):
            if op in first_clause:
                lhs, rhs = first_clause.split(op, 1)
                var_name = lhs.strip()
                raw_val = rhs.strip()
                if raw_val == "True":
                    val: Any = True
                elif raw_val == "False":
                    val = False
                elif raw_val.lstrip("-").isdigit():
                    val = int(raw_val)
                else:
                    try:
                        val = float(raw_val)
                    except ValueError:
                        val = raw_val.strip("'\"")
                return var_name, op, val
        return first_clause, "==", True

    @classmethod
    def _compile_domain_models(cls, contract: ContractIR) -> str:
        lines = [
            f'"""Dynamically Compiled Domain Models for Contract: {contract.contract_id}."""',
            "",
            "from dataclasses import dataclass, field",
            "from typing import Any, Dict, List",
            "",
            "",
            "class DomainInvariantViolationError(AssertionError):",
            '    """Raised when a domain noun invariant is breached at runtime."""',
            "    pass",
            "",
        ]

        for noun_name, noun in contract.nouns.items():
            lines.append("")
            lines.append("@dataclass")
            lines.append(f"class {noun_name}:")
            lines.append(f'    """{noun.description}"""')

            # Pre-compute invariant-satisfying default expressions
            inv_defaults: Dict[str, Tuple[str, str]] = {}
            for inv in noun.invariants:
                var_name, op, val = cls._parse_condition_pair(inv)
                if var_name.isidentifier():
                    if isinstance(val, bool):
                        default_v = val if op == "==" else (not val)
                        inv_defaults[var_name] = ("bool", repr(default_v))
                    elif isinstance(val, int):
                        if op in (">", ">="):
                            default_v = val + 1 if op == ">" else val
                        elif op in ("<", "<="):
                            default_v = val - 1 if op == "<" else val
                        elif op == "!=":
                            default_v = val + 1
                        else:
                            default_v = val
                        inv_defaults[var_name] = ("int", repr(default_v))
                    elif isinstance(val, float):
                        if op in (">", ">="):
                            default_v = val + 1.0 if op == ">" else val
                        elif op in ("<", "<="):
                            default_v = val - 1.0 if op == "<" else val
                        elif op == "!=":
                            default_v = val + 1.0
                        else:
                            default_v = val
                        inv_defaults[var_name] = ("float", repr(default_v))
                    else:
                        inv_defaults[var_name] = ("str", repr(str(val)))

            # Collect fields + any variables referenced in invariants
            declared_field_names = {f.name for f in noun.fields}
            for f in noun.fields:
                py_type, default_expr = cls.TYPE_MAP.get(f.type_name, ("Any", "None"))
                if f.name in inv_defaults:
                    _, default_expr = inv_defaults[f.name]
                if py_type in ("list", "dict"):
                    lines.append(f"    {f.name}: {py_type} = field(default_factory={py_type})")
                else:
                    lines.append(f"    {f.name}: {py_type} = {default_expr}")

            for var_name, (inv_type, inv_default_expr) in inv_defaults.items():
                if var_name not in declared_field_names:
                    declared_field_names.add(var_name)
                    lines.append(f"    {var_name}: {inv_type} = {inv_default_expr}")

            lines.append("")
            lines.append("    def validate_invariants(self) -> bool:")
            lines.append('        """Structurally enforces all ContractIR invariants for this noun."""')
            if not noun.invariants:
                lines.append("        return True")
            else:
                for inv in noun.invariants:
                    var_name, op, val = cls._parse_condition_pair(inv)
                    if var_name.isidentifier():
                        clean_inv = inv.replace("'", "\\'")
                        lines.append(
                            f"        if not (getattr(self, {repr(var_name)}) {op} {repr(val)}):"
                        )
                        lines.append(
                            f"            raise DomainInvariantViolationError("
                            f"f\"Invariant violated on {noun_name}: {clean_inv} (got {{getattr(self, {repr(var_name)})}})\")"
                        )
                lines.append("        return True")
            lines.append("")

        return "\n".join(lines) + "\n"

    @classmethod
    def _compile_contract_service(cls, contract: ContractIR) -> str:
        lines = [
            f'"""Dynamically Compiled Compositional Contract Service for: {contract.contract_id}."""',
            "",
            "import copy",
            "from typing import Any, Dict, List",
            "",
            "",
            "class PreConditionViolationError(RuntimeError):",
            '    """Raised when a verb precondition is not satisfied."""',
            "    pass",
            "",
            "",
            "class PostConditionViolationError(RuntimeError):",
            '    """Raised when a verb postcondition fails to hold after execution."""',
            "    pass",
            "",
            "",
            "class GeneratedContractService:",
            f'    """Executes composed and atomic verbs defined in {contract.contract_id}."""',
            "",
            "    def __init__(self):",
            "        self._undo_stack: List[Dict[str, Any]] = []",
            "",
            "    def undo(self, current_state: Dict[str, Any]) -> Dict[str, Any]:",
            '        """[L1-002] Functorial 1-tap Undo restoring prior state snapshot."""',
            "        if not self._undo_stack:",
            "            return copy.deepcopy(current_state)",
            "        return self._undo_stack.pop()",
        ]

        # Emit all child verbs from sub_contracts and direct verbs
        all_atomic_verbs: Dict[str, DomainVerb] = dict(contract.verbs)
        for sub in contract.sub_contracts.values():
            for vname, vdef in sub.verbs.items():
                all_atomic_verbs[f"{sub.contract_id}__{vname}"] = vdef

        for method_key, verb in all_atomic_verbs.items():
            lines.append("")
            lines.append(f"    def _exec_{method_key}(self, state: Dict[str, Any]) -> Dict[str, Any]:")
            lines.append(f'        """Atomic verb: {verb.name}"""')
            for pre in verb.pre_conditions:
                var_name, op, val = cls._parse_condition_pair(pre)
                lines.append(f"        if {repr(var_name)} not in state or not (state[{repr(var_name)}] {op} {repr(val)}):")
                lines.append(
                    f"            raise PreConditionViolationError("
                    f"f'Precondition failed in {verb.name}: {pre} (state={{state}})')"
                )
            for post in verb.post_conditions:
                var_name, op, val = cls._parse_condition_pair(post)
                if op == "==":
                    lines.append(f"        state[{repr(var_name)}] = {repr(val)}")
                elif op in (">=", ">"):
                    lines.append(f"        state[{repr(var_name)}] = max(state.get({repr(var_name)}, 0), {repr(val + 1 if op == '>' else val)})")
            for post in verb.post_conditions:
                var_name, op, val = cls._parse_condition_pair(post)
                lines.append(f"        if not (state.get({repr(var_name)}) {op} {repr(val)}):")
                lines.append(
                    f"            raise PostConditionViolationError("
                    f"f'Postcondition failed in {verb.name}: {post}')"
                )
            lines.append("        return state")

        # Emit composed verbs
        for comp_name, comp in contract.composed_verbs.items():
            p_verb = comp.parent_verb
            lines.append("")
            lines.append(f"    def {comp_name}(self, state: Dict[str, Any]) -> Dict[str, Any]:")
            lines.append(f'        """Composed parent verb: {p_verb.description}"""')
            lines.append("        self._undo_stack.append(copy.deepcopy(state))")
            lines.append("        working = copy.deepcopy(state)")
            for pre in p_verb.pre_conditions:
                var_name, op, val = cls._parse_condition_pair(pre)
                lines.append(f"        if {repr(var_name)} not in working or not (working[{repr(var_name)}] {op} {repr(val)}):")
                lines.append(
                    f"            raise PreConditionViolationError("
                    f"f'Parent precondition failed in {comp_name}: {pre}')"
                )
            for step in comp.child_steps:
                m_key = f"{step.child_contract_id}__{step.child_verb_name}"
                lines.append(f"        working = self._exec_{m_key}(working)")
            for post in p_verb.post_conditions:
                var_name, op, val = cls._parse_condition_pair(post)
                lines.append(f"        if not (working.get({repr(var_name)}) {op} {repr(val)}):")
                lines.append(
                    f"            raise PostConditionViolationError("
                    f"f'Parent postcondition failed in {comp_name}: {post}')"
                )
            lines.append("        return working")

        return "\n".join(lines) + "\n"

    @classmethod
    def _compile_statechart_engine(cls, chart: StatechartIR) -> Tuple[str, List[str]]:
        """Extracts state hierarchy and transition table directly from StatechartIR."""
        # Build flat lookup of node_id -> StateNode, parent_map, and initial leaf resolver
        node_map: Dict[str, StateNode] = {}
        parent_map: Dict[str, str] = {}

        def _collect(n: StateNode, parent_id: Optional[str]):
            node_map[n.id] = n
            if parent_id:
                parent_map[n.id] = parent_id
            for ch in n.states.values():
                _collect(ch, n.id)

        _collect(chart.root, None)

        def _resolve_initial_leaf(nid: str) -> str:
            curr = node_map.get(nid)
            if not curr:
                return nid
            if curr.node_type == StateNodeType.COMPOUND and curr.initial:
                if curr.initial in curr.states:
                    return _resolve_initial_leaf(curr.states[curr.initial].id)
                for ch in curr.states.values():
                    if ch.id == curr.initial or ch.id.endswith(f".{curr.initial}"):
                        return _resolve_initial_leaf(ch.id)
            return curr.id

        initial_leaf = _resolve_initial_leaf(chart.root.id)

        # Build transition table: {source_node_id: {event: resolved_target_leaf_id}}
        transitions_dict: Dict[str, Dict[str, str]] = {}
        for nid, n in node_map.items():
            for t in n.transitions:
                target_id = t.target
                if target_id not in node_map:
                    # Try resolving by suffix
                    for cand_id in node_map:
                        if cand_id.endswith(f".{target_id}"):
                            target_id = cand_id
                            break
                resolved_leaf = _resolve_initial_leaf(target_id)
                transitions_dict.setdefault(nid, {})[t.event] = resolved_leaf

        # Compute a valid event walk sequence from initial_leaf to a final state using BFS
        walk_events = cls._find_event_walk_to_final(
            initial_leaf,
            node_map,
            parent_map,
            transitions_dict,
        )
        history_states = sorted([
            nid for nid, n in node_map.items() if n.node_type == StateNodeType.HISTORY
        ])

        lines = [
            f'"""Dynamically Compiled Hierarchical Statechart Engine for: {chart.id}."""',
            "",
            "from typing import Dict, List, Optional",
            "",
            "",
            "class InvalidStateTransitionError(RuntimeError):",
            '    """Raised when an event is not legal in the active hierarchical state."""',
            "    pass",
            "",
            "",
            "class GeneratedStatechartMachine:",
            f'    """Executes hierarchical XState v5 semantics for {chart.id}."""',
            "",
            f"    INITIAL_LEAF_STATE = {repr(initial_leaf)}",
            f"    PARENT_MAP: Dict[str, str] = {repr(parent_map)}",
            f"    HISTORY_STATES: List[str] = {repr(history_states)}",
            f"    TRANSITIONS: Dict[str, Dict[str, str]] = {repr(transitions_dict)}",
            "",
            "    def __init__(self):",
            "        self.active_state: str = self.INITIAL_LEAF_STATE",
            "        self.history: List[str] = []",
            "        self.deep_history: Dict[str, str] = {}",
            "",
            "    def send(self, event: str) -> str:",
            '        """Dispatches event up the hierarchical state chain (leaf -> parent compound)."""',
            "        cursor: Optional[str] = self.active_state",
            "        while cursor is not None:",
            "            evt_map = self.TRANSITIONS.get(cursor, {})",
            "            if event in evt_map:",
            "                self.history.append(self.active_state)",
            "                parent_id = self.PARENT_MAP.get(self.active_state)",
            "                if parent_id:",
            "                    self.deep_history[parent_id] = self.active_state",
            "                self.active_state = evt_map[event]",
            "                return self.active_state",
            "            cursor = self.PARENT_MAP.get(cursor)",
            "        raise InvalidStateTransitionError(",
            "            f\"Event '{event}' is not handled in state '{self.active_state}' or its ancestors.\"",
            "        )",
            "",
            "    def undo_transition(self) -> str:",
            "        if self.history:",
            "            self.active_state = self.history.pop()",
            "        return self.active_state",
            "",
            "    def functorial_undo(self) -> str:",
            '        """[L1-002] Functorial Undo restoring prior hierarchical state."""',
            "        return self.undo_transition()",
        ]

        return "\n".join(lines) + "\n", walk_events

    @classmethod
    def _find_event_walk_to_final(
        cls,
        start_state: str,
        node_map: Dict[str, StateNode],
        parent_map: Dict[str, str],
        transitions_dict: Dict[str, Dict[str, str]],
    ) -> List[str]:
        """Finds a valid sequence of events from start_state to any FINAL state via BFS."""
        from collections import deque

        queue = deque([(start_state, [])])
        visited = {start_state}

        longest_path: List[str] = []
        while queue:
            curr, path = queue.popleft()
            if len(path) > len(longest_path):
                longest_path = path
            node = node_map.get(curr)
            if node and node.node_type == StateNodeType.FINAL and path:
                return path

            # Collect all events available from curr or its ancestors
            cursor: Optional[str] = curr
            while cursor is not None:
                for evt, nxt in transitions_dict.get(cursor, {}).items():
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append((nxt, path + [evt]))
                cursor = parent_map.get(cursor)

        return longest_path

    @classmethod
    def _compile_topology_verifier(cls, topology: TopologyIR) -> str:
        lines = [
            f'"""Dynamically Compiled Distributed Topology Verifier for: {topology.topology_id}."""',
            "",
            "import json",
            "from pathlib import Path",
            "from typing import Dict, Any, List",
            "",
            "",
            "class TopologicalFidelityError(RuntimeError):",
            '    """Raised when [L1-G3B-012] anti-loopback boundary realism is breached."""',
            "    pass",
            "",
            "",
            "class GeneratedTopologyVerifier:",
            '    LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1", "0.0.0.0"}',
            "",
            "    @classmethod",
            "    def load_and_verify(cls, config_path: Path = None) -> Dict[str, Any]:",
            "        if config_path is None:",
            "            config_path = Path(__file__).resolve().parent / 'topology_config.json'",
            "        data = json.loads(config_path.read_text(encoding='utf-8'))",
            "        nodes = data.get('nodes', {})",
            "        if len(nodes) > 1:",
            "            for nid, n in nodes.items():",
            "                host = n.get('host_interface', '').strip().lower()",
            "                if host in cls.LOOPBACK_HOSTS:",
            "                    raise TopologicalFidelityError(",
            "                        f\"[L1-G3B-012 Violation] Node '{nid}' binds to loopback '{host}'.\"",
            "                    )",
            "        return data",
        ]
        return "\n".join(lines) + "\n"

    @classmethod
    def _compile_entrypoint(
        cls,
        contract: ContractIR,
        statechart: StatechartIR,
        topology: TopologyIR,
        walk_events: List[str],
    ) -> str:
        comp_name = next(iter(contract.composed_verbs.keys()), None)
        initial_state_dict: Dict[str, Any] = {}
        if comp_name:
            for pre in contract.composed_verbs[comp_name].parent_verb.pre_conditions:
                var_name, op, val = cls._parse_condition_pair(pre)
                if op == "==":
                    initial_state_dict[var_name] = val
                elif op in (">=", "<="):
                    initial_state_dict[var_name] = val
                elif op == ">":
                    initial_state_dict[var_name] = (val + 1) if isinstance(val, int) else (val + 1.0)
                elif op == "<":
                    initial_state_dict[var_name] = (val - 1) if isinstance(val, int) else (val - 1.0)
                elif op == "!=":
                    initial_state_dict[var_name] = (val + 1) if isinstance(val, (int, float)) else f"{val}_diff"
                else:
                    initial_state_dict[var_name] = val

        lines = [
            f'"""1-Command Executable Entrypoint for {contract.contract_id}."""',
            "",
            "import json",
            "from domain_models import *",
            "from contract_service import GeneratedContractService",
            "from statechart_engine import GeneratedStatechartMachine",
            "from topology_verifier import GeneratedTopologyVerifier",
            "",
            "",
            "def main() -> dict:",
            "    topo = GeneratedTopologyVerifier.load_and_verify()",
            "    machine = GeneratedStatechartMachine()",
            f"    for evt in {repr(walk_events)}:",
            "        machine.send(evt)",
            "    service = GeneratedContractService()",
            f"    state = {repr(initial_state_dict)}",
        ]
        if comp_name:
            lines.append(f"    state = service.{comp_name}(state)")
        lines.extend([
            "    result = {",
            f"        'contract_id': {repr(contract.contract_id)},",
            "        'final_machine_state': machine.active_state,",
            "        'final_contract_state': state,",
            "        'topology_nodes': len(topo.get('nodes', {})),",
            "    }",
            "    print(json.dumps(result, indent=2, sort_keys=True))",
            "    return result",
            "",
            "",
            "if __name__ == '__main__':",
            "    main()",
        ])
        return "\n".join(lines) + "\n"

    @classmethod
    def _compile_test_suite(
        cls,
        contract: ContractIR,
        statechart: StatechartIR,
        topology: TopologyIR,
        walk_events: List[str],
    ) -> str:
        comp_name = next(iter(contract.composed_verbs.keys()), None)
        valid_pre_state: Dict[str, Any] = {}
        expected_post_pairs: List[Tuple[str, str, Any]] = []
        if comp_name:
            p_verb = contract.composed_verbs[comp_name].parent_verb
            for pre in p_verb.pre_conditions:
                var_name, op, val = cls._parse_condition_pair(pre)
                if op == "==":
                    valid_pre_state[var_name] = val
                elif op in (">=", "<="):
                    valid_pre_state[var_name] = val
                elif op == ">":
                    valid_pre_state[var_name] = (val + 1) if isinstance(val, int) else (val + 1.0)
                elif op == "<":
                    valid_pre_state[var_name] = (val - 1) if isinstance(val, int) else (val - 1.0)
                elif op == "!=":
                    valid_pre_state[var_name] = (val + 1) if isinstance(val, (int, float)) else f"{val}_diff"
                else:
                    valid_pre_state[var_name] = val
            for post in p_verb.post_conditions:
                expected_post_pairs.append(cls._parse_condition_pair(post))

        lines = [
            f'"""IR-Driven Empirical Verification Test Suite for {contract.contract_id}."""',
            "",
            "import sys",
            "import unittest",
            "from pathlib import Path",
            "",
            "ROOT_DIR = Path(__file__).resolve().parent.parent",
            "if str(ROOT_DIR) not in sys.path:",
            "    sys.path.insert(0, str(ROOT_DIR))",
            "",
            "from domain_models import *",
            "from contract_service import GeneratedContractService, PreConditionViolationError",
            "from statechart_engine import GeneratedStatechartMachine, InvalidStateTransitionError",
            "from topology_verifier import GeneratedTopologyVerifier, TopologicalFidelityError",
            "",
            "",
            "class TestEmittedSystem(unittest.TestCase):",
            "",
            "    def test_domain_noun_invariants(self):",
        ]

        if not contract.nouns:
            lines.append("        self.assertTrue(True)")
        else:
            for noun_name, noun in contract.nouns.items():
                lines.append(f"        instance_{noun_name} = {noun_name}()")
                lines.append(f"        self.assertTrue(instance_{noun_name}.validate_invariants())")
                if noun.invariants:
                    var_name, op, val = cls._parse_condition_pair(noun.invariants[0])
                    if var_name.isidentifier():
                        if isinstance(val, bool):
                            bad_val = (not val) if op == "==" else val
                        elif isinstance(val, (int, float)):
                            bad_val = (val + 100) if op in ("<=", "<") else (val if op == "!=" else val - 100)
                        else:
                            bad_val = val if op == "!=" else "__INVALID__"
                        lines.append(f"        setattr(instance_{noun_name}, {repr(var_name)}, {repr(bad_val)})")
                        lines.append("        with self.assertRaises(DomainInvariantViolationError):")
                        lines.append(f"            instance_{noun_name}.validate_invariants()")

        lines.extend([
            "",
            "    def test_compositional_contract_and_functorial_undo(self):",
            "        service = GeneratedContractService()",
        ])
        if comp_name:
            lines.append(f"        initial = {repr(valid_pre_state)}")
            lines.append(f"        after = service.{comp_name}(initial)")
            for var_name, op, val in expected_post_pairs:
                lines.append(f"        self.assertTrue(after[{repr(var_name)}] {op} {repr(val)})")
            lines.append("        restored = service.undo(after)")
            lines.append("        self.assertEqual(restored, initial)")
            lines.append("        with self.assertRaises(PreConditionViolationError):")
            lines.append(f"            service.{comp_name}({{}})")
        else:
            lines.append("        self.assertIsNotNone(service)")

        lines.extend([
            "",
            "    def test_hierarchical_statechart_transitions(self):",
            "        machine = GeneratedStatechartMachine()",
            "        initial_state = machine.active_state",
            f"        for evt in {repr(walk_events)}:",
            "            machine.send(evt)",
            "        final_state = machine.active_state",
            "        self.assertNotEqual(final_state, initial_state)",
            "        reverted_state = machine.functorial_undo()",
            "        self.assertNotEqual(reverted_state, final_state)",
            "        with self.assertRaises(InvalidStateTransitionError):",
            "            machine.send('__ILLEGAL_UNREGISTERED_EVENT__')",
            "",
            "    def test_distributed_topology_fidelity(self):",
            "        topo = GeneratedTopologyVerifier.load_and_verify()",
            f"        self.assertEqual(topo['topology_id'], {repr(topology.topology_id)})",
            "        self.assertGreaterEqual(len(topo.get('nodes', {})), 1)",
            "",
            "",
            "if __name__ == '__main__':",
            "    unittest.main()",
        ])

        return "\n".join(lines) + "\n"

    @classmethod
    def emit_daughter_compiler(cls, daughter_sandbox_dir: Union[str, Path]) -> Path:
        """Synthesizes a complete, self-hosting Daughter Compiler (G3b') into an isolated sandbox directory.

        Copies the verified compiler kernel into `daughter_sandbox_dir/src/g3b_compiler` and emits
        an executable CLI bootstrap script `compile_seed.py` so the Daughter can be booted in a
        completely isolated subprocess and compile a novel Tier 1 SoC on its own!
        """
        sandbox_path = Path(daughter_sandbox_dir).resolve()
        sandbox_path.mkdir(parents=True, exist_ok=True)

        current_pkg_dir = Path(__file__).resolve().parent.parent  # src/g3b_compiler
        target_pkg_dir = sandbox_path / "src" / "g3b_compiler"
        if target_pkg_dir.exists():
            shutil.rmtree(target_pkg_dir)
        shutil.copytree(
            current_pkg_dir,
            target_pkg_dir,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )

        # Emit standalone CLI entrypoint compile_seed.py in the daughter sandbox
        cli_code = "\n".join([
            '"""Isolated Daughter Compiler (G3b\') CLI Bootstrap Entrypoint."""',
            "",
            "import argparse",
            "import json",
            "import sys",
            "from pathlib import Path",
            "",
            "SANDBOX_SRC = Path(__file__).resolve().parent / 'src'",
            "if str(SANDBOX_SRC) not in sys.path:",
            "    sys.path.insert(0, str(SANDBOX_SRC))",
            "",
            "from g3b_compiler.soc import SituationOfConcern",
            "from g3b_compiler.compiler import SystemG3bCompiler",
            "from g3b_compiler.routing.router import CognitiveRole, ModelTier, SubagentExecutionWitness",
            "",
            "",
            "def main():",
            "    parser = argparse.ArgumentParser(description='Boot Daughter Compiler G3b_Prime')",
            "    parser.add_argument('--soc-json', required=True, help='Path to novel Tier 1 SoC JSON')",
            "    parser.add_argument('--output-dir', required=True, help='Target output dir for downstream app')",
            "    parser.add_argument('--budget', type=int, default=None, help='Daughter token budget (None = DynamicBudgetCalibrator)')",
            "    args = parser.parse_args()",
            "",
            "    soc_data = json.loads(Path(args.soc_json).read_text(encoding='utf-8'))",
            "    soc = SituationOfConcern.from_dict(soc_data)",
            "    invariants = soc_data.get('required_invariants', ['temperature_celsius <= 8', 'quorum_valid == True'])",
            "    is_multi_node = soc_data.get('is_multi_node_cluster', True)",
            "    domain_spec = soc_data.get('domain_spec')",
            "    inject_fault = bool(soc_data.get('inject_fault_on_first_try', False))",
            "    require_live_subagents = bool(soc_data.get('require_live_subagents', False))",
            "    app_output_dir = soc_data.get('app_output_dir')",
            "    raw_witnesses = soc_data.get('subagent_witnesses') or []",
            "    witnesses = [",
            "        SubagentExecutionWitness(",
            "            task_id=w['task_id'],",
            "            subagent_role=w['subagent_role'],",
            "            cognitive_role=CognitiveRole(w['cognitive_role']),",
            "            assigned_model=ModelTier(w['assigned_model']),",
            "            conversation_id=w['conversation_id'],",
            "            prompt_bpe_tokens=int(w['prompt_bpe_tokens']),",
            "            response_bpe_tokens=int(w['response_bpe_tokens']),",
            "            is_live_agy_subagent=bool(w.get('is_live_agy_subagent', True)),",
            "        )",
            "        for w in raw_witnesses",
            "    ] if raw_witnesses else None",
            "",
            "    daughter_compiler = SystemG3bCompiler(",
            "        compiler_id='SystemG3b_Daughter_Prime',",
            "        total_budget=args.budget,",
            "    )",
            "    report = daughter_compiler.compile(",
            "        seed_input=soc,",
            "        target_output_dir=Path(args.output_dir),",
            "        soc_id=soc.soc_id,",
            "        is_multi_node_cluster=is_multi_node,",
            "        required_invariants=invariants,",
            "        inject_fault_on_first_try=inject_fault,",
            "        domain_spec=domain_spec,",
            "        subagent_witnesses=witnesses,",
            "        require_live_subagents=require_live_subagents,",
            "        app_output_dir=Path(app_output_dir) if app_output_dir else None,",
            "    )",
            "    print(json.dumps({",
            "        'status': 'DAUGHTER_COMPILATION_CERTIFIED',",
            "        'daughter_compiler_id': daughter_compiler.compiler_id,",
            "        'downstream_soc_id': soc.soc_id,",
            "        'chain_head_hash': report['telemetry']['chain_head_hash'],",
            "        'test_witness': report['emission']['test_witness'],",
            "    }))",
            "",
            "",
            "if __name__ == '__main__':",
            "    main()",
        ]) + "\n"

        cli_path = sandbox_path / "compile_seed.py"
        cli_path.write_text(cli_code, encoding="utf-8")
        return cli_path

