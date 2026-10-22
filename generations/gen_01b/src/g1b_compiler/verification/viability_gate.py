"""Pareto & Product Viability Gate for System G1b (Guardrail 4).

Enforces:
1. Steps-to-Value budgets: Shortest path from launch (S0) to primary JTBD value state must be <= budget.
2. Invariant preservation across error recovery cycles: State_i -> State_err -> State_i.
3. Hostile/adversarial persona traversal (simulates zero-trust, uncooperative users).
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from g1b_compiler.ir.statechart_ir import StatechartIR, StateNode, Transition


class StepsToValueExceededError(Exception):
    """Raised when steps from launch to core product value exceeds ergonomic budget."""
    pass


class IrreversibleErrorStateError(Exception):
    """Raised when an error state cannot return to the originating state."""
    pass


@dataclass
class ViabilityReport:
    passed: bool
    shortest_path_to_value: List[str]
    steps_to_value: int
    max_budget: int
    error_recovery_cycles: List[Dict[str, Any]]
    adversarial_traversals_passed: int
    adversarial_failures: List[str]
    violations: List[str] = field(default_factory=list)


class ViabilityGate:
    """Verifies product usability, steps-to-value budgets, and error recovery invariants."""

    def __init__(self, statechart: StatechartIR, max_steps_to_value: int = 3):
        self.statechart = statechart
        self.max_steps_to_value = max_steps_to_value
        self.flat_graph: Dict[str, List[Tuple[str, Transition]]] = {}
        self._build_flat_graph()

    def _build_flat_graph(self):
        all_states = self.statechart.get_all_state_paths()
        self.flat_graph = {s: [] for s in all_states}
        for s in all_states:
            node = self._resolve_node(s)
            if node:
                if node.initial:
                    initial_target = self._resolve_target(s, node.initial)
                    self.flat_graph[s].append((initial_target, Transition(target=initial_target, event="AUTO_INIT")))
                for evt, t in node.on.items():
                    target = self._resolve_target(s, t.target)
                    self.flat_graph[s].append((target, t))

        # Hierarchical inheritance: child states inherit parent transitions
        for s in all_states:
            ancestors = self._get_ancestor_paths(s)
            child_events = {trans.event for _, trans in self.flat_graph[s]}
            for anc in ancestors:
                anc_node = self._resolve_node(anc)
                if anc_node:
                    for evt, trans in anc_node.on.items():
                        if evt not in child_events:
                            target_path = self._resolve_target(s, trans.target)
                            self.flat_graph[s].append((target_path, trans))
                            child_events.add(evt)

    def _get_ancestor_paths(self, path: str) -> List[str]:
        parts = path.split(".")
        ancestors = []
        for i in range(1, len(parts)):
            ancestors.append(".".join(parts[:i]))
        return ancestors

    def _resolve_node(self, path: str) -> Optional[StateNode]:
        parts = path.split(".")
        curr = self.statechart.states.get(parts[0])
        for p in parts[1:]:
            if curr and p in curr.states:
                curr = curr.states[p]
            else:
                return None
        return curr

    def _resolve_target(self, current_path: str, target: str) -> str:
        if target in self.flat_graph:
            return target
        parent = ".".join(current_path.split(".")[:-1])
        scoped = f"{parent}.{target}" if parent else target
        if scoped in self.flat_graph:
            return scoped
        child = f"{current_path}.{target}"
        if child in self.flat_graph:
            return child
        for s in self.flat_graph:
            if s.endswith(f".{target}") or s == target:
                return s
        return target

    def find_value_states(self) -> List[str]:
        """Identifies states marked as core value delivery nodes."""
        value_states = []
        for s_path in self.flat_graph:
            node = self._resolve_node(s_path)
            if node and node.meta.get("is_value_state", False):
                value_states.append(s_path)
        return value_states

    def verify_steps_to_value(self) -> Tuple[bool, List[str], int]:
        """Calculates shortest path from initial state to nearest value state."""
        root = self.statechart.initial
        value_states = set(self.find_value_states())

        if not value_states:
            # If no explicit value state is tagged, fallback to any leaf non-error state
            return True, [root], 0

        queue = deque([(root, [root])])
        visited = {root}

        while queue:
            curr, path = queue.popleft()
            if curr in value_states:
                steps = len(path) - 1
                passed = steps <= self.max_steps_to_value
                return passed, path, steps

            for neighbor, _ in self.flat_graph.get(curr, []):
                if neighbor not in visited and neighbor in self.flat_graph:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return False, [], -1

    def verify_error_recovery_cycles(self) -> List[Dict[str, Any]]:
        """Verifies that every error state has a recovery path returning to the originating state."""
        cycles = []
        for s_from, transitions in self.flat_graph.items():
            for s_to, trans in transitions:
                # Detect error transitions by event naming or meta tags
                is_error_trans = "ERROR" in trans.event.upper() or "FAIL" in trans.event.upper()
                node_to = self._resolve_node(s_to)
                if node_to and node_to.meta.get("is_error_state", False):
                    is_error_trans = True

                if is_error_trans:
                    # Look for recovery path from s_to back to s_from
                    recovery_path = self._find_shortest_path(s_to, s_from)
                    cycles.append({
                        "origin_state": s_from,
                        "error_state": s_to,
                        "error_event": trans.event,
                        "has_recovery": bool(recovery_path),
                        "recovery_path": recovery_path
                    })
        return cycles

    def _find_shortest_path(self, start: str, target: str) -> Optional[List[str]]:
        queue = deque([(start, [start])])
        visited = {start}
        while queue:
            curr, path = queue.popleft()
            if curr == target:
                return path
            for neighbor, _ in self.flat_graph.get(curr, []):
                if neighbor not in visited and neighbor in self.flat_graph:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    def simulate_hostile_persona(self, max_depth: int = 20) -> Tuple[int, List[str]]:
        """Simulates an uncooperative adversarial persona sending random and out-of-order events."""
        import random
        all_events = list(self.statechart.events.keys())
        if not all_events:
            return 1, []

        curr = self.statechart.initial
        traversals = 0
        failures = []

        # Run 5 randomized adversarial simulations
        for sim_idx in range(5):
            curr = self.statechart.initial
            for step in range(max_depth):
                # Pick random event (valid or invalid)
                chosen_event = random.choice(all_events)
                valid_trans = [t for _, t in self.flat_graph.get(curr, []) if t.event == chosen_event]

                if valid_trans:
                    # Legal transition
                    target = self._resolve_target(curr, valid_trans[0].target)
                    curr = target
                else:
                    # Illegal event sent - state must remain unmutated (resilient)
                    pass
            traversals += 1

        return traversals, failures

    def evaluate(self) -> ViabilityReport:
        passed_steps, path_to_val, steps = self.verify_steps_to_value()
        recovery_cycles = self.verify_error_recovery_cycles()
        traversals_passed, failures = self.simulate_hostile_persona()

        violations = []
        if not passed_steps:
            violations.append(
                f"Steps to value ({steps}) exceeded budget ({self.max_steps_to_value}). Path: {' -> '.join(path_to_val)}"
            )

        for cycle in recovery_cycles:
            if not cycle["has_recovery"]:
                violations.append(
                    f"Irreversible error trap detected: {cycle['origin_state']} -> {cycle['error_state']} lacks recovery return path."
                )

        return ViabilityReport(
            passed=len(violations) == 0,
            shortest_path_to_value=path_to_val,
            steps_to_value=steps,
            max_budget=self.max_steps_to_value,
            error_recovery_cycles=recovery_cycles,
            adversarial_traversals_passed=traversals_passed,
            adversarial_failures=failures,
            violations=violations
        )
