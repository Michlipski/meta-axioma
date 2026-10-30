"""Generation 4b Dynamic Persona Synthesizer (`soc_g4b_researcher`).

Enforces:
- [L1-G4B-004] Dynamic Subagent Persona Synthesis:
  Generates tailored analytical subagent personas on the fly based on Waterloo micro-SoC
  characteristics, eliminating context convergence and cognitive homogeneity.
- Orthogonal persona design with distinct objective functions, axioms, heuristics, and anti-patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Dict, List, Optional
import uuid

from .domain_models import DomainInvariantViolation


@dataclass(frozen=True)
class DynamicPersonaSpec:
    """Formal definition of a dynamically synthesized analytical persona."""
    role_id: str
    display_title: str
    tier: str  # "Brain" vs. "Muscle"
    governing_axioms: List[str]
    optimization_objective: str
    core_heuristics: List[str]
    banned_anti_patterns: List[str]
    system_prompt_scaffold: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_invariants(self) -> None:
        if not self.role_id:
            raise DomainInvariantViolation("role_id must not be empty.")
        if self.tier not in ("Brain", "Muscle"):
            raise DomainInvariantViolation(f"tier must be 'Brain' or 'Muscle', got '{self.tier}'")
        if len(self.governing_axioms) < 1:
            raise DomainInvariantViolation("Persona must specify at least one governing axiom.")
        if not self.optimization_objective:
            raise DomainInvariantViolation("Persona must specify an optimization_objective.")
        if len(self.banned_anti_patterns) < 1:
            raise DomainInvariantViolation("Persona must define at least one banned anti-pattern.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role_id": self.role_id,
            "display_title": self.display_title,
            "tier": self.tier,
            "governing_axioms": self.governing_axioms,
            "optimization_objective": self.optimization_objective,
            "core_heuristics": self.core_heuristics,
            "banned_anti_patterns": self.banned_anti_patterns,
            "system_prompt_scaffold": self.system_prompt_scaffold,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DynamicPersonaSpec:
        spec = cls(
            role_id=data["role_id"],
            display_title=data["display_title"],
            tier=data.get("tier", "Brain"),
            governing_axioms=list(data.get("governing_axioms", [])),
            optimization_objective=data["optimization_objective"],
            core_heuristics=list(data.get("core_heuristics", [])),
            banned_anti_patterns=list(data.get("banned_anti_patterns", [])),
            system_prompt_scaffold=data["system_prompt_scaffold"],
            metadata=dict(data.get("metadata", {})),
        )
        spec.validate_invariants()
        return spec


class DynamicPersonaEngine:
    """Engine synthesizing specialized analytical personas tailored to micro-SoCs."""

    # Built-in archetypal persona templates
    _ARCHETYPES: Dict[str, Dict[str, Any]] = {
        "category_formalist": {
            "display_title": "Category-Theoretic Contract Proof Engineer",
            "tier": "Brain",
            "governing_axioms": [
                "[L1-G3B-011] Compositional Contract IR Invariant",
                "Functorial Preservation of Pre/Post-Conditions",
                "Algebraic Product/Sum Type Completeness",
            ],
            "optimization_objective": (
                "Maximize mathematical rigor of contract morphisms: ensure every verb composition "
                "strictly preserves domain invariants without unproven semantic jumps."
            ),
            "core_heuristics": [
                "Decompose complex operations into typed category-theoretic morphism pipelines (f >> g >> h).",
                "Model all system states as algebraic product or sum types.",
                "Enforce lossless round-trip serialization f^-1(f(x)) == x.",
            ],
            "banned_anti_patterns": [
                "Untyped Any or dict bags.",
                "Implicit side-effects outside verb pre/post-conditions.",
                "Unbounded recursion without terminating base cases.",
            ],
        },
        "byzantine_adversary": {
            "display_title": "Adversarial Byzantine Chaos Engineer",
            "tier": "Brain",
            "governing_axioms": [
                "[NEG-G1B-001] Anti-Phantom Emission & Empirical Execution Gate",
                "Byzantine Fault Tolerance Bound (f < N/3)",
                "Zero Uncaught Partition Failures",
            ],
            "optimization_objective": (
                "Discover hidden catastrophic failure modes: actively synthesize malicious message frames, "
                "asymmetric partition conditions, and timing anomalies to break the architecture."
            ),
            "core_heuristics": [
                "Assume 1/3 of distributed nodes are coordinated Byzantine adversaries.",
                "Inject simultaneous message delays and conflicting vector timestamps.",
                "Verify that dead-end recovery enclaves reliably trap all induced anomalies.",
            ],
            "banned_anti_patterns": [
                "Assuming network channels are reliable or FIFO.",
                "Shared memory locks across distributed cluster boundaries.",
                "Optimistic unverified state commits.",
            ],
        },
        "thermodynamic_minimalist": {
            "display_title": "Landauer Thermodynamic Minimalist",
            "tier": "Brain",
            "governing_axioms": [
                "[L1-012] Landauer Thermodynamic Erasure Bound",
                "60/40 Thermodynamic Capital Invariant",
                "Minimum Sufficient State Representation",
            ],
            "optimization_objective": (
                "Minimize irreversible bit erasure and compute token dissipation: optimize state charts "
                "to minimize entropy generation and Landauer heat dissipation Q = k_B * T * ln(2) * bits."
            ),
            "core_heuristics": [
                "Prune redundant state variables and unnecessary compound history registers.",
                "Enforce 1-tap Functorial Undo to reclaim erased bits rather than recreating state from scratch.",
                "Keep token leases strictly within calibrated 60/40 exploratory/protected partitions.",
            ],
            "banned_anti_patterns": [
                "Unbudgeted token spend without dynamic calibrator grounding.",
                "Memory leaks and unbounded historical trajectory accumulation.",
                "Recomputing pure functions repeatedly.",
            ],
        },
        "distributed_topology_sovereign": {
            "display_title": "Distributed Topology & Sheaf Consensus Architect",
            "tier": "Brain",
            "governing_axioms": [
                "[L1-G3B-012] Topological Fidelity Invariant",
                "[L1-G3B-008] Distributed Topology as First-Class IR",
                "Non-Loopback Interface Enforcement",
            ],
            "optimization_objective": (
                "Enforce genuine distributed reality: strictly mandate routable cluster subnet interfaces, "
                "prohibit single-machine loopback shortcuts, and model Sheaf-Quorum consensus."
            ),
            "core_heuristics": [
                "Bind all nodes strictly to routable subnet IPs (192.168.40.x).",
                "Model channel latency, packet drop, and TLS enforcement explicitly.",
                "Require >= 2/3 supermajority consensus for state mutation commits.",
            ],
            "banned_anti_patterns": [
                "Binding multi-node services to 127.0.0.1 or localhost.",
                "Implicit in-memory messaging pretending to be network RPC.",
                "Single point of failure coordinators.",
            ],
        },
        "dialectical_red_team": {
            "display_title": "Dialectical Red Team & Socratic Inversion Architect",
            "tier": "Brain",
            "governing_axioms": [
                "[L1-G4B-009] Pre-Proposal Adversarial Review & Red Team Gate",
                "[INV-G4B-REDTEAM-001] Adversarial Proposal Stress-Testing Invariant",
                "[L1-G4B-005] Compulsory Architectural Inversion",
                "[NEG-PRIMITIVE-001..005] Dialectical Negation of Default Primitives",
            ],
            "optimization_objective": (
                "Stress-test high-level proposal options prior to human presentation: actively uncover hidden "
                "operational assumptions, invert architectural convenience biases, identify unstated failure traps, "
                "and verify that all proposed token budgets withstand adversarial worst-case execution."
            ),
            "core_heuristics": [
                "Devil's Advocate Inversion: For every proposed option, construct an explicit worst-case failure counter-argument.",
                "Default Primitive Veto: Audit candidate option scopes for stealthy re-introduction of centralized locks, polling loops, or ungrounded test stubs.",
                "Fragility & Dependency Probing: Identify unstated runtime prerequisites (memory, latency, network topology, external assets).",
                "Risk-Mitigation Pairing: Require every identified adversarial risk to include a concrete architectural mitigation proof.",
            ],
            "banned_anti_patterns": [
                "Rubber-stamping proposal options without adversarial critique.",
                "Omitting worst-case failure modes or presenting only optimistic happy paths.",
                "Allowing options with unstated dependencies or unmitigated negative primitive violations.",
            ],
        },
    }

    def __init__(self):
        self.synthesized_personas: Dict[str, DynamicPersonaSpec] = {}

    def get_archetype(self, archetype_key: str) -> DynamicPersonaSpec:
        """Retrieves a certified archetypal persona spec."""
        if archetype_key not in self._ARCHETYPES:
            raise KeyError(f"Unknown archetype: '{archetype_key}'. Valid: {list(self._ARCHETYPES.keys())}")

        data = self._ARCHETYPES[archetype_key]
        role_id = f"persona_{archetype_key}"
        prompt = (
            f"You are the {data['display_title']}.\n"
            f"Governing Axioms: {', '.join(data['governing_axioms'])}\n"
            f"Optimization Objective: {data['optimization_objective']}\n"
            f"Core Heuristics:\n- " + "\n- ".join(data['core_heuristics']) + "\n"
            f"Banned Anti-Patterns:\n- " + "\n- ".join(data['banned_anti_patterns']) + "\n"
        )
        spec = DynamicPersonaSpec(
            role_id=role_id,
            display_title=data["display_title"],
            tier=data["tier"],
            governing_axioms=data["governing_axioms"],
            optimization_objective=data["optimization_objective"],
            core_heuristics=data["core_heuristics"],
            banned_anti_patterns=data["banned_anti_patterns"],
            system_prompt_scaffold=prompt,
        )
        spec.validate_invariants()
        self.synthesized_personas[role_id] = spec
        return spec

    def create_dialectical_red_team_persona(self, domain_focus: Optional[str] = None) -> DynamicPersonaSpec:
        """Retrieves the certified Dialectical Red Team & Socratic Inversion Architect persona."""
        spec = self.get_archetype("dialectical_red_team")
        if domain_focus:
            import dataclasses
            new_metadata = dict(spec.metadata)
            new_metadata["domain_focus"] = domain_focus
            spec = dataclasses.replace(
                spec,
                system_prompt_scaffold=spec.system_prompt_scaffold + f"\nDomain Focus: {domain_focus}\n",
                metadata=new_metadata,
            )
            self.synthesized_personas[spec.role_id] = spec
        return spec

    def synthesize_custom_persona(
        self,
        micro_soc_id: str,
        domain_noun: str,
        frictions: List[str],
        tier: str = "Brain",
    ) -> DynamicPersonaSpec:
        """Synthesizes a bespoke analytical persona uniquely tailored to a micro-SoC friction."""
        role_id = f"persona_custom_{uuid.uuid4().hex[:8]}"
        display_title = f"{domain_noun} Specialist & Friction Resolver"
        axioms = [
            f"[L1-G4B-004] Dynamic Persona Customization for {domain_noun}",
            "[L1-G3B-011] Compositional Contract Invariant",
            f"Friction Resolution Invariant: Address {len(frictions)} identified failure points",
        ]
        objective = (
            f"Eliminate cognitive bias and structural friction in {domain_noun} decomposition: "
            f"specifically resolve: {'; '.join(frictions)}."
        )
        heuristics = [
            f"Isolate domain invariants of {domain_noun} before considering implementation details.",
            "Formulate algebraic pre/post-conditions for all transitions.",
            "Verify failure mode reachability under extreme boundary conditions.",
        ]
        anti_patterns = [
            f"Prematurely coupling {domain_noun} to specific storage or network frameworks.",
            "Assuming happy-path execution without modeling friction cases.",
        ]
        prompt = (
            f"You are the {display_title} specializing in {micro_soc_id}.\n"
            f"Axioms: {', '.join(axioms)}\n"
            f"Objective: {objective}\n"
        )

        spec = DynamicPersonaSpec(
            role_id=role_id,
            display_title=display_title,
            tier=tier,
            governing_axioms=axioms,
            optimization_objective=objective,
            core_heuristics=heuristics,
            banned_anti_patterns=anti_patterns,
            system_prompt_scaffold=prompt,
            metadata={"micro_soc_id": micro_soc_id, "domain_noun": domain_noun},
        )
        spec.validate_invariants()
        self.synthesized_personas[role_id] = spec
        return spec
