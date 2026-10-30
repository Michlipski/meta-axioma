"""Unit and thermodynamic invariant tests for Landauer Dissipation & Capital Engine (`soc_g4b_telemetry`).

Verifies:
- [L1-G3B-018] Landauer Heat Dissipation: Q = k_B * T * ln(2) * bits at T = 300K.
- Strict 60/40 Thermodynamic Capital Partition:
  - Total Lease Budget:  880,300 tokens
  - Exploratory Capital: 528,180 tokens (60%)
  - Protected Capital:   352,120 tokens (40%)
- Bit erasure accumulation and mathematical adjoint bit recovery via Functorial Undo.
- Protection against exploratory and protected token spend overruns.
- Protection against negative bits, negative spends, and invalid physical temperatures.
- Ledger certification, snapshot immutability, and dissipation metrics.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest

TEL_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = TEL_ROOT.parent.parent.parent.parent
for p in [str(TEL_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from generations.gen_04b.services.telemetry.src.domain_models import (
    TelemetryDomainInvariantViolation,
)
from generations.gen_04b.services.telemetry.src.landauer_thermodynamic_engine import (
    LandauerThermodynamicEngine,
)


class TestLandauerThermodynamicEngine(unittest.TestCase):
    """Test suite for LandauerThermodynamicEngine and 60/40 thermodynamic capital invariants."""

    def setUp(self):
        self.engine = LandauerThermodynamicEngine(token_lease_budget=880300, temp_kelvin=300.0)

    def test_default_initialization_and_60_40_partition(self):
        self.assertEqual(self.engine.ledger.token_lease_budget, 880300)
        self.assertEqual(self.engine.ledger.exploratory_capital, 528180)
        self.assertEqual(self.engine.ledger.protected_capital, 352120)
        self.assertEqual(self.engine.ledger.exploratory_capital + self.engine.ledger.protected_capital, 880300)
        self.assertEqual(self.engine.remaining_exploratory_capital, 528180)
        self.assertEqual(self.engine.remaining_protected_capital, 352120)

    def test_calculate_heat_dissipated_formula(self):
        # Q = kB * T * ln(2) * bits
        k_b = 1.380649e-23
        ln2 = 0.6931471805599453
        bits = 100_000

        expected_q = k_b * 300.0 * ln2 * bits
        actual_q = LandauerThermodynamicEngine.calculate_heat_dissipated(bits, temp_kelvin=300.0)
        self.assertAlmostEqual(actual_q, expected_q, places=25)

        # Zero bits should produce zero heat
        self.assertEqual(LandauerThermodynamicEngine.calculate_heat_dissipated(0, temp_kelvin=300.0), 0.0)

        # Custom temperature T = 350K
        expected_q_350 = k_b * 350.0 * ln2 * bits
        actual_q_350 = LandauerThermodynamicEngine.calculate_heat_dissipated(bits, temp_kelvin=350.0)
        self.assertAlmostEqual(actual_q_350, expected_q_350, places=25)

    def test_record_bit_erasure_and_dissipation(self):
        heat_1 = self.engine.record_bit_erasure(50_000, operation="erase_batch_1")
        self.assertGreater(heat_1, 0.0)
        self.assertEqual(self.engine.ledger.total_bits_erased, 50_000)
        self.assertAlmostEqual(self.engine.ledger.heat_dissipated_joules, heat_1, places=25)

        heat_2 = self.engine.record_bit_erasure(25_000, operation="erase_batch_2")
        self.assertEqual(self.engine.ledger.total_bits_erased, 75_000)
        self.assertAlmostEqual(self.engine.ledger.heat_dissipated_joules, heat_1 + heat_2, places=25)

    def test_functorial_undo_bit_recovery(self):
        self.engine.record_bit_erasure(100_000, operation="erase_forward")
        initial_heat = self.engine.ledger.heat_dissipated_joules

        # Recover 40,000 bits via undo
        recovered_heat = self.engine.record_bit_recovery(40_000, operation="undo_rollback")
        self.assertEqual(self.engine.ledger.total_bits_erased, 60_000)
        self.assertAlmostEqual(
            self.engine.ledger.heat_dissipated_joules,
            initial_heat - recovered_heat,
            places=25,
        )

        # Recover remaining 60,000 bits
        self.engine.record_bit_recovery(60_000)
        self.assertEqual(self.engine.ledger.total_bits_erased, 0)
        self.assertAlmostEqual(self.engine.ledger.heat_dissipated_joules, 0.0, places=25)

    def test_token_spend_within_exploratory_and_protected_pools(self):
        # Spend exploratory capital
        self.engine.spend_tokens(200_000, is_protected=False)
        self.assertEqual(self.engine.ledger.exploratory_spent, 200_000)
        self.assertEqual(self.engine.remaining_exploratory_capital, 328180)
        self.assertEqual(self.engine.ledger.tokens_burned, 200_000)

        # Spend protected capital
        self.engine.spend_tokens(100_000, is_protected=True)
        self.assertEqual(self.engine.ledger.protected_spent, 100_000)
        self.assertEqual(self.engine.remaining_protected_capital, 252120)
        self.assertEqual(self.engine.ledger.tokens_burned, 300_000)

        self.assertTrue(self.engine.verify_capital_invariants())

    def test_token_spend_overrun_exploratory_rejection(self):
        # Spend up to the exact ceiling: 528,180
        self.engine.spend_tokens(528180, is_protected=False)
        self.assertEqual(self.engine.remaining_exploratory_capital, 0)

        # 1 additional token overspend must fail with TelemetryDomainInvariantViolation
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.engine.spend_tokens(1, is_protected=False)

    def test_token_spend_overrun_protected_rejection(self):
        # Spend up to the exact floor: 352,120
        self.engine.spend_tokens(352120, is_protected=True)
        self.assertEqual(self.engine.remaining_protected_capital, 0)

        # 1 additional token overspend must fail with TelemetryDomainInvariantViolation
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.engine.spend_tokens(1, is_protected=True)

    def test_negative_bit_and_spend_invariants(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.engine.record_bit_erasure(-500)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.engine.record_bit_recovery(-200)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.engine.spend_tokens(-1000)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            LandauerThermodynamicEngine.calculate_heat_dissipated(-1)

    def test_ledger_certification_and_metrics(self):
        self.engine.spend_tokens(1000, is_protected=False)
        self.engine.spend_tokens(500, is_protected=True)
        self.engine.record_bit_erasure(10_000)

        self.assertFalse(self.engine.ledger.is_certified)
        self.assertTrue(self.engine.certify_ledger())
        self.assertTrue(self.engine.ledger.is_certified)

        metrics = self.engine.dissipation_metrics
        self.assertEqual(metrics["tokens_burned"], 1500)
        self.assertEqual(metrics["total_bits_erased"], 10_000)
        self.assertTrue(metrics["is_certified"])
        self.assertEqual(metrics["erasure_events_count"], 1)

        snapshot = self.engine.get_ledger_snapshot()
        self.assertEqual(snapshot.tokens_burned, 1500)
        self.assertTrue(snapshot.is_certified)

    def test_invalid_constructor_parameters(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            LandauerThermodynamicEngine(token_lease_budget=-100)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            LandauerThermodynamicEngine(token_lease_budget=0)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            LandauerThermodynamicEngine(temp_kelvin=0.0)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            LandauerThermodynamicEngine(temp_kelvin=-50.0)


if __name__ == "__main__":
    unittest.main()
