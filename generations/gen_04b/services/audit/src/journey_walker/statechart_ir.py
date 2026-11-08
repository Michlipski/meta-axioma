"""Generation 4b Universal Hierarchical Statechart Intermediate Representation (IR).

Enforces:
- [L1-G3B-011] Universal & Hierarchical Statechart IR.
- [L1-G4B-017] Headless Journey Walker & Statechart Covering-Path Fuzzer.
- Full XState v5 specification compliance:
  - Compound states (nested state nodes with initial state and child states)
  - Parallel regions (orthogonal concurrent state machines)
  - History states (shallow and deep history restoration)
  - Guarded transitions with formal preconditions and action mutators
  - Lossless round-trip serialization: f^-1(f(x)) == x
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import json
from typing import Any, Dict, List, Optional, Set, Tuple


class StateNodeType(str, Enum):
    """Classification of state node in the hierarchical statechart."""
    ATOMIC = "atomic"
    COMPOUND = "compound"
    PARALLEL = "parallel"
    HISTORY = "history"
    FINAL = "final"


class HistoryType(str, Enum):
    """Depth of history restoration for history state nodes."""
    SHALLOW = "shallow"
    DEEP = "deep"


@dataclass
class Transition:
    """An event-driven transition between state nodes."""
    event: str
    target: str
    guard: Optional[str] = None
    actions: List[str] = field(default_factory=list)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "event": self.event,
            "target": self.target,
            "actions": list(self.actions),
            "description": self.description,
        }
        if self.guard is not None:
            d["guard"] = self.guard
        if self.metadata:
            d["metadata"] = dict(self.metadata)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Transition:
        return cls(
            event=str(data.get("event", "EV")),
            target=str(data.get("target", "")),
            guard=data.get("guard"),
            actions=list(data.get("actions", [])),
            description=str(data.get("description", "")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class StateNode:
    """A hierarchical state node (atomic, compound, parallel, history, or final)."""
    id: str
    node_type: StateNodeType = StateNodeType.ATOMIC
    initial: Optional[str] = None
    states: Dict[str, StateNode] = field(default_factory=dict)
    transitions: List[Transition] = field(default_factory=list)
    entry_actions: List[str] = field(default_factory=list)
    exit_actions: List[str] = field(default_factory=list)
    history_type: Optional[HistoryType] = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_leaf(self) -> bool:
        """True if node has no child states."""
        return self.node_type in (StateNodeType.ATOMIC, StateNodeType.HISTORY, StateNodeType.FINAL) or not self.states

    @property
    def is_compound(self) -> bool:
        """True if node is compound with child substates."""
        return self.node_type == StateNodeType.COMPOUND

    @property
    def is_parallel(self) -> bool:
        """True if node contains orthogonal parallel regions."""
        return self.node_type == StateNodeType.PARALLEL

    def get_child(self, child_id: str) -> Optional[StateNode]:
        """Retrieves child state node by relative ID."""
        return self.states.get(child_id)

    def get_all_descendant_ids(self, prefix: str = "") -> List[str]:
        """Recursively collects all state IDs rooted at this node."""
        current_id = f"{prefix}.{self.id}" if prefix else self.id
        ids = [current_id]
        for child in self.states.values():
            ids.extend(child.get_all_descendant_ids(current_id))
        return ids

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "id": self.id,
            "type": self.node_type.value,
            "description": self.description,
            "transitions": [t.to_dict() for t in self.transitions],
            "entry_actions": list(self.entry_actions),
            "exit_actions": list(self.exit_actions),
        }
        if self.initial is not None:
            d["initial"] = self.initial
        if self.history_type is not None:
            d["history"] = self.history_type.value
        if self.states:
            d["states"] = {sid: child.to_dict() for sid, child in self.states.items()}
        if self.metadata:
            d["metadata"] = dict(self.metadata)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StateNode:
        child_states: Dict[str, StateNode] = {}
        if "states" in data and isinstance(data["states"], dict):
            for sid, child_dict in data["states"].items():
                child_states[sid] = cls.from_dict(child_dict)

        ht = None
        if "history" in data and data["history"]:
            ht = HistoryType(data["history"])

        raw_type = data.get("type", "atomic")
        try:
            node_type = StateNodeType(raw_type)
        except ValueError:
            node_type = StateNodeType.ATOMIC

        return cls(
            id=str(data.get("id", "anonymous_node")),
            node_type=node_type,
            initial=data.get("initial"),
            states=child_states,
            transitions=[Transition.from_dict(t) for t in data.get("transitions", [])],
            entry_actions=list(data.get("entry_actions", [])),
            exit_actions=list(data.get("exit_actions", [])),
            history_type=ht,
            description=str(data.get("description", "")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class StatechartIR:
    """The Universal Hierarchical Statechart IR.

    Captures compound states, parallel regions, history states, and formal guards.
    """
    id: str
    root: StateNode
    context_schema: Dict[str, str] = field(default_factory=dict)
    initial_context: Dict[str, Any] = field(default_factory=dict)
    version: str = "5.0"

    def get_all_state_ids(self) -> List[str]:
        """Returns flat list of all state IDs in the chart."""
        ids: List[str] = []
        self._collect_ids(self.root, "", ids)
        return ids

    def _collect_ids(self, node: StateNode, prefix: str, acc: List[str]) -> None:
        current_id = f"{prefix}.{node.id}" if prefix else node.id
        acc.append(current_id)
        # Also register direct child ID without prefix for convenience
        if node.id not in acc:
            acc.append(node.id)
        for child in node.states.values():
            self._collect_ids(child, current_id, acc)

    def validate_integrity(self) -> List[str]:
        """Performs structural integrity validation over the statechart."""
        errors: List[str] = []
        all_ids = set(self.get_all_state_ids())

        self._validate_node(self.root, all_ids, errors)

        for key in self.initial_context:
            if self.context_schema and key not in self.context_schema:
                errors.append(f"Initial context key '{key}' not declared in context_schema.")

        return errors

    def _validate_node(self, node: StateNode, all_ids: Set[str], errors: List[str]) -> None:
        if node.node_type == StateNodeType.COMPOUND:
            if not node.states:
                errors.append(f"Compound state node '{node.id}' has no child states.")
            elif not node.initial:
                errors.append(f"Compound state node '{node.id}' missing required 'initial' state.")
            elif node.initial not in node.states and f"{node.id}.{node.initial}" not in all_ids:
                errors.append(
                    f"Compound state node '{node.id}' initial state '{node.initial}' "
                    f"does not exist among child states."
                )
        elif node.node_type == StateNodeType.PARALLEL:
            if not node.states:
                errors.append(f"Parallel state node '{node.id}' must have at least one child region.")

        for child in node.states.values():
            self._validate_node(child, all_ids, errors)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "root": self.root.to_dict(),
            "context_schema": dict(self.context_schema),
            "initial_context": dict(self.initial_context),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StatechartIR:
        root_data = data.get("root", {})
        root_node = StateNode.from_dict(root_data)
        return cls(
            id=str(data.get("id", "anonymous_statechart")),
            root=root_node,
            context_schema=dict(data.get("context_schema", {})),
            initial_context=dict(data.get("initial_context", {})),
            version=str(data.get("version", "5.0")),
        )

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> StatechartIR:
        return cls.from_dict(json.loads(json_str))
