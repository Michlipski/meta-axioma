"""Statechart Intermediate Representation (Statechart IR) conforming to XState v5.

Grounded in [L1-002] (Functorial State Evolution) and [L1-015] (Deterministic Automata Boundaries).
Models all user, system, and operational journeys as formal, edge-connected statecharts.
"""

from dataclasses import dataclass, field
import json
from typing import Any, Dict, List, Optional


@dataclass
class Transition:
    target: str
    event: str
    guard: Optional[str] = None
    actions: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"target": self.target}
        if self.guard:
            data["guard"] = self.guard
        if self.actions:
            data["actions"] = self.actions
        if self.description:
            data["description"] = self.description
        return data


@dataclass
class StateNode:
    id: str
    description: str = ""
    initial: Optional[str] = None
    states: Dict[str, "StateNode"] = field(default_factory=dict)
    on: Dict[str, Transition] = field(default_factory=dict)
    entry: List[str] = field(default_factory=list)
    exit: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)  # e.g. {"is_value_state": True, "is_error_state": False}

    def is_compound(self) -> bool:
        return bool(self.states)

    def to_xstate_v5(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "id": self.id,
            "description": self.description,
        }
        if self.initial:
            result["initial"] = self.initial
        if self.meta:
            result["meta"] = self.meta
        if self.entry:
            result["entry"] = self.entry
        if self.exit:
            result["exit"] = self.exit

        if self.on:
            result["on"] = {evt: trans.to_dict() for evt, trans in self.on.items()}

        if self.states:
            result["states"] = {s_name: node.to_xstate_v5() for s_name, node in self.states.items()}

        return result


@dataclass
class EventSpec:
    name: str
    payload_fields: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class StatechartIR:
    machine_id: str
    initial: str
    states: Dict[str, StateNode] = field(default_factory=dict)
    context_schema: Dict[str, Any] = field(default_factory=dict)
    events: Dict[str, EventSpec] = field(default_factory=dict)
    description: str = ""

    def to_xstate_v5_json(self, indent: int = 2) -> str:
        """Serializes machine to standard XState v5 JSON."""
        root = {
            "id": self.machine_id,
            "initial": self.initial,
            "context": self.context_schema,
            "description": self.description,
            "states": {s_name: node.to_xstate_v5() for s_name, node in self.states.items()}
        }
        return json.dumps(root, indent=indent)

    def get_all_state_paths(self, prefix: str = "", current_states: Optional[Dict[str, StateNode]] = None) -> List[str]:
        """Flattens hierarchical states into full dot-notation paths."""
        if current_states is None:
            current_states = self.states
        paths: List[str] = []
        for name, node in current_states.items():
            full_path = f"{prefix}.{name}" if prefix else name
            paths.append(full_path)
            if node.states:
                paths.extend(self.get_all_state_paths(prefix=full_path, current_states=node.states))
        return paths

    def get_all_transitions(self) -> List[Transition]:
        """Collects all defined transitions in the statechart."""
        transitions: List[Transition] = []
        def _collect(nodes: Dict[str, StateNode]):
            for node in nodes.values():
                transitions.extend(node.on.values())
                if node.states:
                    _collect(node.states)
        _collect(self.states)
        return transitions

    def to_dict(self) -> Dict[str, Any]:
        """Serializes machine to python dictionary."""
        return {
            "id": self.machine_id,
            "initial": self.initial,
            "context": self.context_schema,
            "description": self.description,
            "states": {s_name: node.to_xstate_v5() for s_name, node in self.states.items()}
        }

    def collect_all_state_ids(self) -> List[str]:
        """Collects all flat and dot-notation state IDs."""
        return self.get_all_state_paths()
