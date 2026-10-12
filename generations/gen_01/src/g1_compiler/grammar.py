"""Universal Grammar & Compositional Projection Constraints ([L1-004]).

Formal Expression:
    P_surface(D_deep) ≡ D_deep (mod Transform)

Every inter-module payload and compiler artifact must conform to an invariant
deep syntactic structure whose transformational projections into target
representations preserve semantic well-formedness.
"""

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Dict, List, Optional, Set


@dataclass
class DeepSyntaxNode:
    """Invariant deep syntactic structure AST node."""
    node_type: str
    identifier: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List["DeepSyntaxNode"] = field(default_factory=list)
    semantic_role: str = "COMPUTATIONAL_UNIT"

    def compute_deep_digest(self) -> str:
        """Computes a deterministic cryptographic digest of the invariant deep structure."""
        child_digests = [c.compute_deep_digest() for c in self.children]
        content = {
            "type": self.node_type,
            "id": self.identifier,
            "attributes": {k: str(v) for k, v in sorted(self.attributes.items())},
            "children": child_digests,
            "role": self.semantic_role,
        }
        serialized = json.dumps(content, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Recursive dictionary serialization."""
        return {
            "node_type": self.node_type,
            "identifier": self.identifier,
            "attributes": dict(self.attributes),
            "children": [c.to_dict() for c in self.children],
            "semantic_role": self.semantic_role,
            "deep_digest": self.compute_deep_digest(),
        }


class UniversalGrammar:
    """Enforces deep syntactic well-formedness and projects to target surface representations."""

    VALID_NODE_TYPES: Set[str] = {
        "COMPILER_MODULE",
        "STATE_MACHINE",
        "INVARIANT_SPEC",
        "MCP_GATEWAY",
        "EXCEPTION_ENCLAVE",
        "STORAGE_ADAPTER",
        "THERMODYNAMIC_KERNEL",
        "SUCCESSOR_BASIS",
    }

    @classmethod
    def validate_deep_syntax(cls, node: DeepSyntaxNode) -> bool:
        """Verifies that an AST node conforms to universal grammar constraints."""
        if node.node_type not in cls.VALID_NODE_TYPES:
            raise ValueError(f"Universal Grammar Violation: Invalid node_type '{node.node_type}'")
        if not node.identifier:
            raise ValueError("Universal Grammar Violation: Empty node identifier")

        # Recursively validate all child nodes
        for child in node.children:
            cls.validate_deep_syntax(child)
        return True

    @classmethod
    def project_to_ir(cls, node: DeepSyntaxNode) -> Dict[str, Any]:
        """Surface projection P_surface: Maps deep AST to compiler Intermediate Representation."""
        cls.validate_deep_syntax(node)
        return {
            "ir_version": "1.0",
            "entity": node.identifier,
            "kind": node.node_type,
            "params": node.attributes,
            "subcomponents": [cls.project_to_ir(c) for c in node.children],
            "digest": node.compute_deep_digest(),
        }

    @classmethod
    def project_to_trace_spec(cls, node: DeepSyntaxNode) -> str:
        """Surface projection P_surface: Maps deep AST to TRACE declarative documentation markdown."""
        cls.validate_deep_syntax(node)
        lines = [
            f"# TRACE Specification: {node.identifier}",
            f"- **Kind:** `{node.node_type}`",
            f"- **Semantic Role:** `{node.semantic_role}`",
            f"- **Digest:** `{node.compute_deep_digest()[:16]}...`",
            "",
            "## Attributes",
        ]
        for k, v in sorted(node.attributes.items()):
            lines.append(f"- **{k}:** `{v}`")

        if node.children:
            lines.append("")
            lines.append("## Subcomponents")
            for c in node.children:
                lines.append(f"- `{c.identifier}` (`{c.node_type}`)")

        return "\n".join(lines)

    @classmethod
    def project_to_schema(cls, node: DeepSyntaxNode) -> Dict[str, Any]:
        """Surface projection P_surface: Maps deep AST to typed GraphQL/JSON schema definitions."""
        cls.validate_deep_syntax(node)
        properties = {}
        for k, v in node.attributes.items():
            py_type = type(v).__name__
            schema_type = "String" if py_type == "str" else ("Int" if py_type == "int" else "Boolean")
            properties[k] = {"type": schema_type, "example": str(v)}

        return {
            "type_name": node.identifier,
            "category": node.node_type,
            "fields": properties,
            "children_types": [c.identifier for c in node.children],
        }

    @classmethod
    def verify_projection_fidelity(cls, deep_node: DeepSyntaxNode, surface_ir: Dict[str, Any]) -> bool:
        """Verifies semantic well-formedness preservation: P_surface(D_deep) ≡ D_deep."""
        cls.validate_deep_syntax(deep_node)
        return (
            surface_ir.get("entity") == deep_node.identifier
            and surface_ir.get("kind") == deep_node.node_type
            and surface_ir.get("digest") == deep_node.compute_deep_digest()
        )
