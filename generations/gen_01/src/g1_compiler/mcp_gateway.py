"""Zero-Trust Dual-Boundary Demarcation & Introspectable MCP Governance ([L1-015]).

Formal Expression:
    M(s, a) ∈ G_nouns × A_verbs  ∧  SandboxVerify(a) = 0 ⟹ Admissible(a)

Operational Rule:
    Subsystems attempting imperative state mutation without typed schema
    introspection (Nouns) or bypassing deterministic state machine guard
    transitions (Verbs) are rejected at compile time.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set
import copy


@dataclass
class NounField:
    """Formal type constraint on a data boundary property."""
    field_name: str
    expected_type: type
    required: bool = True
    validator: Optional[Callable[[Any], bool]] = None


@dataclass
class NounSchema:
    """Data Boundary (Noun): Formally typed schema constraining all inter-subsystem payloads."""
    schema_name: str
    fields: Dict[str, NounField] = field(default_factory=dict)

    def validate(self, payload: Dict[str, Any]) -> bool:
        """Validates payload against schema constraints."""
        for field_name, constraint in self.fields.items():
            if field_name not in payload:
                if constraint.required:
                    raise ValueError(f"Noun Schema Violation: Missing required field '{field_name}' in '{self.schema_name}'")
                continue
            val = payload[field_name]
            if not isinstance(val, constraint.expected_type):
                raise TypeError(
                    f"Noun Schema Violation: Field '{field_name}' expects {constraint.expected_type.__name__}, "
                    f"got {type(val).__name__} in '{self.schema_name}'"
                )
            if constraint.validator and not constraint.validator(val):
                raise ValueError(f"Noun Schema Violation: Custom constraint failed on '{field_name}' in '{self.schema_name}'")
        return True

    def introspect(self) -> Dict[str, Any]:
        """Returns JSON-schema-compatible introspectable representation."""
        return {
            "name": self.schema_name,
            "fields": {
                k: {
                    "type": v.expected_type.__name__,
                    "required": v.required,
                }
                for k, v in self.fields.items()
            },
        }


@dataclass
class VerbTransition:
    """Temporal Boundary (Verb): Legal state machine transition guard."""
    from_state: str
    action_name: str
    to_state: str
    guard: Optional[Callable[[Dict[str, Any]], bool]] = None


class VerbStateAutomaton:
    """Temporal Boundary: Deterministic Finite State Automaton regulating allowed actions."""

    def __init__(self, initial_state: str):
        self.current_state = initial_state
        self.transitions: Dict[str, List[VerbTransition]] = {}
        self.history: List[str] = [initial_state]

    def register_transition(self, transition: VerbTransition) -> None:
        """Registers an allowable deterministic transition."""
        key = f"{transition.from_state}:{transition.action_name}"
        if key not in self.transitions:
            self.transitions[key] = []
        self.transitions[key].append(transition)

    def can_transition(self, action_name: str, payload: Dict[str, Any]) -> bool:
        """Checks if an action is valid from current state and satisfies guards."""
        key = f"{self.current_state}:{action_name}"
        valid_transitions = self.transitions.get(key, [])
        for t in valid_transitions:
            if t.guard is None or t.guard(payload):
                return True
        return False

    def trigger(self, action_name: str, payload: Dict[str, Any]) -> str:
        """Executes the state transition or raises an invariant violation."""
        key = f"{self.current_state}:{action_name}"
        valid_transitions = self.transitions.get(key, [])
        for t in valid_transitions:
            if t.guard is None or t.guard(payload):
                self.current_state = t.to_state
                self.history.append(t.to_state)
                return self.current_state

        raise PermissionError(
            f"Verb Boundary Violation [L1-015]: Action '{action_name}' is inadmissible from state '{self.current_state}'."
        )


@dataclass
class McpTool:
    """Introspectable tool exposed across the zero-trust MCP boundary."""
    name: str
    description: str
    input_schema: NounSchema
    action_verb: str
    handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    sandbox_verifier: Optional[Callable[[Dict[str, Any]], int]] = None

    def introspect(self) -> Dict[str, Any]:
        """Provides machine-readable schema for discovery by agents and clients."""
        return {
            "name": self.name,
            "description": self.description,
            "action_verb": self.action_verb,
            "parameters": self.input_schema.introspect(),
        }


class McpGateway:
    """Introspectable Model Context Protocol Gateway enforcing Dual-Boundary Governance."""

    def __init__(self, automaton: VerbStateAutomaton):
        self.automaton = automaton
        self.tools: Dict[str, McpTool] = {}
        self.execution_audit_log: List[Dict[str, Any]] = []

    def register_tool(self, tool: McpTool) -> None:
        """Registers a capability with dual-boundary schema."""
        self.tools[tool.name] = tool

    def list_tools(self) -> List[Dict[str, Any]]:
        """Introspects all registered tools and their schema boundaries."""
        return [t.introspect() for t in self.tools.values()]

    def execute_tool(self, tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a tool with strict Noun schema, Verb FSM, and Sandbox verification."""
        if tool_name not in self.tools:
            raise KeyError(f"MCP Gateway: Tool '{tool_name}' not registered.")

        tool = self.tools[tool_name]

        # 1. Noun Boundary (Data Schema Validation)
        tool.input_schema.validate(payload)

        # 2. Ephemeral Sandbox Pre-flight Verification: SandboxVerify(a) == 0
        if tool.sandbox_verifier is not None:
            sandbox_exit_code = tool.sandbox_verifier(payload)
            if sandbox_exit_code != 0:
                raise RuntimeError(
                    f"Zero-Trust Sandbox Verification Failed: Tool '{tool_name}' returned code {sandbox_exit_code}."
                )

        # 3. Verb Boundary (State Automaton Transition)
        previous_state = self.automaton.current_state
        new_state = self.automaton.trigger(tool.action_verb, payload)

        # 4. Safe Execution
        result = tool.handler(payload)

        self.execution_audit_log.append({
            "tool": tool_name,
            "verb": tool.action_verb,
            "from_state": previous_state,
            "to_state": new_state,
            "payload_summary": list(payload.keys()),
        })

        return result
