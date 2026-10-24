"""Waterloo Systems Design Continuum: Situation of Concern (SoC) Normalizer.

Enforces:
- [L1-G3B-000] The Situation of Concern Normalization Invariant: Regardless of entry tier
  (Tier 1 SoC, Tier 2 Pitch, Tier 3 Reference Product), compilation CANNOT proceed to concept
  synthesis until a formal Situation of Concern (Tier 1) has been explicitly reconstructed,
  characterized, and certified.
"""

import re
from typing import List, Dict, Any, Optional

from .models import (
    SituationOfConcern,
    PitchInput,
    ReferenceProductInput,
    SoCAltitude,
    Actor,
    Friction,
    FrictionSeverity,
    EnvironmentalConstraint,
    ConstraintType,
)


class SoCNormalizationError(Exception):
    """Raised when a Situation of Concern fails formal normalization or validation."""
    pass


class SoCNormalizer:
    """Normalizes any input (Tier 1, Tier 2, or Tier 3) into a rigorous, solution-agnostic Tier 1 SoC."""

    SOLUTION_BIAS_PATTERNS = [
        re.compile(r"\b(?:build|create|use|implement|deploy|integrate)\s+(?:a|an|the)?\s*([a-zA-Z0-9_\-\s]+(?:app|application|website|platform|database|bot|agent|model|api|microservice|framework|ui|tool))\b", re.IGNORECASE),
        re.compile(r"\b(?:needs|requires|must\s+have)\s+(?:a|an)?\s*([a-zA-Z0-9_\-\s]+(?:system|dashboard|screen|button|page))\b", re.IGNORECASE),
    ]

    @classmethod
    def normalize_tier1(cls, soc: SituationOfConcern) -> SituationOfConcern:
        """Validates and certifies a directly submitted Tier 1 Situation of Concern."""
        cls._validate_completeness(soc)
        return soc

    @classmethod
    def deconstruct_pitch(
        cls,
        pitch: PitchInput,
        soc_id: str,
        altitude: SoCAltitude = SoCAltitude.MACRO
    ) -> SituationOfConcern:
        """Deconstructs a Tier 2 Elevator Pitch into a solution-agnostic Tier 1 SoC.

        Executes the Deconstruction Morphism:
        Deconstruct: Pitch -> SoC
        Strips away preconceived solution mechanics to isolate the true underlying human struggle.
        """
        extracted_biases = list(pitch.solution_biases)
        cleaned_narrative = pitch.elevator_pitch

        # Detect solution biases embedded in narrative
        for pattern in cls.SOLUTION_BIAS_PATTERNS:
            for match in pattern.finditer(cleaned_narrative):
                bias = match.group(0).strip()
                if bias not in extracted_biases:
                    extracted_biases.append(bias)

        # Formulate primary actor from target audience
        actor = Actor(
            name="Primary Operator",
            role=pitch.target_audience or "Intended User",
            motivations=[f"Overcome friction in domain: {pitch.title}"],
            frustrations=[f"Currently burdened by unsolved struggle described in '{pitch.title}'"],
        )

        # Derive frictions from intended features (what struggle necessitated them?)
        frictions: List[Friction] = []
        if pitch.intended_features:
            for feat in pitch.intended_features:
                frictions.append(
                    Friction(
                        description=f"Operational friction currently unaddressed: lack of capability for '{feat}'",
                        severity=FrictionSeverity.HIGH,
                        impact="Forces manual workarounds, cognitive overload, or systemic breakdown",
                        trigger_conditions=[f"When attempting workflow related to '{feat}'"],
                    )
                )
        else:
            frictions.append(
                Friction(
                    description=f"Systemic friction described in pitch: {pitch.elevator_pitch[:120]}...",
                    severity=FrictionSeverity.HIGH,
                    impact="Blocks human from achieving objective smoothly",
                    trigger_conditions=["Standard domain workflow"],
                )
            )

        # Unmet needs
        unmet_needs = [
            f"Seamless resolution of need currently attempted via '{feat}'"
            for feat in (pitch.intended_features or [pitch.title])
        ]

        soc = SituationOfConcern(
            soc_id=soc_id,
            title=f"SoC: {pitch.title} (Deconstructed from Pitch)",
            narrative=f"Underlying human struggle behind concept '{pitch.title}': {cleaned_narrative}",
            altitude=altitude,
            actors=[actor],
            frictions=frictions,
            constraints=[
                EnvironmentalConstraint(
                    nature=ConstraintType.ERGONOMIC,
                    description="Cognitive load must remain minimal; zero-assumption workflow",
                    boundary_limit="Human working memory capacity (Miller's law <= 7 chunks)",
                )
            ],
            unmet_needs=unmet_needs,
            induced_frictions=[f"Biases requiring de-biasing during synthesis: {', '.join(extracted_biases)}"] if extracted_biases else [],
        )

        cls._validate_completeness(soc)
        return soc

    @classmethod
    def reverse_audit_product(
        cls,
        ref: ReferenceProductInput,
        soc_id: str,
        altitude: SoCAltitude = SoCAltitude.MACRO
    ) -> SituationOfConcern:
        """Reverse-audits a Tier 3 Reference Product into a formal Tier 1 SoC.

        Executes the Reverse-Audit Morphism:
        ReverseAudit: Product -> SoC
        Identifies:
        (a) Historical problem originally solved
        (b) Induced accidental complexity, bloat, and modern unsolved frictions
        """
        actor = Actor(
            name="Reference User",
            role=f"User of legacy or reference product {ref.product_name}",
            motivations=[f"Attempting to solve: {ref.historical_problem_solved}"],
            frustrations=list(ref.known_limitations_and_bloat),
        )

        frictions: List[Friction] = []
        for limitation in ref.known_limitations_and_bloat:
            frictions.append(
                Friction(
                    description=f"Induced friction in {ref.product_name}: {limitation}",
                    severity=FrictionSeverity.HIGH,
                    impact="Degrades user agency, sovereignty, or responsiveness",
                    trigger_conditions=[f"Standard execution in {ref.product_name}"],
                )
            )

        if not frictions:
            frictions.append(
                Friction(
                    description=f"Historical friction that gave rise to {ref.product_name}: {ref.historical_problem_solved}",
                    severity=FrictionSeverity.MEDIUM,
                    impact="Baseline operational barrier",
                    trigger_conditions=["Initial problem state"],
                )
            )

        unmet_needs = [
            f"Native resolution of '{ref.historical_problem_solved}' without incurring the bloat/friction of: {lim}"
            for lim in (ref.known_limitations_and_bloat or ["accidental complexity"])
        ]

        soc = SituationOfConcern(
            soc_id=soc_id,
            title=f"SoC: Audit of {ref.product_name}",
            narrative=(
                f"Historical need: {ref.historical_problem_solved}. "
                f"However, existing implementation ({ref.product_name}) introduces critical induced frictions "
                f"that require first-principles resolution."
            ),
            altitude=altitude,
            actors=[actor],
            frictions=frictions,
            constraints=[
                EnvironmentalConstraint(
                    nature=ConstraintType.TECHNICAL,
                    description=f"Must transcend architectural limitations of {ref.product_name}",
                    boundary_limit="Zero bloat, zero unnecessary cloud lock-in",
                )
            ],
            unmet_needs=unmet_needs,
            induced_frictions=list(ref.known_limitations_and_bloat),
        )

        cls._validate_completeness(soc)
        return soc

    @classmethod
    def decompose_fractal(
        cls,
        parent: SituationOfConcern,
        sub_specs: List[Dict[str, Any]]
    ) -> SituationOfConcern:
        """Decomposes a higher-altitude SoC into child fractal SoCs (e.g. MACRO -> MESO -> MICRO)."""
        next_altitude = SoCAltitude.MESO if parent.altitude == SoCAltitude.MACRO else SoCAltitude.MICRO

        for spec in sub_specs:
            child = SituationOfConcern(
                soc_id=spec["soc_id"],
                title=spec["title"],
                narrative=spec["narrative"],
                altitude=next_altitude,
                actors=[Actor.from_dict(a) for a in spec.get("actors", [])] or list(parent.actors),
                frictions=[Friction.from_dict(f) for f in spec.get("frictions", [])],
                constraints=[EnvironmentalConstraint.from_dict(c) for c in spec.get("constraints", [])] or list(parent.constraints),
                unmet_needs=spec.get("unmet_needs", []),
                induced_frictions=spec.get("induced_frictions", []),
                parent_soc_id=parent.soc_id,
            )
            cls._validate_completeness(child)
            parent.sub_socs.append(child)

        return parent

    @classmethod
    def _validate_completeness(cls, soc: SituationOfConcern):
        """Enforces formal invariants on the normalized Situation of Concern."""
        if not soc.soc_id or not soc.soc_id.strip():
            raise SoCNormalizationError("SoC must have a valid non-empty soc_id.")
        if not soc.title or not soc.title.strip():
            raise SoCNormalizationError(f"SoC '{soc.soc_id}' must have a non-empty title.")
        if not soc.narrative or len(soc.narrative.strip()) < 10:
            raise SoCNormalizationError(f"SoC '{soc.soc_id}' narrative must be substantive (>= 10 characters).")
        if not soc.actors:
            raise SoCNormalizationError(f"SoC '{soc.soc_id}' must identify at least one human or systemic Actor.")
        if not soc.frictions:
            raise SoCNormalizationError(f"SoC '{soc.soc_id}' must document at least one Friction point.")
        if not soc.unmet_needs:
            raise SoCNormalizationError(f"SoC '{soc.soc_id}' must articulate at least one Unmet Need.")
