"""Generation 3b Universal & Hierarchical Statechart Intermediate Representation (IR).

Natively supports XState v5 hierarchical statechart semantics:
- Compound states (nested state nodes with initial state and child states)
- Parallel regions (orthogonal concurrent state machines)
- History states (shallow and deep history restoration)
- Event-driven transitions with formal guards, actions, and targets
- Context schema definition and typing
- Formal validation and lossless round-trip serialization: f^-1(f(x)) == x
"""

from dataclasses import dataclass, field
from enum import Enum
import json
from typing import List, Dict, Any, Optional, Set


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

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "event": self.event,
            "target": self.target,
            "actions": list(self.actions),
            "description": self.description,
        }
        if self.guard is not None:
            d["guard"] = self.guard
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transition":
        return cls(
            event=data["event"],
            target=data["target"],
            guard=data.get("guard"),
            actions=data.get("actions", []),
            description=data.get("description", ""),
        )


@dataclass
class StateNode:
    """A hierarchical state node (atomic, compound, parallel, history, or final)."""
    id: str
    node_type: StateNodeType = StateNodeType.ATOMIC
    initial: Optional[str] = None
    states: Dict[str, "StateNode"] = field(default_factory=dict)
    transitions: List[Transition] = field(default_factory=list)
    entry_actions: List[str] = field(default_factory=list)
    exit_actions: List[str] = field(default_factory=list)
    history_type: Optional[HistoryType] = None
    description: str = ""

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
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateNode":
        child_states: Dict[str, StateNode] = {}
        if "states" in data and isinstance(data["states"], dict):
            for sid, child_dict in data["states"].items():
                child_states[sid] = cls.from_dict(child_dict)

        ht = None
        if "history" in data and data["history"]:
            ht = HistoryType(data["history"])

        return cls(
            id=data["id"],
            node_type=StateNodeType(data.get("type", "atomic")),
            initial=data.get("initial"),
            states=child_states,
            transitions=[Transition.from_dict(t) for t in data.get("transitions", [])],
            entry_actions=data.get("entry_actions", []),
            exit_actions=data.get("exit_actions", []),
            history_type=ht,
            description=data.get("description", ""),
        )


@dataclass
class StatechartIR:
    """The Universal Hierarchical Statechart IR.

    Mathematically captures compound states, parallel regions, history states,
    and formal guards for any software application or system, including compilers.
    """
    id: str
    root: StateNode
    context_schema: Dict[str, str] = field(default_factory=dict)
    initial_context: Dict[str, Any] = field(default_factory=dict)
    version: str = "5.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "root": self.root.to_dict(),
            "context_schema": self.context_schema,
            "initial_context": self.initial_context,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatechartIR":
        return cls(
            id=data["id"],
            root=StateNode.from_dict(data["root"]),
            context_schema=data.get("context_schema", {}),
            initial_context=data.get("initial_context", {}),
            version=data.get("version", "5.0"),
        )

    def to_json(self, indent: int = 2) -> str:
        """Serializes Statechart IR to formatted JSON."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    @classmethod
    def from_json(cls, json_str: str) -> "StatechartIR":
        """Deserializes Statechart IR from JSON."""
        return cls.from_dict(json.loads(json_str))

    def find_node(self, node_id: str) -> Optional[StateNode]:
        """Recursively finds a state node by its ID."""
        return self._search_node(self.root, node_id)

    def _search_node(self, current: StateNode, target_id: str) -> Optional[StateNode]:
        if current.id == target_id:
            return current
        for child in current.states.values():
            found = self._search_node(child, target_id)
            if found:
                return found
        return None

    def get_all_state_ids(self) -> List[str]:
        """Returns all state node IDs in the hierarchy."""
        ids: List[str] = []
        self._collect_ids(self.root, ids)
        return ids

    def _collect_ids(self, current: StateNode, accumulator: List[str]):
        accumulator.append(current.id)
        for child in current.states.values():
            self._collect_ids(child, accumulator)

    def get_leaf_states(self) -> List[str]:
        """Returns all leaf (atomic, history, or final) state node IDs."""
        leaves: List[str] = []
        self._collect_leaves(self.root, leaves)
        return leaves

    def _collect_leaves(self, current: StateNode, accumulator: List[str]):
        if not current.states:
            accumulator.append(current.id)
        else:
            for child in current.states.values():
                self._collect_leaves(child, accumulator)

    def validate_integrity(self) -> List[str]:
        """Validates formal statechart integrity:

        1. Root must be defined.
        2. Compound nodes must have a valid initial substate.
        3. Parallel nodes must have at least one region.
        4. All transition targets must resolve to existing state node IDs.
        5. Initial context must conform to context_schema keys.
        """
        errors: List[str] = []
        all_ids = set(self.get_all_state_ids())

        self._validate_node(self.root, all_ids, errors)

        # Context key check
        for key in self.initial_context:
            if key not in self.context_schema:
                errors.append(f"Initial context key '{key}' not declared in context_schema.")

        return errors

    def _validate_node(self, node: StateNode, all_ids: Set[str], errors: List[str]):
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

        # Check transitions
        for t in node.transitions:
            if t.target not in all_ids:
                # Also allow relative dot target e.g. "child" inside parent
                resolved_relative = f"{node.id}.{t.target}"
                if resolved_relative not in all_ids:
                    errors.append(
                        f"Transition on event '{t.event}' in node '{node.id}' "
                        f"targets non-existent state '{t.target}'."
                    )

        for child in node.states.values():
            self._validate_node(child, all_ids, errors)
