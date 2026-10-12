"""Landauer Thermodynamic Reversibility & Erasure Dissipation Accounting ([L1-008]).

Formal Expression:
    ΔQ ≥ k_B T ln 2 · ΔH_erasure ⟹ Isomorphic(Kernel)

Operational Rule:
    State mutations discarding intermediate histories without explicit dissipation
    audit channels or reversible inverse paths trigger compiler failure.
"""

from dataclasses import dataclass, field
import hashlib
import json
import math
from typing import Any, Dict, List, Optional
import time

# Physical constants at T = 300 Kelvin
BOLTZMANN_CONSTANT = 1.380649e-23  # J/K
TEMPERATURE_KELVIN = 300.0         # Room temperature K
LANDAUER_LIMIT_PER_BIT = BOLTZMANN_CONSTANT * TEMPERATURE_KELVIN * math.log(2)  # ≈ 2.87e-21 J


@dataclass
class DissipationAuditRecord:
    """Formal audit witness for lossy computational transformations."""
    operation_id: str
    erased_bits: float
    dissipated_energy_joules: float
    is_reversible: bool
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    witness_hash: str = ""

    def __post_init__(self):
        if not self.witness_hash:
            data = {
                "op": self.operation_id,
                "bits": self.erased_bits,
                "joules": self.dissipated_energy_joules,
                "rev": self.is_reversible,
                "time": self.timestamp,
            }
            raw = json.dumps(data, sort_keys=True)
            self.witness_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()


class LandauerAccountingLedger:
    """Canonical ledger tracking computational entropy and Landauer dissipation."""

    def __init__(self):
        self.records: List[DissipationAuditRecord] = []
        self.total_erased_bits: float = 0.0
        self.total_dissipated_joules: float = 0.0

    def record_operation(
        self,
        operation_id: str,
        erased_bits: float,
        is_reversible: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ) -> DissipationAuditRecord:
        """Records an operation and computes thermodynamic dissipation."""
        bits = 0.0 if is_reversible else max(0.0, erased_bits)
        joules = bits * LANDAUER_LIMIT_PER_BIT

        record = DissipationAuditRecord(
            operation_id=operation_id,
            erased_bits=bits,
            dissipated_energy_joules=joules,
            is_reversible=is_reversible,
            context=context or {},
        )
        self.records.append(record)
        self.total_erased_bits += bits
        self.total_dissipated_joules += joules
        return record

    def get_summary(self) -> Dict[str, Any]:
        """Returns cumulative thermodynamic telemetry."""
        return {
            "total_operations": len(self.records),
            "reversible_operations": sum(1 for r in self.records if r.is_reversible),
            "lossy_operations": sum(1 for r in self.records if not r.is_reversible),
            "total_erased_bits": self.total_erased_bits,
            "total_dissipated_joules": self.total_dissipated_joules,
            "landauer_limit_joules_per_bit": LANDAUER_LIMIT_PER_BIT,
        }


class ThermodynamicReversibilityAuditor:
    """Enforces Landauer reversibility invariants and audit compliance."""

    def __init__(self, ledger: Optional[LandauerAccountingLedger] = None):
        self.ledger = ledger or LandauerAccountingLedger()

    def audit_transformation(
        self,
        name: str,
        is_reversible: bool,
        erased_bits: float,
        has_audit_channel: bool = True,
    ) -> DissipationAuditRecord:
        """Audits a transformation: lossy operations must have an audit channel."""
        if not is_reversible and not has_audit_channel:
            raise PermissionError(
                f"Landauer Thermodynamic Invariant Violation [L1-008]: Operation '{name}' "
                f"erases {erased_bits} bits without an explicit dissipation audit channel or inverse path."
            )
        return self.ledger.record_operation(
            operation_id=name,
            erased_bits=erased_bits,
            is_reversible=is_reversible,
        )
