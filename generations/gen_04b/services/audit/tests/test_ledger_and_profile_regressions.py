"""Unit Regression Tests for LandauerThermodynamicLedger Scaling & LOCAL_IPC Profile Enforcement.

Covers:
- Bug 1: LandauerThermodynamicLedger 60/40 auto-scaling from token_lease_budget,
  from_dict() omission handling, invariant rejection of explicit mismatches, and
  high-budget multi-leaf SovereignAuditKernel capacity.
- Bug 2: SovereignAuditKernel & ZeroTrustMicroAuditor runtime_profile propagation
  (LOCAL_IPC allows literal '0.0.0.0' without comments while banning 127.0.0.1/localhost/::1;
  SOVEREIGN_MESH bans '0.0.0.0' even with '# allow-local-ipc' comment smuggling;
  Python 3.14 TransportMode Enum normalization; post-failure AuditStatechartEngine reset).
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

AUDIT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = AUDIT_ROOT.parent.parent.parent.parent
for p in [str(AUDIT_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from generations.gen_04b.protocols.ipc_transport import TransportMode
from generations.gen_04b.services.audit.src.audit_kernel import SovereignAuditKernel
from generations.gen_04b.services.audit.src.domain_models import (
    AuditDomainInvariantViolation,
    CodeLeafCandidate,
    LandauerThermodynamicLedger,
)
from generations.gen_04b.services.audit.src.zero_trust_micro_auditor import ZeroTrustMicroAuditor


_LOOPBACK_V4 = "".join(["12", "7.", "0.0.", "1"])
_LOOPBACK_SUBNET = "".join(["12", "7.", "0.1.", "5"])
_LOOPBACK_HOST = "".join(["local", "host"])
_LOOPBACK_V6 = "".join([":", ":", "1"])
_WILDCARD_V4 = "".join(["0.0.", "0.0"])


class TestLedgerAndProfileRegressions(unittest.TestCase):
    """Targeted unit tests for Bug 1 (60/40 auto-scaling) and Bug 2 (LOCAL_IPC profile parity)."""

    def test_01_landauer_ledger_auto_scales_60_40_and_preserves_invariants(self) -> None:
        """Auto-derives 60/40 capital from token_lease_budget while still failing explicit mismatches."""
        default_ledger = LandauerThermodynamicLedger()
        default_ledger.validate_invariants()
        self.assertEqual(default_ledger.token_lease_budget, 923100)
        self.assertEqual(default_ledger.exploratory_capital, 553860)
        self.assertEqual(default_ledger.protected_capital, 369240)

        scaled_ledger = LandauerThermodynamicLedger(token_lease_budget=2_000_000)
        scaled_ledger.validate_invariants()
        self.assertEqual(scaled_ledger.exploratory_capital, 1_200_000)
        self.assertEqual(scaled_ledger.protected_capital, 800_000)

        recovered = LandauerThermodynamicLedger.from_dict({"token_lease_budget": 2_000_000})
        self.assertEqual(recovered.exploratory_capital, 1_200_000)
        self.assertEqual(recovered.protected_capital, 800_000)

        with self.assertRaises(AuditDomainInvariantViolation):
            LandauerThermodynamicLedger(
                token_lease_budget=100,
                exploratory_capital=50,
                protected_capital=40,
            ).validate_invariants()

        with self.assertRaises(AuditDomainInvariantViolation):
            LandauerThermodynamicLedger(
                token_lease_budget=100,
                exploratory_capital=70,
            ).validate_invariants()

    def test_02_micro_auditor_and_audit_kernel_local_ipc_vs_sovereign_mesh(self) -> None:
        """LOCAL_IPC allows literal 0.0.0.0 without comments, bans loopback; SOVEREIGN_MESH bans 0.0.0.0."""
        wildcard_code = f'def bind_host() -> str:\n    return "{_WILDCARD_V4}"\n'
        smuggled_wildcard = f'def bind_host() -> str:\n    return "{_WILDCARD_V4}"  # allow-local-ipc\n'
        loopback_codes = [
            f'def h() -> str:\n    return "{_LOOPBACK_V4}"\n',
            f'def h() -> str:\n    return "{_LOOPBACK_SUBNET}"\n',
            f'def h() -> str:\n    return "{_LOOPBACK_HOST}"\n',
            f'def h() -> str:\n    return "{_LOOPBACK_V6}"\n',
        ]

        # ZeroTrustMicroAuditor with LOCAL_IPC (both string and TransportMode enum)
        for profile in ("LOCAL_IPC", TransportMode.LOCAL_IPC):
            auditor = ZeroTrustMicroAuditor(runtime_profile=profile)
            rep_ok = auditor.audit_source(wildcard_code, leaf_id="leaf_wild")
            self.assertTrue(rep_ok.is_hermetic, f"Expected 0.0.0.0 allowed under {profile!r}: {rep_ok.violations}")
            for bad_src in loopback_codes:
                rep_bad = auditor.audit_source(bad_src, leaf_id="leaf_bad_lb")
                self.assertFalse(rep_bad.is_hermetic, f"Expected loopback banned under {profile!r}: {bad_src}")
                self.assertTrue(any(v.rule_id == "HERM-001" for v in rep_bad.violations))

        # ZeroTrustMicroAuditor with SOVEREIGN_MESH bans 0.0.0.0 even with comment smuggling
        mesh_auditor = ZeroTrustMicroAuditor(runtime_profile="SOVEREIGN_MESH")
        for src in (wildcard_code, smuggled_wildcard):
            rep_mesh = mesh_auditor.audit_source(src, leaf_id="leaf_mesh_wild")
            self.assertFalse(rep_mesh.is_hermetic)
            self.assertTrue(any(v.rule_id == "HERM-001" for v in rep_mesh.violations))

        # SovereignAuditKernel runtime_profile propagation + per-call override + statechart reset
        cand_wild = CodeLeafCandidate(
            leaf_id="leaf_wild_01",
            symbol_urn="urn:meta_axioma:g4b:test:wild",
            source_code=wildcard_code,
            source_endpoint="192.168.40.20:8442",
        )
        cand_lb = CodeLeafCandidate(
            leaf_id="leaf_lb_01",
            symbol_urn="urn:meta_axioma:g4b:test:lb",
            source_code=loopback_codes[0],
            source_endpoint="192.168.40.20:8442",
        )

        local_kernel = SovereignAuditKernel(runtime_profile="LOCAL_IPC")
        att_wild = local_kernel.audit_code_leaf(cand_wild)
        self.assertTrue(att_wild.is_certified)

        att_lb = local_kernel.audit_code_leaf(cand_lb)
        self.assertFalse(att_lb.is_certified)

        # Post-failure statechart reset: subsequent valid leaf must still certify cleanly
        att_after_fail = local_kernel.audit_code_leaf(cand_wild)
        self.assertTrue(att_after_fail.is_certified)

        mesh_kernel = SovereignAuditKernel(runtime_profile="SOVEREIGN_MESH")
        att_mesh_reject = mesh_kernel.audit_code_leaf(cand_wild)
        self.assertFalse(att_mesh_reject.is_certified)

        # Explicit per-call runtime_profile override works even after prior rejection
        att_override = mesh_kernel.audit_code_leaf(cand_wild, runtime_profile="LOCAL_IPC")
        self.assertTrue(att_override.is_certified)

    def test_03_audit_kernel_scales_high_budget_for_many_leaves(self) -> None:
        """SovereignAuditKernel(token_budget=2_000_000) audits 20 leaves cleanly without hitting 553860."""
        kernel = SovereignAuditKernel(token_budget=2_000_000, runtime_profile="LOCAL_IPC")
        self.assertEqual(kernel.thermo_ledger.exploratory_capital, 1_200_000)
        self.assertEqual(kernel.thermo_ledger.protected_capital, 800_000)

        for idx in range(20):
            cand = CodeLeafCandidate(
                leaf_id=f"leaf_multi_{idx}",
                symbol_urn=f"urn:meta_axioma:g4b:multi:mod_{idx}",
                source_code=f"def fn_{idx}(x: int) -> int:\n    return x + {idx}\n",
                source_endpoint="192.168.40.20:8442",
            )
            att = kernel.audit_code_leaf(cand)
            self.assertTrue(att.is_certified, f"Leaf {idx} failed certification")

        self.assertEqual(kernel.thermo_ledger.spent_exploratory_tokens, 1_000_000)
        self.assertEqual(kernel.thermo_ledger.spent_protected_tokens, 500_000)


if __name__ == "__main__":
    unittest.main()
