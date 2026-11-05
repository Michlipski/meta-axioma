"""Empirical Test Suite for Bijective Contract Verification & Operational Pitfall AST Micro-Auditing.

Enforces:
- [NEG-G1B-001] Anti-Phantom Emission & Empirical Test Witness.
- Formal Verification of:
  - BIJ-001: Strict Bijective Symbol Mapping.
  - BIJ-002: Cryptographic Docstring & Specification Hash Synchronization.
  - BIJ-003: Type-Signature Morphism Isomorphism.
  - OP-001: Lock Dominance over Shared Mutable State (WITH_LOCK_GUARD).
  - OP-002: Deterministic Resource Cleanup (TRY_FINALLY_CLEANUP).
  - OP-003: Bounded Timeout on Network/IO Calls (BOUNDED_TIMEOUT).
  - OP-004: Hermetic Exception Translation (EXCEPTION_TRANSLATION_ENCLAVE).
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from generations.gen_04b.protocols.deliverable_bundle import (
    MitigationPattern,
    MitigationRule,
    OperationalPitfall,
)
from generations.gen_04b.services.audit.src.bijective_verifier import BijectiveVerifier
from generations.gen_04b.services.audit.src.operational_pitfall_auditor import (
    OperationalPitfallAuditor,
    operational_contract,
)
from generations.gen_04b.services.audit.src.zero_trust_micro_auditor import ZeroTrustMicroAuditor
from generations.gen_04b.services.audit.src.domain_models import (
    RogueSymbolViolation,
    UnimplementedVerbViolation,
    SpecificationDriftViolation,
    SignatureMismatchViolation,
    UnprotectedStateMutationViolation,
    ResourceLeakViolation,
    UnboundedNetworkCallViolation,
    RawExceptionLeakViolation,
)


@dataclass
class DummyParam:
    name: str
    type_name: str = "str"


@dataclass
class DummyVerb:
    name: str
    parameters: List[DummyParam] = field(default_factory=list)
    return_type: str = "void"
    pre_conditions: List[str] = field(default_factory=list)
    post_conditions: List[str] = field(default_factory=list)


@dataclass
class DummyContract:
    contract_id: str = "contract_ledger_v1"
    nouns: Dict[str, Any] = field(default_factory=dict)
    verbs: Dict[str, DummyVerb] = field(default_factory=dict)


class TestBijectiveAndOperationalAuditor(unittest.TestCase):
    """Exhaustive empirical test suite for BIJ-001..003 and OP-001..004."""

    def setUp(self) -> None:
        self.verifier = BijectiveVerifier()
        self.operational_auditor = OperationalPitfallAuditor()
        self.micro_auditor = ZeroTrustMicroAuditor()

        # Build dummy contract for testing
        self.commit_verb = DummyVerb(
            name="commit_delta",
            parameters=[DummyParam(name="delta", type_name="int")],
            return_type="bool",
            pre_conditions=["delta > 0"],
            post_conditions=["self.balance > prev_balance"],
        )
        self.spec_hash = BijectiveVerifier.compute_spec_hash(self.commit_verb)
        self.contract = DummyContract(
            contract_id="contract_test",
            verbs={"commit_delta": self.commit_verb},
        )

    # =========================================================================
    # BIJ-001 Tests: Bijective Symbol Mapping (Total Injectivity & Surjectivity)
    # =========================================================================

    def test_01_bij_happy_path(self) -> None:
        """Verifies valid bijective mapping with matching symbol, spec hash, and signature."""
        code = f'''
def commit_delta(delta: int) -> bool:
    """Commits delta to ledger.
    :param delta: int
    :return: bool
    :pre delta > 0
    :post self.balance > prev_balance
    @spec_hash: {self.spec_hash}
    """
    return True
'''
        witness = self.verifier.verify_bijectivity(code, self.contract, "test_happy.py")
        self.assertTrue(witness.is_bijective)
        self.assertEqual(witness.mapped_verbs, ["commit_delta"])
        self.assertEqual(witness.unmapped_verbs, [])
        self.assertEqual(witness.rogue_functions, [])

    def test_02_bij_001_rogue_function_trapped(self) -> None:
        """Verifies BIJ-001 raises RogueSymbolViolation when undocumented code exists."""
        code = f'''
def commit_delta(delta: int) -> bool:
    """Commits delta.
    :pre delta > 0
    :post self.balance > prev_balance
    @spec_hash: {self.spec_hash}
    """
    return True

def backdoor_phantom_helper() -> None:
    """Undocumented function not in contract."""
    pass
'''
        with self.assertRaises(RogueSymbolViolation):
            self.verifier.verify_bijectivity(code, self.contract, "test_rogue.py")

    def test_03_bij_001_unimplemented_verb_trapped(self) -> None:
        """Verifies BIJ-001 raises UnimplementedVerbViolation when a contract verb is missing."""
        code = '''
def some_other_function() -> None:
    pass
'''
        contract_extra = DummyContract(
            verbs={
                "commit_delta": self.commit_verb,
                "missing_verb": DummyVerb(name="missing_verb"),
            }
        )
        with self.assertRaises(RogueSymbolViolation):
            # some_other_function is rogue
            self.verifier.verify_bijectivity(code, contract_extra, "test_missing.py")

        # When only empty code with missing verbs
        with self.assertRaises(UnimplementedVerbViolation):
            self.verifier.verify_bijectivity("# empty file\n", contract_extra, "test_empty.py")

    # =========================================================================
    # BIJ-002 Tests: Docstring & Spec Hash Synchronization
    # =========================================================================

    def test_04_bij_002_missing_docstring_trapped(self) -> None:
        """Verifies BIJ-002 traps missing docstring specification."""
        code = '''
def commit_delta(delta: int) -> bool:
    return True
'''
        with self.assertRaises(SpecificationDriftViolation):
            self.verifier.verify_bijectivity(code, self.contract, "test_no_doc.py")

    def test_05_bij_002_missing_spec_hash_trapped(self) -> None:
        """Verifies BIJ-002 traps docstrings that omit @spec_hash directive."""
        code = '''
def commit_delta(delta: int) -> bool:
    """Commits delta without spec hash."""
    return True
'''
        with self.assertRaises(SpecificationDriftViolation):
            self.verifier.verify_bijectivity(code, self.contract, "test_no_hash.py")

    def test_06_bij_002_tampered_spec_hash_trapped(self) -> None:
        """Verifies BIJ-002 detects specification drift when hash does not match contract."""
        tampered_hash = "0" * 64
        code = f'''
def commit_delta(delta: int) -> bool:
    """Commits delta.
    :pre delta > 0
    :post self.balance > prev_balance
    @spec_hash: {tampered_hash}
    """
    return True
'''
        with self.assertRaises(SpecificationDriftViolation):
            self.verifier.verify_bijectivity(code, self.contract, "test_tampered.py")

    def test_07_bij_002_missing_pre_condition_trapped(self) -> None:
        """Verifies BIJ-002 ensures pre-conditions are documented."""
        code = f'''
def commit_delta(delta: int) -> bool:
    """Commits delta without pre clause.
    :post self.balance > prev_balance
    @spec_hash: {self.spec_hash}
    """
    return True
'''
        with self.assertRaises(SpecificationDriftViolation):
            self.verifier.verify_bijectivity(code, self.contract, "test_missing_pre.py")

    # =========================================================================
    # BIJ-003 Tests: Signature & Parameter Morphism Isomorphism
    # =========================================================================

    def test_08_bij_003_parameter_name_mismatch_trapped(self) -> None:
        """Verifies BIJ-003 raises SignatureMismatchViolation when parameter names drift."""
        code = f'''
def commit_delta(wrong_param_name: int) -> bool:
    """Commits delta.
    :pre delta > 0
    :post self.balance > prev_balance
    @spec_hash: {self.spec_hash}
    """
    return True
'''
        with self.assertRaises(SignatureMismatchViolation):
            self.verifier.verify_bijectivity(code, self.contract, "test_param_drift.py")

    # =========================================================================
    # OP-001 Tests: Lock Dominance (WITH_LOCK_GUARD)
    # =========================================================================

    def test_09_op_001_lock_guard_happy_path(self) -> None:
        """Verifies OP-001 passes when all state mutations are guarded by designated lock."""
        code = '''
class LedgerService:
    @operational_contract(
        pitfalls=[OperationalPitfall.CONCURRENCY_STATE_RACE],
        mitigations=[
            MitigationPattern(
                pitfall=OperationalPitfall.CONCURRENCY_STATE_RACE,
                rule=MitigationRule.WITH_LOCK_GUARD,
                target_guard="self._state_lock"
            )
        ]
    )
    def update_balance(self, amount: int) -> None:
        with self._state_lock:
            self._balance += amount
'''
        report = self.operational_auditor.audit_source(code, "test_lock_pass.py")
        self.assertTrue(report.is_compliant)
        self.assertIn("update_balance:WITH_LOCK_GUARD(self._state_lock)", report.mitigations_verified)

    def test_10_op_001_unprotected_mutation_trapped(self) -> None:
        """Verifies OP-001 raises UnprotectedStateMutationViolation when self.* is mutated outside lock."""
        code = '''
class LedgerService:
    @operational_contract(
        pitfalls=[OperationalPitfall.CONCURRENCY_STATE_RACE],
        mitigations=[
            MitigationPattern(
                pitfall=OperationalPitfall.CONCURRENCY_STATE_RACE,
                rule=MitigationRule.WITH_LOCK_GUARD,
                target_guard="self._state_lock"
            )
        ]
    )
    def update_balance(self, amount: int) -> None:
        self._balance += amount  # Unprotected mutation!
'''
        with self.assertRaises(UnprotectedStateMutationViolation):
            self.operational_auditor.audit_source(code, "test_lock_fail.py")

    # =========================================================================
    # OP-002 Tests: Resource Cleanup (TRY_FINALLY_CLEANUP)
    # =========================================================================

    def test_11_op_002_resource_cleanup_happy_path(self) -> None:
        """Verifies OP-002 passes when allocated resource is cleaned up in finally block."""
        code = '''
class SessionManager:
    @operational_contract(
        pitfalls=[OperationalPitfall.RESOURCE_LEAK_UNCLOSED],
        mitigations=[
            MitigationPattern(
                pitfall=OperationalPitfall.RESOURCE_LEAK_UNCLOSED,
                rule=MitigationRule.TRY_FINALLY_CLEANUP,
                cleanup_target="session.close"
            )
        ]
    )
    def execute_transaction(self) -> None:
        session = self.open_session()
        try:
            session.execute()
        finally:
            session.close()
'''
        report = self.operational_auditor.audit_source(code, "test_cleanup_pass.py")
        self.assertTrue(report.is_compliant)
        self.assertIn("execute_transaction:TRY_FINALLY_CLEANUP(session.close)", report.mitigations_verified)

    def test_12_op_002_resource_leak_trapped(self) -> None:
        """Verifies OP-002 raises ResourceLeakViolation when finally cleanup is missing."""
        code = '''
class SessionManager:
    @operational_contract(
        pitfalls=[OperationalPitfall.RESOURCE_LEAK_UNCLOSED],
        mitigations=[
            MitigationPattern(
                pitfall=OperationalPitfall.RESOURCE_LEAK_UNCLOSED,
                rule=MitigationRule.TRY_FINALLY_CLEANUP,
                cleanup_target="session.close"
            )
        ]
    )
    def execute_transaction(self) -> None:
        session = self.open_session()
        session.execute()
'''
        with self.assertRaises(ResourceLeakViolation):
            self.operational_auditor.audit_source(code, "test_cleanup_fail.py")

    # =========================================================================
    # OP-003 Tests: Bounded Timeout (BOUNDED_TIMEOUT)
    # =========================================================================

    def test_13_op_003_bounded_timeout_happy_path(self) -> None:
        """Verifies OP-003 passes when network call explicitly passes positive timeout."""
        code = '''
class HttpClient:
    @operational_contract(
        pitfalls=[OperationalPitfall.TRANSIENT_NETWORK_FAILURE],
        mitigations=[
            MitigationPattern(
                pitfall=OperationalPitfall.TRANSIENT_NETWORK_FAILURE,
                rule=MitigationRule.BOUNDED_TIMEOUT,
                max_timeout_sec=5.0
            )
        ]
    )
    def fetch_data(self, url: str) -> None:
        self.get(url, timeout=5.0)
'''
        report = self.operational_auditor.audit_source(code, "test_timeout_pass.py")
        self.assertTrue(report.is_compliant)
        self.assertIn("fetch_data:BOUNDED_TIMEOUT(5.0s)", report.mitigations_verified)

    def test_14_op_003_unbounded_network_call_trapped(self) -> None:
        """Verifies OP-003 raises UnboundedNetworkCallViolation when timeout kwarg is missing."""
        code = '''
class HttpClient:
    @operational_contract(
        pitfalls=[OperationalPitfall.TRANSIENT_NETWORK_FAILURE],
        mitigations=[
            MitigationPattern(
                pitfall=OperationalPitfall.TRANSIENT_NETWORK_FAILURE,
                rule=MitigationRule.BOUNDED_TIMEOUT,
                max_timeout_sec=5.0
            )
        ]
    )
    def fetch_data(self, url: str) -> None:
        self.get(url)  # Missing timeout!
'''
        with self.assertRaises(UnboundedNetworkCallViolation):
            self.operational_auditor.audit_source(code, "test_timeout_fail.py")

    # =========================================================================
    # OP-004 Tests: Exception Translation Enclave (EXCEPTION_TRANSLATION_ENCLAVE)
    # =========================================================================

    def test_15_op_004_exception_enclave_happy_path(self) -> None:
        """Verifies OP-004 passes when raw exceptions are translated into typed domain exceptions."""
        code = '''
class GatewayService:
    @operational_contract(
        pitfalls=[OperationalPitfall.UNHANDLED_BOUNDARY_EXCEPTION],
        mitigations=[
            MitigationPattern(
                pitfall=OperationalPitfall.UNHANDLED_BOUNDARY_EXCEPTION,
                rule=MitigationRule.EXCEPTION_TRANSLATION_ENCLAVE
            )
        ]
    )
    def dispatch(self) -> None:
        try:
            self.do_io()
        except OSError as e:
            raise AuditDomainInvariantViolation("Gateway IO error") from e
'''
        report = self.operational_auditor.audit_source(code, "test_enclave_pass.py")
        self.assertTrue(report.is_compliant)
        self.assertIn("dispatch:EXCEPTION_TRANSLATION_ENCLAVE", report.mitigations_verified)

    def test_16_op_004_bare_except_trapped(self) -> None:
        """Verifies OP-004 raises RawExceptionLeakViolation when bare except: is used."""
        code = '''
class GatewayService:
    @operational_contract(
        pitfalls=[OperationalPitfall.UNHANDLED_BOUNDARY_EXCEPTION],
        mitigations=[
            MitigationPattern(
                pitfall=OperationalPitfall.UNHANDLED_BOUNDARY_EXCEPTION,
                rule=MitigationRule.EXCEPTION_TRANSLATION_ENCLAVE
            )
        ]
    )
    def dispatch(self) -> None:
        try:
            self.do_io()
        except:  # Bare except is prohibited!
            pass
'''
        with self.assertRaises(RawExceptionLeakViolation):
            self.operational_auditor.audit_source(code, "test_bare_except.py")

    # =========================================================================
    # Comprehensive Micro-Auditor Integration Test
    # =========================================================================

    def test_17_micro_auditor_comprehensive_full_suite(self) -> None:
        """Verifies ZeroTrustMicroAuditor.audit_leaf_comprehensive executes all tiers cleanly."""
        code = f'''
class LedgerService:
    @operational_contract(
        pitfalls=[
            OperationalPitfall.CONCURRENCY_STATE_RACE,
            OperationalPitfall.RESOURCE_LEAK_UNCLOSED
        ],
        mitigations=[
            MitigationPattern(
                pitfall=OperationalPitfall.CONCURRENCY_STATE_RACE,
                rule=MitigationRule.WITH_LOCK_GUARD,
                target_guard="self._state_lock"
            ),
            MitigationPattern(
                pitfall=OperationalPitfall.RESOURCE_LEAK_UNCLOSED,
                rule=MitigationRule.TRY_FINALLY_CLEANUP,
                cleanup_target="session.close"
            )
        ]
    )
    def commit_delta(self, delta: int) -> bool:
        """Commits delta to ledger.
        :param delta: int
        :return: bool
        :pre delta > 0
        :post self.balance > prev_balance
        @spec_hash: {self.spec_hash}
        """
        with self._state_lock:
            session = self.open_session()
            try:
                self._balance += delta
                return True
            finally:
                session.close()
'''
        result = self.micro_auditor.audit_leaf_comprehensive(
            code, contract=self.contract, leaf_id="ledger_service.py"
        )
        self.assertTrue(result["is_passed"])
        self.assertEqual(result["stage"], "COMPREHENSIVE_AUDIT_PASSED")
        self.assertTrue(result["hermetic_report"]["is_hermetic"])
        self.assertTrue(result["bijective_witness"]["is_bijective"])
        self.assertTrue(result["operational_report"]["is_compliant"])


if __name__ == "__main__":
    unittest.main()
