"""Contract Intermediate Representation (Contract IR) for System G1b.

Grounded in [L1-015] (Zero-Trust Dual-Boundary Demarcation: Typed Nouns + Deterministic Verbs).
Binds data shapes (Nouns) and state transitions (Verbs) to explicit, introspectable interfaces.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from g1b_compiler.ir.semantic_ir import EntitySpec, FieldType


@dataclass
class NounContract:
    """Typed data boundary contract (e.g. GraphQL/Zod/TypeScript interface)."""
    entity_name: str
    fields: Dict[str, str]  # field_name -> type_string
    required_fields: List[str]
    description: str = ""

    def to_typescript_interface(self) -> str:
        lines = [f"export interface {self.entity_name} {{"]
        for fname, ftype in self.fields.items():
            optional = "" if fname in self.required_fields else "?"
            lines.append(f"  {fname}{optional}: {ftype};")
        lines.append("}")
        return "\n".join(lines)


@dataclass
class VerbContract:
    """Temporal action / mutation boundary contract (FSM handler signature)."""
    action_name: str
    from_state: str
    to_state: str
    event_payload_type: str
    description: str
    has_side_effect: bool = False
    enclave_required: bool = False  # Grounded in [L1-016] Demarcated Exception Enclaves

    def to_typescript_signature(self) -> str:
        return f"export type {self.action_name}Handler = (context: AppContext, event: {self.event_payload_type}) => Promise<AppContext>;"


@dataclass
class DualBoundaryContractIR:
    app_id: str
    nouns: Dict[str, NounContract] = field(default_factory=dict)
    verbs: Dict[str, VerbContract] = field(default_factory=dict)
    api_routes: List[Dict[str, Any]] = field(default_factory=list)
    version: str = "1.0.0"

    def get_noun(self, name: str) -> Optional[NounContract]:
        return self.nouns.get(name)

    def get_verb(self, name: str) -> Optional[VerbContract]:
        return self.verbs.get(name)
