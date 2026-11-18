"""Generation 4b Canonical Gemini 4 Cognitive Routing Protocol (`[L1-G3B-014]`, `[L1-G4B-001]`).

Enforces:
- Strictly Python stdlib only — zero imports from `services/*` (`[L1-G4B-001]`).
- Stateless pure mapping — zero global mutable feature flags (`NEG-001`).
- Zero Argon in active Gen 4b routing:
  - Brain / Research / Audit / Red Team roles -> Gemini 4 Neon (`agy_model_param="pro"`).
  - Muscle / Code / QA / Dashboard roles -> Gemini 4 Hydrogen (`agy_model_param="flash"`).
  - Read-only discovery roles -> Gemini 4 Hydrogen (Lite) (`agy_model_param="flash_lite"`).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, FrozenSet


VALID_AGY_MODEL_PARAMS: tuple[str, ...] = ("pro", "flash", "flash_lite", "inherit")


class Gemini4ModelTier(str, Enum):
    """Logical Gemini 4 cognitive model tiers mapped onto AGY runtime selectors."""

    BRAIN_NEON = "Gemini 4 Neon"
    MUSCLE_HYDROGEN = "Gemini 4 Hydrogen"
    DISCOVERY_LITE = "Gemini 4 Hydrogen (Lite)"


class RoutingProtocolViolation(Exception):
    """Raised when an invalid AGY model selector or unknown cognitive role is supplied."""

    pass


@dataclass(frozen=True)
class RoutingDecision:
    """Immutable routing resolution decoupling logical Gemini 4 tier from AGY enum param."""

    cognitive_role: str
    logical_tier: Gemini4ModelTier
    agy_model_param: str
    display_tier: str
    witness_model_label: str
    is_brain: bool

    def __post_init__(self) -> None:
        if self.agy_model_param not in VALID_AGY_MODEL_PARAMS:
            raise RoutingProtocolViolation(
                f"Invalid agy_model_param '{self.agy_model_param}'. "
                f"Expected one of: {', '.join(VALID_AGY_MODEL_PARAMS)}."
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize routing decision into a plain JSON-compatible dictionary."""
        return {
            "cognitive_role": self.cognitive_role,
            "logical_tier": self.logical_tier.value,
            "agy_model_param": self.agy_model_param,
            "display_tier": self.display_tier,
            "witness_model_label": self.witness_model_label,
            "is_brain": self.is_brain,
        }


BRAIN_ROLES: FrozenSet[str] = frozenset(
    {
        "ORCHESTRATOR_FSM",
        "SOC_NORMALIZATION",
        "MODEL_CHECKER",
        "JOURNEY_WALKER",
        "ZERO_TRUST_AUDITOR",
        "DIALECTICAL_EXPLORATION",
        "HUMAN_ERGONOMICS_ARCHITECT",
        "DOMAIN_ONTOLOGIST",
        "DISTRIBUTED_TOPOLOGY_ARCHITECT",
        "STATECHART_FSM_ENGINEER",
        "SOCRATIC_RED_TEAM",
        "DIALECTICAL_RED_TEAM",
        "HERMETIC_BOUNDARY_AUDITOR",
        "REACTIVE_MICRO_AUDITOR",
        "QUINE_CRUCIBLE_ENGINEER",
    }
)

RED_TEAM_ROLES: FrozenSet[str] = frozenset(
    {
        "SOCRATIC_RED_TEAM",
        "DIALECTICAL_RED_TEAM",
    }
)

MUSCLE_ROLES: FrozenSet[str] = frozenset(
    {
        "LEAF_CODE_EMISSION",
        "LEAF_SCHEMA_EMISSION",
        "LEAF_DATA_EMISSION",
        "LEAF_STYLE_EMISSION",
        "CORE_ENGINE_SYNTHESIZER",
        "OPERATIONAL_DASHBOARD_SYNTHESIZER",
        "ADVERSARIAL_QA_ENGINEER",
        "AST_INTERFACE_SPECIALIST",
        "SURGICAL_BYTE_PATCHER",
        "CAUSAL_QA_ENGINEER",
    }
)

DISCOVERY_ROLES: FrozenSet[str] = frozenset(
    {
        "CODEBASE_DISCOVERY",
        "TELEMETRY_INSPECTOR",
        "MECHANICAL_HOUSEKEEPING",
    }
)


def resolve_role_routing(
    cognitive_role: str | Enum,
    *,
    tier_label: str | None = None,
) -> RoutingDecision:
    """Resolve a cognitive role to an immutable Gemini 4 routing decision."""
    raw_role = cognitive_role.value if isinstance(cognitive_role, Enum) else str(cognitive_role)
    normalized_role = raw_role.strip().upper()
    if not normalized_role:
        raise RoutingProtocolViolation("cognitive_role must not be empty.")

    if normalized_role in BRAIN_ROLES:
        default_tier = (
            "Red Team Gate (Brain)"
            if normalized_role in RED_TEAM_ROLES
            else "Brain Gate"
        )
        return RoutingDecision(
            cognitive_role=normalized_role,
            logical_tier=Gemini4ModelTier.BRAIN_NEON,
            agy_model_param="pro",
            display_tier=tier_label if tier_label is not None else default_tier,
            witness_model_label=Gemini4ModelTier.BRAIN_NEON.value,
            is_brain=True,
        )

    if normalized_role in MUSCLE_ROLES:
        return RoutingDecision(
            cognitive_role=normalized_role,
            logical_tier=Gemini4ModelTier.MUSCLE_HYDROGEN,
            agy_model_param="flash",
            display_tier=tier_label if tier_label is not None else "Muscle",
            witness_model_label=Gemini4ModelTier.MUSCLE_HYDROGEN.value,
            is_brain=False,
        )

    if normalized_role in DISCOVERY_ROLES:
        return RoutingDecision(
            cognitive_role=normalized_role,
            logical_tier=Gemini4ModelTier.DISCOVERY_LITE,
            agy_model_param="flash_lite",
            display_tier=tier_label if tier_label is not None else "Discovery (Lite)",
            witness_model_label=Gemini4ModelTier.DISCOVERY_LITE.value,
            is_brain=False,
        )

    raise RoutingProtocolViolation(
        f"Unknown cognitive_role '{raw_role}' (normalized: '{normalized_role}')."
    )


def is_brain_model_label(model_label: str, tier_label: str = "") -> bool:
    """Return True for Brain/Red Team model or tier labels (including historical Argon archives)."""
    model_lower = model_label.lower()
    tier_lower = tier_label.lower()
    return (
        "neon" in model_lower
        or "argon" in model_lower
        or "brain" in tier_lower
        or "red team" in tier_lower
    )
