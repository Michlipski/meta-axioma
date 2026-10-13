"""Axioma Fabric Thermodynamic Landauer Buffer & Entropy Accounting.

Computes exact physical Landauer erasure dissipation:
    Q = Delta S * k_B * T * ln(2)
Enforces thermodynamic compute leases and ring buffer backpressure limits.
"""

from __future__ import annotations
import math
import time
from collections import deque
from typing import Deque, Generic, List, Optional, Tuple, TypeVar
from .models import CausalEvent

T = TypeVar("T")

# Fundamental Physical Constants
BOLTZMANN_CONSTANT = 1.380649e-23  # J/K
DEFAULT_TEMPERATURE_KELVIN = 300.0  # Room temp
LN_2 = math.log(2.0)
LANDAUER_BIT_ENERGY_JOULES = BOLTZMANN_CONSTANT * DEFAULT_TEMPERATURE_KELVIN * LN_2


class ThermodynamicBackpressureError(Exception):
    """Raised when thermodynamic capacity or token budget lease is exhausted."""
    pass


class LandauerRingBuffer:
    """Bounded event buffer with physical bit-erasure entropy dissipation accounting."""

    def __init__(
        self,
        capacity_entries: int = 1000,
        max_memory_bytes: int = 1_000_000,
        token_lease_budget: float = 1000.0,
        temperature_kelvin: float = DEFAULT_TEMPERATURE_KELVIN,
    ) -> None:
        self.capacity_entries = capacity_entries
        self.max_memory_bytes = max_memory_bytes
        self.token_lease_budget = token_lease_budget
        self.temperature_kelvin = temperature_kelvin
        
        self._buffer: Deque[CausalEvent] = deque()
        self._current_memory_bytes: int = 0
        self._cumulative_bits_erased: int = 0
        self._cumulative_erasure_joules: float = 0.0
        self._tokens_consumed: float = 0.0

    @property
    def bit_energy(self) -> float:
        return BOLTZMANN_CONSTANT * self.temperature_kelvin * LN_2

    @property
    def current_bytes(self) -> int:
        return self._current_memory_bytes

    @property
    def current_entries(self) -> int:
        return len(self._buffer)

    @property
    def cumulative_erasure_joules(self) -> float:
        return self._cumulative_erasure_joules

    @property
    def remaining_token_budget(self) -> float:
        return max(0.0, self.token_lease_budget - self._tokens_consumed)

    def append(self, event: CausalEvent) -> Optional[CausalEvent]:
        """Append event to ring buffer.
        
        If capacity or memory threshold is exceeded, evicts oldest entry,
        calculates Landauer erasure dissipation, and consumes token budget.
        Raises ThermodynamicBackpressureError if budget is exhausted.
        """
        # Check token budget lease
        if self._tokens_consumed >= self.token_lease_budget:
            raise ThermodynamicBackpressureError(
                f"Thermodynamic compute lease exhausted ({self._tokens_consumed:.2f}/{self.token_lease_budget:.2f} tokens). "
                "Cooperative backpressure triggered."
            )

        evicted: Optional[CausalEvent] = None

        # Check entry or byte limit triggers eviction
        while len(self._buffer) >= self.capacity_entries or (
            self._current_memory_bytes + event.byte_size > self.max_memory_bytes and len(self._buffer) > 0
        ):
            old = self._buffer.popleft()
            self._current_memory_bytes -= old.byte_size
            bits = old.byte_size * 8
            self._cumulative_bits_erased += bits
            self._cumulative_erasure_joules += bits * self.bit_energy
            
            # 1 token per 10KB erased or 0.1 tokens min
            token_cost = max(0.01, old.byte_size / 10240.0)
            self._tokens_consumed += token_cost
            evicted = old

        self._buffer.append(event)
        self._current_memory_bytes += event.byte_size
        return evicted

    def replenish_token_lease(self, additional_tokens: float) -> None:
        """Replenish thermodynamic token budget (cooperative epoch reset)."""
        self.token_lease_budget += additional_tokens

    def get_all(self) -> List[CausalEvent]:
        """Return snapshot of events currently in buffer."""
        return list(self._buffer)

    def get_since(self, timestamp: float) -> List[CausalEvent]:
        """Return events with timestamp strictly greater than given time."""
        return [e for e in self._buffer if e.timestamp > timestamp]

    def clear(self) -> None:
        """Evict all items and record total erasure dissipation."""
        while self._buffer:
            old = self._buffer.popleft()
            bits = old.byte_size * 8
            self._cumulative_bits_erased += bits
            self._cumulative_erasure_joules += bits * self.bit_energy
        self._current_memory_bytes = 0
