"""Generation 3b Dual-Model Cognitive Router.

Enforces:
- [L1-G3B-014] Cognitive Routing Invariant:
  The Meta-Orchestrator must implement a strictly partitioned, dual-model LLM router:
  1. The Brain (Orchestrator & Evaluators): Gemini 4 Argon.
     Exclusively reserved for the deterministic FSM orchestrator, dialectical exploration,
     Waterloo SoC normalization, and all Zero-Trust Evaluators (checker.py, journey_walker.py, micro_auditors.py).
  2. The Muscle (Leaf-Node Emission): Gemini 3.8 Flash.
     Exclusively utilized for indivisible, leaf-node generation tasks (AST code, schemas, leaf templates).
     Any failure at this layer triggers an isolated re-prompt governed by the Argon evaluators.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, Set


class CognitiveRole(str, Enum):
    """Classification of cognitive task for model routing."""
    # THE BRAIN: Gemini 4 Argon
    ORCHESTRATOR_FSM = "orchestrator_fsm"
    SOC_NORMALIZATION = "soc_normalization"
    MODEL_CHECKER = "model_checker"
    JOURNEY_WALKER = "journey_walker"
    ZERO_TRUST_AUDITOR = "zero_trust_auditor"
    DIALECTICAL_EXPLORATION = "dialectical_exploration"
    # Orthogonally Maximal Brain Personas
    HUMAN_ERGONOMICS_ARCHITECT = "human_ergonomics_architect"
    DOMAIN_ONTOLOGIST = "domain_ontologist"
    DISTRIBUTED_TOPOLOGY_ARCHITECT = "distributed_topology_architect"
    STATECHART_FSM_ENGINEER = "statechart_fsm_engineer"

    # THE MUSCLE: Gemini 3.8 Flash
    LEAF_CODE_EMISSION = "leaf_code_emission"
    LEAF_SCHEMA_EMISSION = "leaf_schema_emission"
    LEAF_DATA_EMISSION = "leaf_data_emission"
    LEAF_STYLE_EMISSION = "leaf_style_emission"
    # Orthogonally Maximal Muscle Personas
    CORE_ENGINE_SYNTHESIZER = "core_engine_synthesizer"
    OPERATIONAL_DASHBOARD_SYNTHESIZER = "operational_dashboard_synthesizer"
    ADVERSARIAL_QA_ENGINEER = "adversarial_qa_engineer"


class ModelTier(str, Enum):
    """The formal LLM model tiers in System G3b."""
    BRAIN_ARGON = "Gemini 4 Argon"
    MUSCLE_FLASH = "Gemini 3.8 Flash"


class CognitiveRoutingViolation(Exception):
    """Raised when a task is routed to an unapproved model tier violating [L1-G3B-014]."""
    pass


class SubagentExecutionViolation(Exception):
    """Raised when compilation requires live AGY subagents (`invoke_subagent`) but none were spawned."""
    pass


@dataclass
class SubagentExecutionWitness:
    """Cryptographic witness of a subagent invocation (`invoke_subagent`) and its BPE token footprint."""
    task_id: str
    subagent_role: str
    cognitive_role: CognitiveRole
    assigned_model: ModelTier
    conversation_id: str
    prompt_bpe_tokens: int = 0
    response_bpe_tokens: int = 0
    is_live_agy_subagent: bool = True
    task_description: str = ""
    parent_task_id: Optional[str] = None
    caller_role: str = "Meta-Orchestrator (Parent Agent)"
    subagent_type: str = "self"

    @property
    def total_bpe_tokens(self) -> int:
        return self.prompt_bpe_tokens + self.response_bpe_tokens

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "subagent_role": self.subagent_role,
            "cognitive_role": self.cognitive_role.value,
            "assigned_model": self.assigned_model.value,
            "conversation_id": self.conversation_id,
            "prompt_bpe_tokens": self.prompt_bpe_tokens,
            "response_bpe_tokens": self.response_bpe_tokens,
            "total_bpe_tokens": self.total_bpe_tokens,
            "is_live_agy_subagent": self.is_live_agy_subagent,
            "task_description": self.task_description,
            "parent_task_id": self.parent_task_id,
            "caller_role": self.caller_role,
            "subagent_type": self.subagent_type,
        }


@dataclass
class RoutedTaskInvocation:
    """A formal invocation request bound to an invariant-verified model."""
    task_id: str
    role: CognitiveRole
    assigned_model: ModelTier
    payload: Dict[str, Any]
    isolation_depth: int = 0
    is_reprompt: bool = False
    subagent_conversation_id: Optional[str] = None


class DualModelRouter:
    """Strictly partitioned router enforcing [L1-G3B-014]."""

    BRAIN_ROLES: Set[CognitiveRole] = {
        CognitiveRole.ORCHESTRATOR_FSM,
        CognitiveRole.SOC_NORMALIZATION,
        CognitiveRole.MODEL_CHECKER,
        CognitiveRole.JOURNEY_WALKER,
        CognitiveRole.ZERO_TRUST_AUDITOR,
        CognitiveRole.DIALECTICAL_EXPLORATION,
        CognitiveRole.HUMAN_ERGONOMICS_ARCHITECT,
        CognitiveRole.DOMAIN_ONTOLOGIST,
        CognitiveRole.DISTRIBUTED_TOPOLOGY_ARCHITECT,
        CognitiveRole.STATECHART_FSM_ENGINEER,
    }

    MUSCLE_ROLES: Set[CognitiveRole] = {
        CognitiveRole.LEAF_CODE_EMISSION,
        CognitiveRole.LEAF_SCHEMA_EMISSION,
        CognitiveRole.LEAF_DATA_EMISSION,
        CognitiveRole.LEAF_STYLE_EMISSION,
        CognitiveRole.CORE_ENGINE_SYNTHESIZER,
        CognitiveRole.OPERATIONAL_DASHBOARD_SYNTHESIZER,
        CognitiveRole.ADVERSARIAL_QA_ENGINEER,
    }

    # Quota & Model Tier Flag: Default False to prevent Argon quota exhaustion
    ENABLE_ARGON: bool = os.environ.get("META_AXIOMA_ENABLE_ARGON", "false").lower() in ("1", "true", "yes")

    @classmethod
    def set_argon_enabled(cls, enabled: bool) -> None:
        """Configures whether Gemini 4 Argon is enabled or downgraded to Gemini 3.8 Flash."""
        cls.ENABLE_ARGON = enabled

    @classmethod
    def is_argon_enabled(cls) -> bool:
        """Returns True if Gemini 4 Argon is active; False if downgraded to Flash."""
        return cls.ENABLE_ARGON

    @classmethod
    def get_authorized_model(cls, role: CognitiveRole) -> ModelTier:
        """Determines the authorized model for a cognitive role."""
        if role in cls.BRAIN_ROLES:
            if not cls.ENABLE_ARGON:
                return ModelTier.MUSCLE_FLASH
            return ModelTier.BRAIN_ARGON
        if role in cls.MUSCLE_ROLES:
            return ModelTier.MUSCLE_FLASH
        raise CognitiveRoutingViolation(f"Unrecognized cognitive role: {role}")

    @classmethod
    def create_invocation(
        cls,
        task_id: str,
        role: CognitiveRole,
        payload: Dict[str, Any],
        requested_model: Optional[ModelTier] = None,
        is_reprompt: bool = False,
        isolation_depth: int = 0,
        subagent_conversation_id: Optional[str] = None,
    ) -> RoutedTaskInvocation:
        """Validates and constructs an invocation, raising CognitiveRoutingViolation on mismatch."""
        authorized = cls.get_authorized_model(role)
        if not cls.ENABLE_ARGON:
            # When Argon is disabled, Brain roles gracefully accept either MUSCLE_FLASH or BRAIN_ARGON (downgraded to Flash)
            if role in cls.BRAIN_ROLES:
                assigned = ModelTier.MUSCLE_FLASH
            else:
                if requested_model is not None and requested_model != authorized:
                    raise CognitiveRoutingViolation(
                        f"[L1-G3B-014 Violation] Role '{role.value}' is strictly bound to "
                        f"'{authorized.value}', but was invoked with '{requested_model.value}'."
                    )
                assigned = authorized
        else:
            if requested_model is not None and requested_model != authorized:
                raise CognitiveRoutingViolation(
                    f"[L1-G3B-014 Violation] Role '{role.value}' is strictly bound to "
                    f"'{authorized.value}', but was invoked with '{requested_model.value}'."
                )
            assigned = authorized

        return RoutedTaskInvocation(
            task_id=task_id,
            role=role,
            assigned_model=assigned,
            payload=payload,
            isolation_depth=isolation_depth,
            is_reprompt=is_reprompt,
            subagent_conversation_id=subagent_conversation_id,
        )

    @classmethod
    def validate_subagent_witness(cls, witness: SubagentExecutionWitness) -> SubagentExecutionWitness:
        """Verifies that a SubagentExecutionWitness obeys [L1-G3B-014] model routing and has a valid ID."""
        if not cls.ENABLE_ARGON:
            # When Argon is disabled, Brain roles are permitted to have run under Flash or Argon
            if witness.cognitive_role in cls.BRAIN_ROLES:
                allowed_models = {ModelTier.MUSCLE_FLASH, ModelTier.BRAIN_ARGON}
            elif witness.cognitive_role in cls.MUSCLE_ROLES:
                allowed_models = {ModelTier.MUSCLE_FLASH}
            else:
                raise CognitiveRoutingViolation(f"Unrecognized cognitive role: {witness.cognitive_role}")
        else:
            authorized = cls.get_authorized_model(witness.cognitive_role)
            allowed_models = {authorized}

        if witness.assigned_model not in allowed_models:
            raise CognitiveRoutingViolation(
                f"[L1-G3B-014 Violation] Subagent '{witness.subagent_role}' (task '{witness.task_id}') "
                f"executed role '{witness.cognitive_role.value}' under '{witness.assigned_model.value}', "
                f"but is strictly bound to {[m.value for m in allowed_models]}."
            )
        cid = (witness.conversation_id or "").strip().lower()
        if witness.is_live_agy_subagent and (
            not cid
            or cid in ("none", "mock", "in-process", "placeholder")
            or cid.startswith(("mock", "fake", "placeholder", "in-process", "in_process"))
        ):
            raise SubagentExecutionViolation(
                f"Subagent witness for '{witness.task_id}' claims is_live_agy_subagent=True "
                f"but has invalid conversation_id='{witness.conversation_id}'."
            )
        return witness

    @classmethod
    def synthesize_isolated_reprompt(
        cls,
        failed_leaf_task_id: str,
        leaf_role: CognitiveRole,
        defect_report: str,
        prior_payload: Dict[str, Any],
    ) -> RoutedTaskInvocation:
        """Synthesizes an isolated leaf-node re-prompt governed by Argon evaluators."""
        if leaf_role not in cls.MUSCLE_ROLES:
            raise CognitiveRoutingViolation(
                f"Only leaf-node muscle tasks can be isolated re-prompted; got '{leaf_role.value}'."
            )

        updated_payload = dict(prior_payload)
        updated_payload["defect_remediation"] = defect_report
        updated_payload["reprompt_governor"] = (
            ModelTier.BRAIN_ARGON.value if cls.ENABLE_ARGON else ModelTier.MUSCLE_FLASH.value
        )

        return cls.create_invocation(
            task_id=f"{failed_leaf_task_id}:reprompt",
            role=leaf_role,
            payload=updated_payload,
            requested_model=ModelTier.MUSCLE_FLASH,
            is_reprompt=True,
            isolation_depth=prior_payload.get("isolation_depth", 0) + 1,
        )
