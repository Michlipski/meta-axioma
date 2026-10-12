"""Functorial State Evolution and Morphism Preservation ([L1-002]).

Formal Expression:
    F(f ∘ g) = F(f) ∘ F(g)  ∧  F(id_A) = id_{F(A)}

Guarantees that component composition in the problem domain is preserved under
compilation into execution morphisms without non-compositional side effects.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar
import copy

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


@dataclass
class Morphism(Generic[T, U]):
    """A structure-preserving morphism between domain states."""
    name: str
    source_type: str
    target_type: str
    transform: Callable[[T], U]
    inverse: Optional[Callable[[U], T]] = None
    erasure_bits: float = 0.0

    def apply(self, x: T) -> U:
        """Applies the morphism transformation."""
        return self.transform(x)

    def is_reversible(self) -> bool:
        """Returns True if this morphism provides an explicit inverse transformation."""
        return self.inverse is not None

    def invert(self, y: U) -> Optional[T]:
        """Applies inverse transformation if defined."""
        if self.inverse is not None:
            return self.inverse(y)
        return None

    def compose(self, before: "Morphism[V, T]") -> "Morphism[V, U]":
        """Composes this morphism with a preceding morphism: (self ∘ before)(x) = self(before(x))."""
        if before.target_type != self.source_type:
            raise TypeError(
                f"Functorial Composition Mismatch: Cannot compose '{self.name}' (expects {self.source_type}) "
                f"with '{before.name}' (produces {before.target_type})."
            )

        def composed_transform(x: V) -> U:
            intermediate = before.apply(x)
            return self.apply(intermediate)

        composed_inverse: Optional[Callable[[U], V]] = None
        if self.is_reversible() and before.is_reversible():
            composed_inverse = lambda u: before.invert(self.invert(u))  # type: ignore

        return Morphism(
            name=f"({self.name} ∘ {before.name})",
            source_type=before.source_type,
            target_type=self.target_type,
            transform=composed_transform,
            inverse=composed_inverse,
            erasure_bits=before.erasure_bits + self.erasure_bits,
        )


class CategoryFunctor:
    """Functor F: Cat_A -> Cat_B mapping objects and morphisms while preserving structure."""

    def __init__(self, name: str):
        self.name = name

    def map_object(self, obj: Any) -> Any:
        """Maps an object from source category to target category."""
        return copy.deepcopy(obj)

    def map_morphism(self, morphism: Morphism) -> Morphism:
        """Lifts a morphism into the target category."""
        def lifted_transform(x: Any) -> Any:
            mapped_input = self.map_object(x)
            result = morphism.apply(mapped_input)
            return self.map_object(result)

        lifted_inverse = None
        if morphism.is_reversible():
            def lifted_inverse_func(y: Any) -> Any:
                mapped_y = self.map_object(y)
                inverted = morphism.invert(mapped_y)
                return self.map_object(inverted)
            lifted_inverse = lifted_inverse_func

        return Morphism(
            name=f"{self.name}({morphism.name})",
            source_type=morphism.source_type,
            target_type=morphism.target_type,
            transform=lifted_transform,
            inverse=lifted_inverse,
            erasure_bits=morphism.erasure_bits,
        )

    def verify_functor_laws(self, sample_input: Any, m1: Morphism, m2: Morphism) -> Dict[str, bool]:
        """Formally verifies identity and composition preservation laws for given sample input.

        Law 1: F(id) = id
        Law 2: F(m2 ∘ m1) = F(m2) ∘ F(m1)
        """
        # Identity morphism
        id_morphism = Morphism(
            name="id",
            source_type=m1.source_type,
            target_type=m1.source_type,
            transform=lambda x: x,
        )
        lifted_id = self.map_morphism(id_morphism)
        id_preservation = lifted_id.apply(sample_input) == sample_input

        # Composition law
        direct_composed = m2.compose(m1)
        lifted_direct_composed = self.map_morphism(direct_composed)

        lifted_m1 = self.map_morphism(m1)
        lifted_m2 = self.map_morphism(m2)
        lifted_composed = lifted_m2.compose(lifted_m1)

        val_a = lifted_direct_composed.apply(sample_input)
        val_b = lifted_composed.apply(sample_input)
        composition_preservation = (val_a == val_b)

        return {
            "identity_preserved": bool(id_preservation),
            "composition_preserved": bool(composition_preservation),
            "functor_law_satisfied": bool(id_preservation and composition_preservation),
        }


class FunctorialPipeline:
    """Manages sequential execution of morphisms over system state."""

    def __init__(self, name: str = "G1_Execution_Pipeline"):
        self.name = name
        self.morphisms: List[Morphism] = []
        self.functor = CategoryFunctor(name=f"F_{name}")

    def add_step(self, morphism: Morphism) -> None:
        """Appends a morphism to the pipeline with type checking."""
        if self.morphisms:
            last = self.morphisms[-1]
            if last.target_type != morphism.source_type:
                raise TypeError(
                    f"Type alignment failure in pipeline '{self.name}': "
                    f"Step '{last.name}' output ({last.target_type}) does not match "
                    f"Step '{morphism.name}' input ({morphism.source_type})."
                )
        self.morphisms.append(morphism)

    def execute(self, initial_state: Any) -> Any:
        """Executes pipeline morphisms in order."""
        state = initial_state
        for m in self.morphisms:
            lifted = self.functor.map_morphism(m)
            state = lifted.apply(state)
        return state

    def compose_all(self) -> Optional[Morphism]:
        """Folds all pipeline morphisms into a single composite morphism."""
        if not self.morphisms:
            return None
        composed = self.morphisms[0]
        for m in self.morphisms[1:]:
            composed = m.compose(composed)
        return composed
