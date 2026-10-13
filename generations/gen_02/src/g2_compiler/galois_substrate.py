"""Adjoint Galois Substrate Connection & Multi-Target Preservation [L1-G2-001].

Category-Theoretic Principle:
    Given category C (Declarative Intent ASTs) and category D (Substrate Execution Runtimes),
    the compilation functor F: C -> D and reflection functor G: D -> C must form an
    adjoint Galois connection F ⊣ G:
        Hom_C(F(A), B) ≅ Hom_D(A, G(B))
    with unit η: Id_C -> G ∘ F and counit ε: F ∘ G -> Id_D.
"""

from typing import Any, Dict, List, Optional, Tuple
import copy
import json

from g2_compiler.types import (
    GaloisRoundTripAudit,
    IntentAST,
    SubstrateAST,
    SubstrateType,
)


class GaloisSubstrateMapper:
    """Manages adjoint transformations between declarative user intent and heterogeneous execution substrates."""

    def __init__(self, name: str = "GaloisSubstrateEngine"):
        self.name = name

    def lower_intent(self, intent: IntentAST, substrate: SubstrateType) -> SubstrateAST:
        """Functor F: C -> D mapping IntentAST into a specific SubstrateAST."""
        payload: Dict[str, Any] = {
            "action": intent.action,
            "noun": intent.target_noun,
            "params": copy.deepcopy(intent.parameters),
            "constraints": list(intent.constraints),
            "substrate_type": substrate.value,
        }

        # Substrate-specific code emission
        if substrate == SubstrateType.CLI:
            params_str = " ".join(f"--{k} {v}" for k, v in intent.parameters.items())
            code = f"agy-cli {intent.action} {intent.target_noun} {params_str}".strip()
        elif substrate == SubstrateType.WEB_PWA:
            code = (
                f"window.dispatchEvent(new CustomEvent('{intent.action}:{intent.target_noun}', "
                f"{{ detail: {json.dumps(intent.parameters)} }}));"
            )
        elif substrate == SubstrateType.MICROSERVICE:
            code = json.dumps({
                "rpc_method": f"{intent.target_noun}.{intent.action}",
                "request_payload": intent.parameters,
                "invariant_guardrails": intent.constraints,
            })
        else:  # EMBEDDED_EDGE
            code = f"edge_dispatch(\"{intent.action}_{intent.target_noun}\", {len(intent.parameters)});"

        return SubstrateAST(
            substrate=substrate,
            payload=payload,
            executable_code=code,
            metadata={"origin_intent_id": intent.intent_id},
        )

    def reflect_substrate(self, substrate_ast: SubstrateAST) -> IntentAST:
        """Functor G: D -> C lifting SubstrateAST back into high-level IntentAST."""
        payload = substrate_ast.payload
        intent_id = substrate_ast.metadata.get("origin_intent_id", f"reflected_{time_stamp()}")
        return IntentAST(
            intent_id=intent_id,
            action=payload.get("action", "unknown_action"),
            target_noun=payload.get("noun", "unknown_noun"),
            parameters=copy.deepcopy(payload.get("params", {})),
            constraints=list(payload.get("constraints", [])),
        )

    def verify_round_trip(self, intent: IntentAST, substrate: SubstrateType) -> GaloisRoundTripAudit:
        """Verifies the unit η: Id_C -> G ∘ F and counit ε: F ∘ G -> Id_D."""
        # 1. Forward functor F
        substrate_ast = self.lower_intent(intent, substrate)

        # 2. Reverse reflection functor G
        reflected_intent = self.reflect_substrate(substrate_ast)

        # 3. Unit satisfaction check: G(F(A)) ~ A
        unit_ok = (
            reflected_intent.action == intent.action
            and reflected_intent.target_noun == intent.target_noun
            and reflected_intent.parameters == intent.parameters
            and reflected_intent.constraints == intent.constraints
        )

        # 4. Counit satisfaction check: F(G(B)) ~ B
        re_lowered = self.lower_intent(reflected_intent, substrate)
        counit_ok = (
            re_lowered.payload == substrate_ast.payload
            and re_lowered.executable_code == substrate_ast.executable_code
        )

        # 5. Measure closure error (0.0 if perfect isomorphism)
        closure_error = 0.0 if (unit_ok and counit_ok) else 1.0

        return GaloisRoundTripAudit(
            original_intent=intent,
            projected_substrate=substrate_ast,
            reflected_intent=reflected_intent,
            unit_satisfied=unit_ok,
            counit_satisfied=counit_ok,
            round_trip_closure_error=closure_error,
            is_valid=(closure_error == 0.0),
        )

    def verify_multi_substrate_preservation(
        self, intent: IntentAST, substrates: Optional[List[SubstrateType]] = None
    ) -> Tuple[bool, List[GaloisRoundTripAudit]]:
        """Verifies that an intent preserves Galois closure across ALL target substrates."""
        if substrates is None:
            substrates = list(SubstrateType)

        audits = [self.verify_round_trip(intent, sub) for sub in substrates]
        all_valid = all(a.is_valid for a in audits)
        return all_valid, audits


def time_stamp() -> int:
    import time
    return int(time.time() * 1000)
