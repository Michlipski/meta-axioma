"""Waterloo Situation of Concern (SoC) Normalization Module."""

from .models import (
    SoCAltitude,
    FrictionSeverity,
    ConstraintType,
    Actor,
    Friction,
    EnvironmentalConstraint,
    SituationOfConcern,
    PitchInput,
    ReferenceProductInput,
)
from .normalizer import SoCNormalizer, SoCNormalizationError
from .elenchus_seed import (
    SOC_ID_ELENCHUS,
    REQUIRED_INVARIANTS_ELENCHUS,
    build_epistemic_curiosity_soc,
    build_epistemic_curiosity_contract_ir,
    build_epistemic_curiosity_statechart_ir,
    build_epistemic_curiosity_topology_ir,
    build_epistemic_curiosity_domain_spec,
)

__all__ = [
    "SoCAltitude",
    "FrictionSeverity",
    "ConstraintType",
    "Actor",
    "Friction",
    "EnvironmentalConstraint",
    "SituationOfConcern",
    "PitchInput",
    "ReferenceProductInput",
    "SoCNormalizer",
    "SoCNormalizationError",
    "SOC_ID_ELENCHUS",
    "REQUIRED_INVARIANTS_ELENCHUS",
    "build_epistemic_curiosity_soc",
    "build_epistemic_curiosity_contract_ir",
    "build_epistemic_curiosity_statechart_ir",
    "build_epistemic_curiosity_topology_ir",
    "build_epistemic_curiosity_domain_spec",
]

