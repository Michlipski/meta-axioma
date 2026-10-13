"""Kinetic Chaining & Semantic Momentum Propagation [L1-G2-007].

Exogenous Domain: Biomechanics, Movement Kinesiology & Dance (Kinetic Chains).
Biomechanics Principle:
    Force and momentum generated in the core propagate through sequential
    articulated segments to the distal extremities. Rigid joints leak energy and cause
    mechanical breakdown; elastic, compliant articulation preserves kinetic momentum.

Systems Formalization:
    Semantic Momentum: p_semantic = M_core · v_intent
    Joint Articulation: J_joint : CoreAST -> SubstrateAdapter
    Conservation Condition:
        ∮_{∂Substrate} (p_semantic - J_joint · q_dot) dt = 0
    Ensures that intent generated at the core AST propagates flawlessly to distal
    substrates (Terminal CLI, Background Daemon, Web HUD) without brittle coupling
    or syntactical impedance leakage.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import copy
import hashlib
import json
import time

from g2_compiler.types import IntentAST, SubstrateAST, SubstrateType


class JointFlexibility(str, Enum):
    """Compliance tier of the translation joint."""
    RIGID = "RIGID"          # Brittle: forces strict syntax, leaks under variance
    COMPLIANT = "COMPLIANT"  # Elastic: preserves momentum with adaptive impedance
    DAMPENED = "DAMPENED"    # Absorptive: filters high-frequency noise


@dataclass
class KineticMomentumVector:
    """The momentum carried from the core intent into substrate execution."""
    intent_id: str
    action: str
    target_noun: str
    mass_complexity: float      # Number of parameters + constraints
    velocity_urgency: float     # Execution priority
    magnitude: float            # mass * velocity
    invariants: List[str]


@dataclass
class KineticJointAudit:
    """Measures momentum preservation across an articulated substrate boundary."""
    substrate: SubstrateType
    input_momentum: float
    output_momentum: float
    impedance_loss: float       # Energy dissipated at the joint
    momentum_retained_ratio: float
    is_compliant: bool
    rejection_reasons: List[str] = field(default_factory=list)


class CompliantKineticJoint:
    """Articulated joint adapter translating core AST momentum into a specific substrate extremity."""

    def __init__(
        self,
        substrate: SubstrateType,
        flexibility: JointFlexibility = JointFlexibility.COMPLIANT,
        max_impedance_loss: float = 0.05,
    ):
        self.substrate = substrate
        self.flexibility = flexibility
        self.max_impedance_loss = max_impedance_loss

    def propagate_momentum(
        self, momentum: KineticMomentumVector, intent: IntentAST
    ) -> Tuple[SubstrateAST, KineticJointAudit]:
        """Propagates semantic momentum through the joint without rigid syntactic friction."""
        # Calculate joint impedance
        if self.flexibility == JointFlexibility.RIGID:
            # Rigid joints leak energy when dealing with diverse parameter shapes
            impedance_loss = 0.15 * momentum.mass_complexity
        else:
            # Compliant joints match impedance dynamically
            impedance_loss = 0.01 * min(momentum.mass_complexity, 3.0)

        output_momentum = max(0.0, momentum.magnitude - impedance_loss)
        retention_ratio = output_momentum / max(momentum.magnitude, 1e-6)

        rejection_reasons = []
        if impedance_loss > self.max_impedance_loss:
            rejection_reasons.append(
                f"Joint impedance loss {impedance_loss:.3f} exceeds threshold {self.max_impedance_loss:.3f}."
            )

        # Emit substrate extremity representation
        payload: Dict[str, Any] = {
            "action": intent.action,
            "noun": intent.target_noun,
            "params": copy.deepcopy(intent.parameters),
            "momentum_magnitude": output_momentum,
            "substrate": self.substrate.value,
        }

        if self.substrate == SubstrateType.CLI:
            code = f"sentinel-cli {intent.action} --noun {intent.target_noun} --momentum {output_momentum:.2f}"
        elif self.substrate == SubstrateType.EMBEDDED_EDGE:
            code = f"sentinel_daemon_dispatch(\"{intent.action}\", momentum={output_momentum:.2f});"
        elif self.substrate == SubstrateType.WEB_PWA:
            code = f"window.Sentinel.dispatch('{intent.action}', {{ momentum: {output_momentum:.2f} }});"
        else:
            code = f"rpc_call('{intent.action}', {json.dumps(intent.parameters)});"

        substrate_ast = SubstrateAST(
            substrate=self.substrate,
            payload=payload,
            executable_code=code,
            metadata={"origin_intent_id": intent.intent_id, "joint_flexibility": self.flexibility.value},
        )

        audit = KineticJointAudit(
            substrate=self.substrate,
            input_momentum=momentum.magnitude,
            output_momentum=output_momentum,
            impedance_loss=impedance_loss,
            momentum_retained_ratio=retention_ratio,
            is_compliant=(len(rejection_reasons) == 0),
            rejection_reasons=rejection_reasons,
        )

        return substrate_ast, audit


class KineticChainCompiler:
    """Propagates core semantic momentum across all articulated substrate extremities."""

    def __init__(self):
        self.joints: Dict[SubstrateType, CompliantKineticJoint] = {
            SubstrateType.CLI: CompliantKineticJoint(SubstrateType.CLI),
            SubstrateType.EMBEDDED_EDGE: CompliantKineticJoint(SubstrateType.EMBEDDED_EDGE),
            SubstrateType.WEB_PWA: CompliantKineticJoint(SubstrateType.WEB_PWA),
            SubstrateType.MICROSERVICE: CompliantKineticJoint(SubstrateType.MICROSERVICE),
        }

    def compute_core_momentum(self, intent: IntentAST) -> KineticMomentumVector:
        """Derives the semantic momentum vector generated by the core intent."""
        # Mass = syntactic volume of parameters and constraints
        mass = 1.0 + len(intent.parameters) * 0.2 + len(intent.constraints) * 0.3
        # Velocity = action urgency
        velocity = 1.5 if "rollback" in intent.action or "emergency" in intent.action else 1.0
        magnitude = mass * velocity

        return KineticMomentumVector(
            intent_id=intent.intent_id,
            action=intent.action,
            target_noun=intent.target_noun,
            mass_complexity=mass,
            velocity_urgency=velocity,
            magnitude=magnitude,
            invariants=list(intent.constraints),
        )

    def propagate_to_extremities(
        self, intent: IntentAST, target_substrates: Optional[List[SubstrateType]] = None
    ) -> Tuple[Dict[SubstrateType, SubstrateAST], List[KineticJointAudit]]:
        """Chains momentum from core AST to all requested extremities."""
        if target_substrates is None:
            target_substrates = list(self.joints.keys())

        momentum = self.compute_core_momentum(intent)
        results: Dict[SubstrateType, SubstrateAST] = {}
        audits: List[KineticJointAudit] = []

        for sub in target_substrates:
            joint = self.joints[sub]
            sub_ast, audit = joint.propagate_momentum(momentum, intent)
            results[sub] = sub_ast
            audits.append(audit)

        return results, audits
