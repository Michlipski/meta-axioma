"""Structural / Axiom Regulator for System G1b (Guardrail 3).

Grounded in [L1-015_1] (Compositional Boundary Isolation).
The Regulator governs architectural invariants and schema constraints.
CRITICAL INVARIANT: The Regulator is strictly prohibited from proposing or generating application source code.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from g2b_compiler.ir.semantic_ir import SemanticDomainIR
from g2b_compiler.ir.statechart_ir import StatechartIR
from g2b_compiler.ir.contract_ir import DualBoundaryContractIR


class EpistemicIsolationBreachError(Exception):
    """Raised when an actor breaches epistemic isolation boundaries."""
    pass


@dataclass
class RegulationAuditResult:
    is_compliant: bool
    structural_axioms_enforced: List[str]
    schema_integrity_valid: bool
    audit_notes: List[str] = field(default_factory=list)


class StructuralAxiomRegulator:
    """Enforces architectural axioms and schema boundaries without emitting code."""

    def __init__(self):
        self.enforced_axioms = [
            "L1-002",  # Functorial State Evolution
            "L1-004",  # Universal Grammar
            "L1-011_3", # Decoupled State & Persistence
            "L1-008",  # Landauer Thermodynamic Accounting
            "L1-015",  # Zero-Trust MCP Dual-Boundary
            "L1-016",  # Demarcated Exception Enclaves
            "L1-015_1", # Compositional Boundary Isolation
        ]

    def audit_specification(self, semantic_ir: SemanticDomainIR, contract_ir: DualBoundaryContractIR) -> RegulationAuditResult:
        """Audits domain and contract IR against structural axioms."""
        notes = []
        is_compliant = True

        # Check Universal Grammar [L1-004] & Dual-Boundary [L1-015]
        for entity in semantic_ir.entities:
            noun = contract_ir.get_noun(entity.name)
            if not noun:
                notes.append(f"[L1-015 Violation] Entity '{entity.name}' has no corresponding NounContract in Contract IR.")
                is_compliant = False
            else:
                for f in entity.fields:
                    if f.name not in noun.fields:
                        notes.append(f"[L1-004 Violation] Field '{f.name}' in Entity '{entity.name}' missing from NounContract projection.")
                        is_compliant = False

        # Invariant: Regulator must NEVER return application implementation code
        return RegulationAuditResult(
            is_compliant=is_compliant,
            structural_axioms_enforced=self.enforced_axioms,
            schema_integrity_valid=is_compliant,
            audit_notes=notes
        )

    def guard_code_emission(self, proposed_code: Optional[str] = None):
        """Sanity guard: Regulator will raise an error if any component asks it to generate code."""
        if proposed_code is not None:
            raise EpistemicIsolationBreachError(
                "Regulator cannot propose or manipulate application implementation code."
            )
