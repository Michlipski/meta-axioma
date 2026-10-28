"""Generation 3b Formal Model Checker (The Brain - Gemini 4 Argon).

Performs exhaustive formal verification over Hierarchical Statechart IR:
1. Reachability analysis: Traverses compound, parallel, and atomic nodes from root.initial. Traps orphaned/unreachable states.
2. Dead-end discovery: Flags non-final leaf states that lack outgoing transitions (deadlocks).
3. Dangling target detection: Identifies transitions pointing to non-existent state nodes.
4. Parallel region conflict analysis: Detects race conditions or conflicting transitions in concurrent orthogonal regions.
5. Emits formal ModelCheckingReport and raises ModelCheckingFailure on any defect.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Any, List, Set, Optional

from ..ir.statechart_ir import (
    StatechartIR,
    StateNode,
    StateNodeType,
    Transition,
)
from ..routing.router import DualModelRouter, CognitiveRole, ModelTier


class ModelCheckingFailure(Exception):
    """Raised when formal model checking detects an unrecoverable statechart defect."""
    pass


@dataclass
class ModelCheckingReport:
    """Formal verification report certifying or rejecting a Statechart IR."""
    statechart_id: str
    is_certified: bool
    total_states_analyzed: int
    evaluating_model: str = ModelTier.BRAIN_ARGON.value
    reachable_states: List[str] = field(default_factory=list)
    unreachable_states: List[str] = field(default_factory=list)
    dead_end_states: List[str] = field(default_factory=list)
    dangling_transitions: List[Dict[str, str]] = field(default_factory=list)
    parallel_conflicts: List[str] = field(default_factory=list)
    defect_summary: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statechart_id": self.statechart_id,
            "is_certified": self.is_certified,
            "total_states_analyzed": self.total_states_analyzed,
            "evaluating_model": self.evaluating_model,
            "reachable_states": self.reachable_states,
            "unreachable_states": self.unreachable_states,
            "dead_end_states": self.dead_end_states,
            "dangling_transitions": self.dangling_transitions,
            "parallel_conflicts": self.parallel_conflicts,
            "defect_summary": self.defect_summary,
        }


class FormalModelChecker:
    """Adversarial zero-trust statechart model checker."""

    @classmethod
    def check(cls, chart: StatechartIR) -> ModelCheckingReport:
        """Executes full formal statechart model check under Gemini 4 Argon governance."""
        # Enforce [L1-G3B-014] Cognitive Routing
        invocation = DualModelRouter.create_invocation(
            task_id=f"model_check:{chart.id}",
            role=CognitiveRole.MODEL_CHECKER,
            payload={"statechart_id": chart.id},
            requested_model=ModelTier.BRAIN_ARGON,
        )

        all_ids = set(chart.get_all_state_ids())
        total_states = len(all_ids)

        defects: List[str] = []
        dangling: List[Dict[str, str]] = []

        # 1. First-pass IR structural integrity check
        ir_errors = chart.validate_integrity()
        for err in ir_errors:
            defects.append(f"Structural Integrity: {err}")

        # 2. Graph reachability traversal
        # Identify start state: root.initial
        initial_id = chart.root.initial
        if not initial_id:
            defects.append(f"Root state node '{chart.root.id}' has no initial substate.")
            return ModelCheckingReport(
                statechart_id=chart.id,
                is_certified=False,
                total_states_analyzed=total_states,
                defect_summary=defects,
            )

        # Resolve initial node ID
        start_node_id = f"{chart.root.id}.{initial_id}" if initial_id in chart.root.states else initial_id
        if start_node_id not in all_ids:
            # check direct child key
            if chart.root.id in all_ids:
                start_node_id = initial_id

        reachable: Set[str] = set()
        queue: deque = deque()

        # Seed traversal with root and its initial state
        reachable.add(chart.root.id)
        if start_node_id in all_ids:
            queue.append(start_node_id)
            reachable.add(start_node_id)
        elif initial_id in chart.root.states:
            resolved_child_id = chart.root.states[initial_id].id
            queue.append(resolved_child_id)
            reachable.add(resolved_child_id)

        # Breadth-first search along transitions and compound parent/child hierarchies
        while queue:
            curr_id = queue.popleft()
            node = chart.find_node(curr_id)
            if not node:
                continue

            # If compound, its initial child state is automatically reachable
            if node.node_type == StateNodeType.COMPOUND and node.initial:
                child_init = None
                if node.initial in node.states:
                    child_init = node.states[node.initial].id
                elif f"{node.id}.{node.initial}" in all_ids:
                    child_init = f"{node.id}.{node.initial}"
                elif node.initial in all_ids:
                    child_init = node.initial

                if child_init and child_init not in reachable:
                    reachable.add(child_init)
                    queue.append(child_init)

            # If parallel, all regions are concurrently entered and reachable
            elif node.node_type == StateNodeType.PARALLEL:
                for region_key, region_node in node.states.items():
                    if region_node.id not in reachable:
                        reachable.add(region_node.id)
                        queue.append(region_node.id)

            # Follow outgoing transitions
            for t in node.transitions:
                target = t.target
                resolved_target = None
                if target in all_ids:
                    resolved_target = target
                elif f"{node.id}.{target}" in all_ids:
                    resolved_target = f"{node.id}.{target}"

                if resolved_target:
                    if resolved_target not in reachable:
                        reachable.add(resolved_target)
                        queue.append(resolved_target)
                else:
                    dangling.append({"source": node.id, "event": t.event, "target": t.target})
                    defects.append(f"Dangling Transition: '{node.id}' --[{t.event}]--> '{t.target}' (non-existent)")

        # Also add parent compound/parallel containers if their children are reachable
        for sid in list(reachable):
            # check parent hierarchy
            parts = sid.split(".")
            for i in range(1, len(parts)):
                prefix = ".".join(parts[:i])
                if prefix in all_ids:
                    reachable.add(prefix)

        unreachable = sorted(list(all_ids - reachable))
        for u in unreachable:
            defects.append(f"Unreachable State Trap: State '{u}' cannot be reached from root initial state.")

        # 3. Dead-end discovery
        # A non-final state with no outgoing transitions and no child transitions is a dead-end
        dead_ends: List[str] = []
        for sid in reachable:
            node = chart.find_node(sid)
            if not node:
                continue
            if node.node_type in (StateNodeType.FINAL, StateNodeType.HISTORY):
                continue

            has_outgoing = len(node.transitions) > 0
            has_child_states = len(node.states) > 0

            # If it's a leaf node (no child states) and has no outgoing transitions, it's a dead-end trap
            if not has_child_states and not has_outgoing:
                dead_ends.append(node.id)
                defects.append(f"Dead-End Trap: State '{node.id}' has type '{node.node_type.value}' but zero outbound transitions and is not marked 'final'.")

        # 4. Parallel Region Conflict Analysis
        # Check if parallel regions trigger conflicting events or state collisions
        def _get_subtree_transitions(sub_node: StateNode) -> List[Transition]:
            collected = list(sub_node.transitions)
            for ch in sub_node.states.values():
                collected.extend(_get_subtree_transitions(ch))
            return collected

        parallel_conflicts: List[str] = []
        for sid in all_ids:
            node = chart.find_node(sid)
            if node and node.node_type == StateNodeType.PARALLEL:
                event_map: Dict[str, List[str]] = {}
                for r_name, r_node in node.states.items():
                    for t in _get_subtree_transitions(r_node):
                        event_map.setdefault(t.event, []).append(f"{r_name}:{t.target}")
                for evt, targets in event_map.items():
                    if len(targets) > 1:
                        conflict_desc = f"Parallel Region Conflict in '{node.id}': Event '{evt}' triggers concurrent uncoordinated transitions: {targets}"
                        parallel_conflicts.append(conflict_desc)
                        defects.append(conflict_desc)

        is_certified = len(defects) == 0

        return ModelCheckingReport(
            statechart_id=chart.id,
            is_certified=is_certified,
            total_states_analyzed=total_states,
            reachable_states=sorted(list(reachable)),
            unreachable_states=unreachable,
            dead_end_states=dead_ends,
            dangling_transitions=dangling,
            parallel_conflicts=parallel_conflicts,
            defect_summary=defects,
        )

    @classmethod
    def assert_certified(cls, chart: StatechartIR) -> ModelCheckingReport:
        """Runs check and immediately raises ModelCheckingFailure on any violation."""
        report = cls.check(chart)
        if not report.is_certified:
            raise ModelCheckingFailure(
                f"Model checking failed for '{chart.id}' with {len(report.defect_summary)} defects:\n" +
                "\n".join(f"  - {d}" for d in report.defect_summary)
            )
        return report
