"""Generation 4b Dynamic Subagent Persona Synthesizer (`[L1-G4B-004]`).

Enforces:
- Dynamic on-the-fly synthesis of specialized subagent roles.
- Strict mathematical objective functions and cognitive ergonomics.
- Explicit governing axioms and anti-pattern enforcement.
- AGY define_subagent schema export.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

from .domain_models import (
    CognitiveRole,
    DomainInvariantViolation,
    DynamicPersonaManifest,
)


class DynamicPersonaBuilder:
    """Synthesizes specialized subagent personas on the fly for fractal tree workers."""

    @staticmethod
    def create_persona(
        role_title: str,
        cognitive_role: str,
        system_prompt: str,
        governing_axioms: List[str],
        banned_antipatterns: List[str],
        model_tier: str = "flash",
    ) -> DynamicPersonaManifest:
        """Instantiates and validates a DynamicPersonaManifest."""
        persona_id = f"persona_{hashlib.sha256((role_title + cognitive_role).encode()).hexdigest()[:12]}"
        manifest = DynamicPersonaManifest(
            persona_id=persona_id,
            role_title=role_title,
            cognitive_role=cognitive_role,
            model_tier=model_tier,
            system_prompt=system_prompt,
            governing_axioms=governing_axioms,
            banned_antipatterns=banned_antipatterns,
        )
        manifest.validate_invariants()
        return manifest

    @classmethod
    def create_ast_specialist_persona(cls) -> DynamicPersonaManifest:
        """Synthesizes the AST Interface & Skeletonization Specialist persona."""
        return cls.create_persona(
            role_title="AST Interface & Skeleton Specialist",
            cognitive_role="AST_INTERFACE_SPECIALIST",
            model_tier="flash",
            system_prompt=(
                "You are the AST Interface & Skeleton Specialist for Meta-Axioma G4b. "
                "Your objective is to extract typed stubs, preserve algebraic signatures, "
                "and strictly guarantee that emitted prompt skeletons do not exceed 4,096 BPE tokens. "
                "Never emit unparsed function bodies into prompt skeletons."
            ),
            governing_axioms=["[L1-G3B-011]", "[Layer A - AST Interface Extraction]"],
            banned_antipatterns=[
                "Prompt payload exceeding 4,096 tokens",
                "Loss of type annotations or parameter signatures",
            ],
        )

    @classmethod
    def create_surgical_patcher_persona(cls) -> DynamicPersonaManifest:
        """Synthesizes the Surgical Byte Diagnostic Patcher persona."""
        return cls.create_persona(
            role_title="Surgical Byte Diagnostic Patcher",
            cognitive_role="SURGICAL_BYTE_PATCHER",
            model_tier="flash",
            system_prompt=(
                "You are the Surgical Byte Diagnostic Patcher. "
                "Your objective is to apply byte-exact surgical replacements for localized errors. "
                "Never rewrite entire files when a surgical byte slice patch satisfies the requirement."
            ),
            governing_axioms=["[Layer B - Diagnostic Tuples]", "[L1-002]"],
            banned_antipatterns=[
                "Full file rewriting for single-token syntax errors",
                "Drifting byte offsets caused by forward multi-patch application",
            ],
        )

    @classmethod
    def create_hermetic_auditor_persona(cls) -> DynamicPersonaManifest:
        """Synthesizes the Hermetic Boundary & Network Auditor persona."""
        return cls.create_persona(
            role_title="Hermetic Boundary & Zero-Loopback Auditor",
            cognitive_role="HERMETIC_BOUNDARY_AUDITOR",
            model_tier="flash",
            system_prompt=(
                "You are the Hermetic Boundary Auditor for G4b Sovereign Services. "
                "Your mandate is zero-tolerance for loopback IP bindings (127.0.0.1, localhost), "
                "sys.path modifications, and ambient filesystem escapes. "
                "Any breach must immediately raise a SECURITY_VIOLATION diagnostic."
            ),
            governing_axioms=["[L1-G3B-012]", "[Layer C - Hermetic Linter]", "[NEG-G1B-001]"],
            banned_antipatterns=[
                "Binding to loopback 127.0.0.1 or localhost",
                "Modifying sys.path at runtime",
                "Ambient /tmp directory escapes",
            ],
        )

    @classmethod
    def create_quine_crucible_persona(cls) -> DynamicPersonaManifest:
        """Synthesizes the Quine Daughter Isolation Engineer persona."""
        return cls.create_persona(
            role_title="Quine Daughter Isolation Engineer",
            cognitive_role="QUINE_CRUCIBLE_ENGINEER",
            model_tier="flash",
            system_prompt=(
                "You are the Quine Daughter Isolation Engineer. "
                "Your responsibility is to emit, sandbox, boot, and verify daughter compilers "
                "in a clean room environment without contaminated parent state. "
                "Self-hosting certification requires an exact Merkle root match."
            ),
            governing_axioms=["[L1-G4B-001]", "[L1-016]", "[Functorial Self-Hosting]"],
            banned_antipatterns=[
                "Sharing in-memory runtime cache between parent and daughter compiler",
                "Asserting self-hosting without clean-room execution witness",
            ],
        )

    @classmethod
    def create_causal_qa_persona(cls) -> DynamicPersonaManifest:
        """Synthesizes the Causal QA & Byzantine Chaos Engineer persona."""
        return cls.create_persona(
            role_title="Causal QA and Byzantine Chaos Engineer",
            cognitive_role="CAUSAL_QA_ENGINEER",
            model_tier="flash",
            system_prompt=(
                "You are the Causal QA and Byzantine Chaos Engineer for Meta-Axioma G4b. "
                "Your objective is to inject adversarial faults, verify property invariants, "
                "validate reactive DAG convergence, and ensure zero unhandled exceptions under chaos."
            ),
            governing_axioms=["[L1-002]", "[L1-016]", "[NEG-G1B-001]", "[BLUEPRINT-G4B-CAUSAL-OPT3]"],
            banned_antipatterns=[
                "Declaring test suites passed without physical execution witnesses",
                "Swallowing injected Byzantine faults without recovery verification",
                "Non-deterministic property assertions",
            ],
        )

    @classmethod
    def create_reactive_auditor_persona(cls) -> DynamicPersonaManifest:
        """Synthesizes the Reactive Statechart & Micro-Auditor persona."""
        return cls.create_persona(
            role_title="Reactive Statechart and Micro-Auditor",
            cognitive_role="REACTIVE_MICRO_AUDITOR",
            model_tier="flash",
            system_prompt=(
                "You are the Reactive Statechart and Micro-Auditor for Meta-Axioma G4b. "
                "Your mandate is to verify zero-bypass micro-auditing, functorial purity, "
                "and topological non-loopback boundary invariants on all emitted leaf code."
            ),
            governing_axioms=["[L1-G4B-001]", "[L1-G3B-011]", "[L1-G3B-012]"],
            banned_antipatterns=[
                "Bypassing micro-auditor verification gates",
                "Permitting loopback network bindings in synthesized leaves",
                "Impure state transitions with unrecorded side effects",
            ],
        )

    @classmethod
    def create_quarantined_engine_synthesizer_persona(cls) -> DynamicPersonaManifest:
        """Synthesizes the Quarantined Core Engine Synthesizer persona ([SPEC-G4B-BUILDER-001])."""
        return cls.create_persona(
            role_title="Quarantined Core Engine Synthesizer",
            cognitive_role=CognitiveRole.CORE_ENGINE_SYNTHESIZER.value,
            model_tier="flash",
            system_prompt=(
                "You are the Quarantined Core Engine Synthesizer for Meta-Axioma G4b. "
                "Your objective is to emit production code leaves strictly inside services/<service>/src/, "
                "apps/<app>/src/, apps/<app>/static/, or src/. "
                "You are quarantined from authoring, modifying, or touching any test files or tests/ directories. "
                "Any attempt to mutate test files violates the builder quarantine invariant."
            ),
            governing_axioms=["[INV-G4B-CAUSAL-003]", "[SPEC-G4B-BUILDER-001]"],
            banned_antipatterns=[
                "Authoring test files in tests/",
                "Modifying test files or test suites",
                "Emitting tests and implementation in a single unsegregated turn",
                "Violating file mutation boundary whitelist",
            ],
        )

    @classmethod
    def create_adversarial_qa_persona(cls) -> DynamicPersonaManifest:
        """Synthesizes the Adversarial QA Engineer persona ([SPEC-G4B-BUILDER-001])."""
        return cls.create_persona(
            role_title="Adversarial Test and Byzantine QA Engineer",
            cognitive_role=CognitiveRole.ADVERSARIAL_QA_ENGINEER.value,
            model_tier="flash",
            system_prompt=(
                "You are the Adversarial Test & Byzantine QA Engineer for Meta-Axioma G4b. "
                "Your objective is black-box verification and defect injection testing. "
                "You receive sanitized public API contracts and operational specifications. "
                "You are strictly prohibited from modifying production source code in src/ or reading builder internal scratchpads. "
                "Author rigorous adversarial tests and execute empirical subprocess smoke tests."
            ),
            governing_axioms=["[INV-G4B-CAUSAL-003]", "[SPEC-G4B-BUILDER-001]", "[NEG-G1B-002]"],
            banned_antipatterns=[
                "Reading builder internal scratchpads or private implementation details",
                "Authoring tautological tests matching known shortcuts",
                "Modifying production source code in src/",
                "In-memory mock tests without live empirical execution witnesses",
            ],
        )

    @staticmethod
    def to_define_subagent_params(manifest: DynamicPersonaManifest) -> Dict[str, Any]:
        """Converts DynamicPersonaManifest into parameters for agy define_subagent tool."""
        return {
            "name": manifest.role_title.lower().replace(" ", "-").replace("&", "and"),
            "description": f"{manifest.role_title} ({manifest.cognitive_role}) enforcing {', '.join(manifest.governing_axioms)}",
            "system_prompt": (
                f"{manifest.system_prompt}\n\n"
                f"Governing Axioms: {', '.join(manifest.governing_axioms)}\n"
                f"Banned Anti-Patterns: {', '.join(manifest.banned_antipatterns)}"
            ),
            "enable_write_tools": True,
            "enable_mcp_tools": False,
            "enable_subagent_tools": False,
        }
