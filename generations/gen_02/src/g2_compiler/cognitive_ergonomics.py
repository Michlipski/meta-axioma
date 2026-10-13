"""Cognitive Ergonomics & Persona Alignment Invariance [L1-G2-003].

Phenomenological HCI Principle:
    D_KL(Model_User || Model_System) ≤ ε_ergonomics
    Utility(A_app) = PersonaGoalVelocity / (1 + CognitiveFriction) > U_min
    Every user-facing boundary synthesized by Generation 2 must minimize mental model
    divergence and maximize persona goal velocity.
"""

from typing import Any, Dict, List, Optional
import math

from g2_compiler.types import ErgonomicsAuditResult, PersonaModel


class CognitiveErgonomicsAuditor:
    """Measures mental model divergence, cognitive friction, and persona goal velocity."""

    def __init__(
        self,
        epsilon_ergonomics: float = 0.50,
        min_utility_threshold: float = 0.65,
    ):
        self.epsilon_ergonomics = epsilon_ergonomics
        self.min_utility_threshold = min_utility_threshold

    def calculate_kl_divergence(
        self,
        persona: PersonaModel,
        system_vocabulary: List[str],
    ) -> float:
        """Approximates KL divergence D_KL(P || Q) over domain concepts and vocabulary.
        
        P = Persona's expected vocabulary probability distribution.
        Q = System's emitted vocabulary and terminology distribution.
        """
        user_vocab_set = set(w.lower() for w in persona.expected_vocabulary)
        sys_vocab_set = set(w.lower() for w in system_vocabulary)

        if not user_vocab_set:
            return 0.0

        # Overlap proportion
        matched_words = len(user_vocab_set.intersection(sys_vocab_set))
        total_user_words = len(user_vocab_set)

        p_match = max(matched_words / total_user_words, 1e-4)
        p_unmatched = 1.0 - p_match

        # Surrogate distribution comparison:
        # Expected: user expects familiar terms with high probability (p=0.90)
        # Observed: system provides familiar terms with probability p_match
        p = 0.90
        q = min(max(p_match, 0.05), 0.95)

        # Binary KL divergence D_KL(p || q) = p * ln(p/q) + (1-p) * ln((1-p)/(1-q))
        kl = p * math.log(p / q) + (1.0 - p) * math.log((1.0 - p) / (1.0 - q))
        return max(kl, 0.0)

    def evaluate_interface_ergonomics(
        self,
        persona: PersonaModel,
        system_vocabulary: List[str],
        interaction_steps: int,
        cryptic_error_count: int,
        undo_available: bool,
        task_completion_seconds: float,
    ) -> ErgonomicsAuditResult:
        """Audits an application interface against persona ergonomic invariants."""
        rejection_reasons: List[str] = []

        # 1. KL Divergence (vocabulary / conceptual divergence)
        kl = self.calculate_kl_divergence(persona, system_vocabulary)
        if kl > self.epsilon_ergonomics:
            rejection_reasons.append(
                f"KL divergence {kl:.3f} exceeds tolerance {self.epsilon_ergonomics:.3f}: vocabulary disconnect."
            )

        # 2. Cognitive Friction Index
        # Base friction from steps + heavy penalty for cryptic errors - credit for undo
        base_friction = max(interaction_steps - 1, 0) * 0.15
        error_friction = cryptic_error_count * 0.40
        reversibility_bonus = -0.20 if undo_available else 0.20

        cognitive_friction = max(base_friction + error_friction + reversibility_bonus, 0.05)

        if cryptic_error_count > 0:
            rejection_reasons.append(
                f"Contains {cryptic_error_count} unhandled/cryptic error codes without humane recovery affordance."
            )

        # 3. Persona Goal Velocity
        # Normalized inverse of time taken: velocity = 10.0 / (seconds + 1)
        persona_goal_velocity = min(10.0 / (max(task_completion_seconds, 1.0)), 2.0)

        # 4. Ergonomic Utility Formula
        utility = persona_goal_velocity / (1.0 + cognitive_friction)

        if utility < self.min_utility_threshold:
            rejection_reasons.append(
                f"Ergonomic utility score {utility:.3f} below minimum threshold {self.min_utility_threshold:.3f}."
            )

        is_acceptable = len(rejection_reasons) == 0

        return ErgonomicsAuditResult(
            persona_name=persona.persona_name,
            kl_divergence=kl,
            cognitive_friction=cognitive_friction,
            persona_goal_velocity=persona_goal_velocity,
            utility_score=utility,
            is_acceptable=is_acceptable,
            rejection_reasons=rejection_reasons,
        )
