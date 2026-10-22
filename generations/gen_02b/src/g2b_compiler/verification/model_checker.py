"""Model-Based Flow Verifier & Statechart Checker for System G1b (Guardrail 2).

Grounded in [L1-002] (Functorial State Evolution) and [L1-015] (Deterministic Automata Boundaries).
Enforces:
1. Root-to-leaf state reachability (BFS/DFS traversal from initial state).
2. 100% edge coverage test path synthesis.
3. Exhaustive negative / rejected transition testing.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
from g2b_compiler.ir.statechart_ir import StatechartIR, StateNode, Transition


class StateReachabilityViolation(Exception):
    """Raised when declared product states cannot be reached from root initial state."""
    pass


class IncompleteEdgeCoverageError(Exception):
    """Raised when generated test suites fail to traverse 100% of defined transitions."""
    pass


@dataclass
class TraversalPath:
    states: List[str]
    events: List[str]
    transitions: List[Transition]

    def length(self) -> int:
        return len(self.events)


@dataclass
class ModelCheckResult:
    is_valid: bool
    total_states: int
    reachable_states: List[str]
    unreachable_states: List[str]
    total_edges: int
    covering_paths: List[TraversalPath] = field(default_factory=list)
    negative_test_cases: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class StatechartModelChecker:
    """Verifies XState v5 Statechart IR models and synthesizes exhaustive test suites."""

    def __init__(self, statechart: StatechartIR):
        self.statechart = statechart
        self.adjacency: Dict[str, List[Tuple[str, Transition]]] = {}
        self.all_states: List[str] = []
        self.all_events: Set[str] = set()
        self._build_graph()

    def _build_graph(self):
        """Constructs flat directed graph from hierarchical Statechart IR operating over atomic configurations."""
        all_raw_paths = self.statechart.get_all_state_paths()
        # Atomic states are leaf states without children
        self.all_states = [s for s in all_raw_paths if not self._resolve_node(s).states]
        self.adjacency = {state: [] for state in self.all_states}
        self.all_events = set(self.statechart.events.keys())
        self.root_initial = self._resolve_leaf(self.statechart.initial)

        # Collect transitions for all atomic states (including inherited from ancestors)
        for state_path in self.all_states:
            ancestors = [state_path] + self._get_ancestor_paths(state_path)
            handled_events = set()
            for node_path in ancestors:
                node = self._resolve_node(node_path)
                if node:
                    for evt, transition in node.on.items():
                        if evt not in handled_events:
                            self.all_events.add(evt)
                            resolved_raw = self._resolve_target(state_path, transition.target)
                            target_leaf = self._resolve_leaf(resolved_raw)
                            self.adjacency[state_path].append((target_leaf, transition))
                            handled_events.add(evt)

    def _get_ancestor_paths(self, path: str) -> List[str]:
        parts = path.split(".")
        ancestors = []
        for i in range(1, len(parts)):
            ancestors.append(".".join(parts[:i]))
        return ancestors

    def _resolve_node(self, path: str) -> Optional[StateNode]:
        parts = path.split(".")
        current = self.statechart.states.get(parts[0])
        for p in parts[1:]:
            if current and p in current.states:
                current = current.states[p]
            else:
                return None
        return current

    def _resolve_leaf(self, path: str) -> str:
        """Recursively resolves a compound state down to its initial atomic leaf state."""
        node = self._resolve_node(path)
        while node and node.initial:
            path = f"{path}.{node.initial}"
            node = self._resolve_node(path)
        return path

    def _resolve_target(self, current_path: str, target: str) -> str:
        # 1. Exact match
        if self._resolve_node(target):
            return target
        # 2. Sibling / child of parent
        parent = ".".join(current_path.split(".")[:-1])
        scoped = f"{parent}.{target}" if parent else target
        if self._resolve_node(scoped):
            return scoped
        # 3. Child of current
        child = f"{current_path}.{target}"
        if self._resolve_node(child):
            return child
        # 4. Search all states
        all_raw = self.statechart.get_all_state_paths()
        for s in all_raw:
            if s.endswith(f".{target}") or s == target:
                return s
        return target

    def verify_reachability(self) -> Tuple[bool, List[str], List[str]]:
        """Verifies that all declared atomic states have valid paths from the root initial state."""
        if self.root_initial not in self.adjacency:
            return False, [], self.all_states

        visited: Set[str] = set()
        queue = deque([self.root_initial])
        visited.add(self.root_initial)

        while queue:
            curr = queue.popleft()
            for neighbor, _ in self.adjacency.get(curr, []):
                if neighbor not in visited and neighbor in self.adjacency:
                    visited.add(neighbor)
                    queue.append(neighbor)

        unreachable = [s for s in self.all_states if s not in visited]
        is_fully_reachable = len(unreachable) == 0
        return is_fully_reachable, sorted(list(visited)), sorted(unreachable)

    def synthesize_covering_paths(self) -> List[TraversalPath]:
        """Synthesizes a minimal set of paths traversing 100% of defined state transitions (edges)."""
        unvisited_edges: Set[Tuple[str, str, str]] = set()  # (from_state, event, to_state)

        for s_from, transitions in self.adjacency.items():
            for s_to, trans in transitions:
                unvisited_edges.add((s_from, trans.event, s_to))

        total_edges_count = len(unvisited_edges)
        if total_edges_count == 0:
            return [TraversalPath(states=[self.root_initial], events=[], transitions=[])]

        covering_paths: List[TraversalPath] = []

        # Find paths from initial state using BFS to cover edges
        while unvisited_edges:
            path = self._find_path_covering_edge(self.root_initial, unvisited_edges)
            if not path:
                # Break to avoid infinite loop if disconnected edge exists
                break
            covering_paths.append(path)
            for i in range(len(path.events)):
                edge = (path.states[i], path.events[i], path.states[i+1])
                unvisited_edges.discard(edge)

        return covering_paths

    def _find_path_covering_edge(self, start: str, target_edges: Set[Tuple[str, str, str]]) -> Optional[TraversalPath]:
        """BFS search from start to find and traverse an unvisited target edge, extending as much as possible."""
        # Queue contains (current_state, states_path, events_path, transitions_path)
        queue = deque([(start, [start], [], [])])
        visited_states_in_search = set()

        while queue:
            curr_state, states_seq, events_seq, trans_seq = queue.popleft()

            # Check neighbors
            for neighbor, trans in self.adjacency.get(curr_state, []):
                edge = (curr_state, trans.event, neighbor)
                new_states = states_seq + [neighbor]
                new_events = events_seq + [trans.event]
                new_trans = trans_seq + [trans]

                if edge in target_edges:
                    # Found target edge, attempt to greedily traverse more target edges
                    return self._extend_greedily(neighbor, new_states, new_events, new_trans, target_edges)

                # Keep searching
                state_sig = (curr_state, trans.event, neighbor)
                if state_sig not in visited_states_in_search:
                    visited_states_in_search.add(state_sig)
                    queue.append((neighbor, new_states, new_events, new_trans))

        return None

    def _extend_greedily(self, curr_state: str, states: List[str], events: List[str], trans: List[Transition], target_edges: Set[Tuple[str, str, str]]) -> TraversalPath:
        """Greedily extends a path while subsequent target edges are available."""
        curr = curr_state
        extended = True
        while extended:
            extended = False
            for neighbor, t in self.adjacency.get(curr, []):
                edge = (curr, t.event, neighbor)
                if edge in target_edges:
                    states.append(neighbor)
                    events.append(t.event)
                    trans.append(t)
                    target_edges.discard(edge)
                    curr = neighbor
                    extended = True
                    break
        return TraversalPath(states=states, events=events, transitions=trans)

    def synthesize_negative_transitions(self) -> List[Dict[str, Any]]:
        """Synthesizes negative test assertions for every state: events that must be rejected."""
        negative_tests: List[Dict[str, Any]] = []

        for state in self.all_states:
            valid_events = {trans.event for _, trans in self.adjacency.get(state, [])}
            invalid_events = self.all_events - valid_events

            for inv_event in sorted(list(invalid_events)):
                negative_tests.append({
                    "state": state,
                    "rejected_event": inv_event,
                    "expected_outcome": "NOOP_OR_REJECT",
                    "assertion": f"Sending '{inv_event}' to state '{state}' must not cause state mutation or error leakage."
                })

        return negative_tests

    def run_full_check(self) -> ModelCheckResult:
        """Executes full model check: reachability, 100% edge covering paths, and negative tests."""
        reachable, reachable_states, unreachable = self.verify_reachability()
        errors = []

        if not reachable:
            errors.append(f"Unreachable states detected ({len(unreachable)}): {', '.join(unreachable)}")

        # Calculate total edges
        total_edges = sum(len(transitions) for transitions in self.adjacency.values())

        covering_paths = self.synthesize_covering_paths()
        negative_tests = self.synthesize_negative_transitions()

        # Check coverage
        covered_edges = set()
        for p in covering_paths:
            for i in range(len(p.events)):
                covered_edges.add((p.states[i], p.events[i], p.states[i+1]))

        if len(covered_edges) < total_edges:
            uncovered_count = total_edges - len(covered_edges)
            errors.append(f"Incomplete edge coverage: {uncovered_count} transitions could not be traversed from initial state.")

        is_valid = len(errors) == 0

        return ModelCheckResult(
            is_valid=is_valid,
            total_states=len(self.all_states),
            reachable_states=reachable_states,
            unreachable_states=unreachable,
            total_edges=total_edges,
            covering_paths=covering_paths,
            negative_test_cases=negative_tests,
            errors=errors
        )
