"""Landauer Thermodynamic Accounting & Dissipation Engine (`soc_g4b_telemetry`).

Enforces:
- Invariant [L1-G3B-018]: Thermodynamic Capital & Landauer Heat Dissipation.
  Formula: Q = k_B * T * ln(2) * bits at T = 300K.
- Strict 60/40 Thermodynamic Capital Partition:
  Total Lease Budget:     880,300 BPE tokens (Option C Sovereign Telemetry).
  Exploratory Capital:    528,180 BPE tokens (60% lease ceiling).
  Protected Capital:      352,120 BPE tokens (40% verification floor).
- Pure adjoint functorial bit recovery for reversible computational paths.
"""

from __future__ import annotations

import copy
import math
import time
from typing import Any, Dict, List, Optional

from .domain_models import (
    LandauerDissipationLedger,
    TelemetryDomainInvariantViolation,
)


class LandauerThermodynamicEngine:
    """Manages Landauer thermodynamic heat calculation, bit erasure, and 60/40 token capital."""

    # Fundamental Physical Constants
    BOLTZMANN_K: float = 1.380649e-23  # Joules / Kelvin
    LN_2: float = 0.6931471805599453   # ln(2)
    DEFAULT_TEMP_KELVIN: float = 300.0  # Standard room temperature

    # Option C Sovereign Telemetry Capital Budget
    DEFAULT_LEASE_BUDGET: int = 880300
    DEFAULT_EXPLORATORY_CAPITAL: int = 528180  # 60%
    DEFAULT_PROTECTED_CAPITAL: int = 352120    # 40%

    def __init__(
        self,
        token_lease_budget: int = DEFAULT_LEASE_BUDGET,
        temp_kelvin: float = DEFAULT_TEMP_KELVIN,
    ) -> None:
        if token_lease_budget <= 0:
            raise TelemetryDomainInvariantViolation("token_lease_budget must be positive.")
        if temp_kelvin <= 0:
            raise TelemetryDomainInvariantViolation("temp_kelvin must be positive.")

        exploratory = int(token_lease_budget * 0.60)
        protected = token_lease_budget - exploratory

        self.temp_kelvin = temp_kelvin
        self.ledger = LandauerDissipationLedger(
            ledger_id="ledger_g4b_telemetry_thermodynamics",
            token_lease_budget=token_lease_budget,
            exploratory_capital=exploratory,
            protected_capital=protected,
        )
        self.ledger.validate_invariants()

        self._erasure_events: List[Dict[str, Any]] = []
        self._recovery_events: List[Dict[str, Any]] = []

    @classmethod
    def calculate_heat_dissipated(cls, bits: int, temp_kelvin: float = DEFAULT_TEMP_KELVIN) -> float:
        """Computes Landauer minimal dissipation heat Q = k_B * T * ln(2) * bits."""
        if bits < 0:
            raise TelemetryDomainInvariantViolation("bits must be non-negative.")
        return cls.BOLTZMANN_K * temp_kelvin * cls.LN_2 * float(bits)

    def record_bit_erasure(
        self,
        bits: int,
        operation: str = "irreversible_erasure",
        temp_kelvin: Optional[float] = None,
    ) -> float:
        """Records irreversible bit erasure, updates ledger heat dissipation, and logs event."""
        if bits < 0:
            raise TelemetryDomainInvariantViolation("bits erased must be non-negative.")

        temp = temp_kelvin or self.temp_kelvin
        dissipated_heat = self.ledger.record_bit_erasure(bits, temp_kelvin=temp)

        event = {
            "timestamp_ms": int(time.time() * 1000),
            "operation": operation,
            "bits_erased": bits,
            "heat_dissipated_joules": dissipated_heat,
            "total_bits_erased": self.ledger.total_bits_erased,
            "cumulative_heat_joules": self.ledger.heat_dissipated_joules,
        }
        self._erasure_events.append(event)
        return dissipated_heat

    def record_bit_recovery(self, bits: int, operation: str = "functorial_undo_reversal") -> float:
        """Applies mathematical adjoint bit recovery, reducing accumulated erasure tally."""
        if bits < 0:
            raise TelemetryDomainInvariantViolation("bits recovered must be non-negative.")

        initial_bits = self.ledger.total_bits_erased
        self.ledger.record_bit_recovery(bits)
        recovered_actual = initial_bits - self.ledger.total_bits_erased

        # Recalculate heat dissipation corresponding to recovered bits
        recovered_heat = self.calculate_heat_dissipated(recovered_actual, self.temp_kelvin)
        self.ledger.heat_dissipated_joules = max(0.0, self.ledger.heat_dissipated_joules - recovered_heat)

        event = {
            "timestamp_ms": int(time.time() * 1000),
            "operation": operation,
            "bits_recovered": recovered_actual,
            "heat_recovered_joules": recovered_heat,
            "total_bits_erased": self.ledger.total_bits_erased,
            "cumulative_heat_joules": self.ledger.heat_dissipated_joules,
        }
        self._recovery_events.append(event)
        return recovered_heat

    def spend_tokens(self, amount: int, is_protected: bool = False) -> None:
        """Deducts BPE tokens while enforcing the strict 60/40 thermodynamic boundary."""
        self.ledger.spend_tokens(amount, is_protected=is_protected)

    def get_ledger_snapshot(self) -> LandauerDissipationLedger:
        """Returns a snapshot copy of the current thermodynamic dissipation ledger."""
        return copy.deepcopy(self.ledger)

    def verify_capital_invariants(self) -> bool:
        """Verifies strict adherence to 60/40 capital partition and non-negative balances."""
        self.ledger.validate_invariants()

        if self.ledger.exploratory_spent > self.ledger.exploratory_capital:
            raise TelemetryDomainInvariantViolation(
                f"Exploratory capital overrun: {self.ledger.exploratory_spent} > {self.ledger.exploratory_capital}."
            )
        if self.ledger.protected_spent > self.ledger.protected_capital:
            raise TelemetryDomainInvariantViolation(
                f"Protected capital overrun: {self.ledger.protected_spent} > {self.ledger.protected_capital}."
            )
        if self.ledger.tokens_burned != (self.ledger.exploratory_spent + self.ledger.protected_spent):
            raise TelemetryDomainInvariantViolation(
                f"Tokens burned discrepancy: {self.ledger.tokens_burned} != {self.ledger.exploratory_spent + self.ledger.protected_spent}."
            )
        return True

    def certify_ledger(self) -> bool:
        """Validates all capital invariants and certifies the ledger."""
        self.verify_capital_invariants()
        self.ledger.is_certified = True
        return True

    @property
    def remaining_exploratory_capital(self) -> int:
        return self.ledger.exploratory_capital - self.ledger.exploratory_spent

    @property
    def remaining_protected_capital(self) -> int:
        return self.ledger.protected_capital - self.ledger.protected_spent

    @property
    def dissipation_metrics(self) -> Dict[str, Any]:
        return {
            "total_bits_erased": self.ledger.total_bits_erased,
            "heat_dissipated_joules": self.ledger.heat_dissipated_joules,
            "tokens_burned": self.ledger.tokens_burned,
            "token_lease_budget": self.ledger.token_lease_budget,
            "exploratory_capital": self.ledger.exploratory_capital,
            "exploratory_spent": self.ledger.exploratory_spent,
            "exploratory_remaining": self.remaining_exploratory_capital,
            "protected_capital": self.ledger.protected_capital,
            "protected_spent": self.ledger.protected_spent,
            "protected_remaining": self.remaining_protected_capital,
            "is_certified": self.ledger.is_certified,
            "erasure_events_count": len(self._erasure_events),
            "recovery_events_count": len(self._recovery_events),
        }
