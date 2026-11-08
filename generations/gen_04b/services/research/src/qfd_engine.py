"""Generation 4b Quality Function Deployment (QFD) House of Quality Engine.

Enforces:
- [SPEC-G4B-RESEARCH-QFD-001]: Rigorous derivation of engineering characteristics from customer JTBDs.
- [L1-G4B-001]: Decoupled Research Sovereignty.
- [L1-G4B-002]: Zero-Code Research Boundary.
- [L1-G4B-003]: Cryptographic Merkle-DAG Telemetry.
- Mitigation for VULN-QFD-003: Substrate invariants are exempt from relevance threshold elimination.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
import hashlib
import json
import time
from typing import Any, Dict, List, Optional

from .domain_models import DomainInvariantViolation


class CharacteristicType(str, Enum):
    """Classification of engineering characteristic [VULN-QFD-003]."""
    USER_FACING_JTBD = "USER_FACING_JTBD"
    SUBSTRATE_INVARIANT = "SUBSTRATE_INVARIANT"


class OptimizationDirection(str, Enum):
    """Direction of optimization for an engineering characteristic."""
    MAXIMIZE = "MAXIMIZE"
    MINIMIZE = "MINIMIZE"
    TARGET = "TARGET"


class CorrelationType(IntEnum):
    """Roof correlation strength between engineering characteristics."""
    STRONG_POSITIVE = 2
    POSITIVE = 1
    NONE = 0
    NEGATIVE = -1
    STRONG_NEGATIVE = -2


class RelationshipStrength(IntEnum):
    """Standard House of Quality relationship scoring."""
    NONE = 0
    WEAK = 1
    MEDIUM = 3
    STRONG = 9


@dataclass
class CustomerRequirement:
    """Customer requirement representing a user-facing JTBD or friction pain point."""
    req_id: str
    description: str
    weight: float  # In range (0.0, 1.0]
    frictions_addressed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "req_id": self.req_id,
            "description": self.description,
            "weight": self.weight,
            "frictions_addressed": list(self.frictions_addressed),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CustomerRequirement:
        return cls(
            req_id=str(data["req_id"]),
            description=str(data.get("description", "")),
            weight=float(data.get("weight", 1.0)),
            frictions_addressed=list(data.get("frictions_addressed", [])),
        )


@dataclass
class EngineeringCharacteristic:
    """Measurable engineering characteristic in the House of Quality."""
    char_id: str
    name: str
    char_type: CharacteristicType
    direction: OptimizationDirection
    unit: str
    target_value: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "char_id": self.char_id,
            "name": self.name,
            "char_type": self.char_type.value if isinstance(self.char_type, Enum) else str(self.char_type),
            "direction": self.direction.value if isinstance(self.direction, Enum) else str(self.direction),
            "unit": self.unit,
            "target_value": self.target_value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EngineeringCharacteristic:
        raw_type = data.get("char_type", CharacteristicType.USER_FACING_JTBD.value)
        char_type = CharacteristicType(raw_type) if isinstance(raw_type, str) else raw_type
        raw_dir = data.get("direction", OptimizationDirection.MAXIMIZE.value)
        direction = OptimizationDirection(raw_dir) if isinstance(raw_dir, str) else raw_dir
        return cls(
            char_id=str(data["char_id"]),
            name=str(data.get("name", "")),
            char_type=char_type,
            direction=direction,
            unit=str(data.get("unit", "")),
            target_value=float(data.get("target_value", 0.0)),
        )


@dataclass
class CorrelationRoofEdge:
    """Roof correlation edge between two engineering characteristics."""
    char_id_a: str
    char_id_b: str
    correlation: CorrelationType
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "char_id_a": self.char_id_a,
            "char_id_b": self.char_id_b,
            "correlation": self.correlation.value if isinstance(self.correlation, Enum) else int(self.correlation),
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CorrelationRoofEdge:
        raw_corr = data.get("correlation", 0)
        corr = CorrelationType(raw_corr) if isinstance(raw_corr, int) else CorrelationType[str(raw_corr)]
        return cls(
            char_id_a=str(data["char_id_a"]),
            char_id_b=str(data["char_id_b"]),
            correlation=corr,
            rationale=str(data.get("rationale", "")),
        )


@dataclass
class HouseOfQualityIR:
    """Intermediate Representation (IR) for a sealed House of Quality (QFD) matrix."""
    matrix_id: str
    target_soc_id: str
    requirements: List[CustomerRequirement]
    characteristics: List[EngineeringCharacteristic]
    relationship_tensor: Dict[str, Dict[str, RelationshipStrength]]
    roof_edges: List[CorrelationRoofEdge]
    technical_importance: Dict[str, float]
    normalized_importance: Dict[str, float]
    included_characteristics: List[str]
    cut_characteristics: List[str]
    merkle_root: str = ""
    timestamp_unix_ms: int = 0
    is_sealed: bool = False

    def validate_invariants(self) -> None:
        """Validates all formal structural invariants of the House of Quality IR."""
        if not self.matrix_id or not self.matrix_id.strip():
            raise DomainInvariantViolation("HouseOfQualityIR matrix_id must be non-empty")
        if not self.target_soc_id or not self.target_soc_id.strip():
            raise DomainInvariantViolation("HouseOfQualityIR target_soc_id must be non-empty")
        if not self.requirements:
            raise DomainInvariantViolation("HouseOfQualityIR requirements must be non-empty")
        for req in self.requirements:
            if not req.req_id or not req.req_id.strip():
                raise DomainInvariantViolation("CustomerRequirement req_id must be non-empty")
            if not (0.0 < req.weight <= 1.0):
                raise DomainInvariantViolation(
                    f"CustomerRequirement {req.req_id} weight {req.weight} must be in (0, 1]"
                )
        if not self.characteristics:
            raise DomainInvariantViolation("HouseOfQualityIR characteristics must be non-empty")
        char_ids = set()
        for char in self.characteristics:
            if not char.char_id or not char.char_id.strip():
                raise DomainInvariantViolation("EngineeringCharacteristic char_id must be non-empty")
            if char.char_id in char_ids:
                raise DomainInvariantViolation(f"Duplicate EngineeringCharacteristic char_id: {char.char_id}")
            char_ids.add(char.char_id)
        for edge in self.roof_edges:
            if edge.char_id_a not in char_ids or edge.char_id_b not in char_ids:
                raise DomainInvariantViolation(
                    f"CorrelationRoofEdge references unknown char_id: {edge.char_id_a} or {edge.char_id_b}"
                )
            if edge.char_id_a == edge.char_id_b:
                raise DomainInvariantViolation(
                    f"CorrelationRoofEdge cannot link characteristic to itself: {edge.char_id_a}"
                )
        if self.is_sealed:
            if not self.merkle_root or len(self.merkle_root) < 32:
                raise DomainInvariantViolation("Sealed HouseOfQualityIR must have valid merkle_root digest")
            if self.timestamp_unix_ms <= 0:
                raise DomainInvariantViolation("Sealed HouseOfQualityIR must have positive timestamp_unix_ms")

    def to_dict(self) -> Dict[str, Any]:
        serialized_tensor: Dict[str, Dict[str, int]] = {}
        for req_id, char_map in self.relationship_tensor.items():
            serialized_tensor[req_id] = {}
            for char_id, strength in char_map.items():
                val = strength.value if isinstance(strength, Enum) else int(strength)
                serialized_tensor[req_id][char_id] = val

        return {
            "matrix_id": self.matrix_id,
            "target_soc_id": self.target_soc_id,
            "requirements": [r.to_dict() for r in self.requirements],
            "characteristics": [c.to_dict() for c in self.characteristics],
            "relationship_tensor": serialized_tensor,
            "roof_edges": [e.to_dict() for e in self.roof_edges],
            "technical_importance": dict(self.technical_importance),
            "normalized_importance": dict(self.normalized_importance),
            "included_characteristics": list(self.included_characteristics),
            "cut_characteristics": list(self.cut_characteristics),
            "merkle_root": self.merkle_root,
            "timestamp_unix_ms": self.timestamp_unix_ms,
            "is_sealed": self.is_sealed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HouseOfQualityIR:
        reqs = [CustomerRequirement.from_dict(r) for r in data.get("requirements", [])]
        chars = [EngineeringCharacteristic.from_dict(c) for c in data.get("characteristics", [])]
        roofs = [CorrelationRoofEdge.from_dict(e) for e in data.get("roof_edges", [])]

        raw_tensor = data.get("relationship_tensor", {})
        restored_tensor: Dict[str, Dict[str, RelationshipStrength]] = {}
        for req_id, char_map in raw_tensor.items():
            restored_tensor[req_id] = {}
            for char_id, val in char_map.items():
                strength = RelationshipStrength(val) if isinstance(val, int) else RelationshipStrength[str(val)]
                restored_tensor[req_id][char_id] = strength

        instance = cls(
            matrix_id=str(data["matrix_id"]),
            target_soc_id=str(data["target_soc_id"]),
            requirements=reqs,
            characteristics=chars,
            relationship_tensor=restored_tensor,
            roof_edges=roofs,
            technical_importance={k: float(v) for k, v in data.get("technical_importance", {}).items()},
            normalized_importance={k: float(v) for k, v in data.get("normalized_importance", {}).items()},
            included_characteristics=list(data.get("included_characteristics", [])),
            cut_characteristics=list(data.get("cut_characteristics", [])),
            merkle_root=str(data.get("merkle_root", "")),
            timestamp_unix_ms=int(data.get("timestamp_unix_ms", 0)),
            is_sealed=bool(data.get("is_sealed", False)),
        )
        return instance


class QFDEngine:
    """Quality Function Deployment (QFD) House of Quality Engine.

    Enforces:
    - [SPEC-G4B-RESEARCH-QFD-001]: Rigorous derivation of engineering characteristics from customer JTBDs.
    - [L1-G4B-001], [L1-G4B-002]: Zero-code research contract synthesis.
    - [L1-G4B-003]: Cryptographic Merkle-DAG telemetry anchoring.
    - Mitigation for VULN-QFD-003: Substrate invariants are exempt from relevance threshold elimination.
    """

    def __init__(self, relevance_threshold: float = 0.35):
        self.relevance_threshold = relevance_threshold

    def create_house_of_quality(
        self,
        matrix_id: str,
        target_soc_id: str,
        requirements: List[CustomerRequirement],
        characteristics: List[EngineeringCharacteristic],
        relationship_tensor: Dict[str, Dict[str, RelationshipStrength]],
        roof_edges: Optional[List[CorrelationRoofEdge]] = None,
    ) -> HouseOfQualityIR:
        """Constructs and calculates a House of Quality matrix."""
        edges = list(roof_edges or [])

        # 1. Compute technical importance T_j = sum_i (W_i * R_ij)
        tech_importance: Dict[str, float] = {}
        for char in characteristics:
            t_j = 0.0
            for req in requirements:
                w_i = req.weight
                rel = relationship_tensor.get(req.req_id, {}).get(char.char_id, RelationshipStrength.NONE)
                r_val = rel.value if isinstance(rel, Enum) else int(rel)
                t_j += w_i * float(r_val)
            tech_importance[char.char_id] = round(t_j, 4)

        # 2. Compute normalized importance \bar{T}_j = T_j / max(T_k)
        max_t = max(tech_importance.values()) if tech_importance else 0.0
        norm_importance: Dict[str, float] = {}
        for char_id, t_val in tech_importance.items():
            if max_t > 0.0:
                norm_importance[char_id] = round(t_val / max_t, 4)
            else:
                norm_importance[char_id] = 0.0

        # 3. Partition characteristics into included vs cut
        # Invariant [VULN-QFD-003]: SUBSTRATE_INVARIANT characteristics are ALWAYS included regardless of threshold
        included: List[str] = []
        cut: List[str] = []
        for char in characteristics:
            val = norm_importance.get(char.char_id, 0.0)
            if val >= self.relevance_threshold or char.char_type == CharacteristicType.SUBSTRATE_INVARIANT:
                included.append(char.char_id)
            else:
                cut.append(char.char_id)

        hoq = HouseOfQualityIR(
            matrix_id=matrix_id,
            target_soc_id=target_soc_id,
            requirements=requirements,
            characteristics=characteristics,
            relationship_tensor=relationship_tensor,
            roof_edges=edges,
            technical_importance=tech_importance,
            normalized_importance=norm_importance,
            included_characteristics=included,
            cut_characteristics=cut,
            merkle_root="",
            timestamp_unix_ms=0,
            is_sealed=False,
        )
        hoq.validate_invariants()
        return hoq

    def extract_negative_roof_contradictions(
        self,
        hoq: HouseOfQualityIR,
    ) -> List[CorrelationRoofEdge]:
        """Filters roof correlation edges where correlation is negative or strong negative."""
        return [
            edge for edge in hoq.roof_edges
            if edge.correlation in (CorrelationType.NEGATIVE, CorrelationType.STRONG_NEGATIVE)
        ]

    def seal_qfd_matrix(
        self,
        hoq: HouseOfQualityIR,
        merkle_engine: Optional[Any] = None,
    ) -> str:
        """Seals the House of Quality with SHA-256 Merkle root digest and records timestamp."""
        if hoq.timestamp_unix_ms <= 0:
            hoq.timestamp_unix_ms = int(time.time() * 1000)

        # Generate deterministic canonical JSON over the matrix payload
        payload = hoq.to_dict()
        # Compute digest over content excluding merkle_root and is_sealed
        hash_payload = {k: v for k, v in payload.items() if k not in ("merkle_root", "is_sealed")}
        canonical_bytes = json.dumps(hash_payload, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(canonical_bytes).hexdigest()

        hoq.merkle_root = digest
        hoq.is_sealed = True

        if merkle_engine is not None and hasattr(merkle_engine, "record_witness"):
            merkle_engine.record_witness(
                task_id=f"qfd_{hoq.matrix_id}",
                actor_id="soc_g4b_researcher",
                payload_data={
                    "qfd_merkle_root": digest,
                    "matrix_id": hoq.matrix_id,
                    "target_soc_id": hoq.target_soc_id,
                    "timestamp_unix_ms": hoq.timestamp_unix_ms,
                    "included_count": len(hoq.included_characteristics),
                    "cut_count": len(hoq.cut_characteristics),
                },
            )

        return digest
