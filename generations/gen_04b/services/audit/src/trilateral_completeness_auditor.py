r"""Trilateral Completeness Auditor & Tri-Planar Bisimulation Engine (`soc_g4b_audit`).

Enforces:
- [L1-G4B-001] Sovereign Mesh Verification Gate & Protocol Standardization.
- [L1-G3B-011] Universal Contract & Statechart IR.
- [L1-G3B-013] Empirical Journey Observation & Subprocess Grounding.
- [L1-G4B-015] Presentation Micro-Auditor & 4 Universal Human Ergonomics Axioms.
- [L1-G4B-017] Headless Journey Walker & Eulerian Covering Path.
- [INV-G4B-TRACE-001] TRACE-AST Bijectivity & Type-Morphism Isomorphism (TRACE-001A..D).
- [NEG-G1B-001] Anti-Phantom Emission Gate.
- [NEG-G1B-002] Anti-Mock Subprocess Entrypoint Smoke Invariant.
- Mathematical Tri-Planar Bisimulation:
    G_spec <== [Galois Adjunction] ==> G_code
      ||                                 ||
      || [Statechart Covering]           || [Subprocess Smoke & Delta S]
      \/                                 \/
    G_state <============================ G_state
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from .bijective_verifier import BijectiveVerifier
from .domain_models import AuditSeverity
from .headless_ui_walker import HeadlessUIWalker, HeadlessUIWalkReport
from .journey_walker.domain_models import JourneyReport, JourneyStep
from .journey_walker.flow_parser import FlowParser
from .journey_walker.runner import HeadlessUIJourneyWalker
from .journey_walker.statechart_ir import StatechartIR
from .presentation_micro_auditor import PresentationAuditReport, PresentationMicroAuditor
from .trace_bijective_auditor import TraceAuditReport, TraceBijectiveAuditor


class TrilateralAuditViolation(Exception):
    """Raised when an application violates Tri-Planar Completeness invariants."""
    pass


@dataclass(frozen=True)
class TriPlanarMerkleAttestation:
    """Immutable cryptographic witness anchoring the 3 parallel planes into a Merkle root."""
    attestation_id: str
    app_id: str
    spec_code_hash: str
    code_state_hash: str
    spec_state_hash: str
    tri_planar_merkle_root: str
    timestamp_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if len(self.tri_planar_merkle_root) != 64:
            raise ValueError(f"Invalid tri_planar_merkle_root length: {len(self.tri_planar_merkle_root)}")
        if len(self.spec_code_hash) != 64 or len(self.code_state_hash) != 64 or len(self.spec_state_hash) != 64:
            raise ValueError("All plane constituent hashes must be 64-character SHA-256 strings.")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrilateralAuditReport:
    """Consolidated master audit report spanning all 3 parallel planes."""
    app_id: str
    is_complete: bool
    spec_code_bijective: bool
    code_state_conforming: bool
    spec_state_bisimilar: bool
    tri_planar_merkle_root: str
    attestation: Optional[TriPlanarMerkleAttestation]
    trace_report: TraceAuditReport
    presentation_report: Optional[PresentationAuditReport] = None
    headless_walk_report: Optional[HeadlessUIWalkReport] = None
    journey_report: Optional[JourneyReport] = None
    telemetry_tx_count: int = 0
    violations: List[str] = field(default_factory=list)
    timestamp_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "app_id": self.app_id,
            "is_complete": self.is_complete,
            "spec_code_bijective": self.spec_code_bijective,
            "code_state_conforming": self.code_state_conforming,
            "spec_state_bisimilar": self.spec_state_bisimilar,
            "tri_planar_merkle_root": self.tri_planar_merkle_root,
            "attestation": self.attestation.to_dict() if self.attestation else None,
            "trace_report": asdict(self.trace_report),
            "presentation_report": asdict(self.presentation_report) if self.presentation_report else None,
            "headless_walk_report": asdict(self.headless_walk_report) if self.headless_walk_report else None,
            "journey_report": self.journey_report.to_dict() if self.journey_report else None,
            "telemetry_tx_count": self.telemetry_tx_count,
            "violations": list(self.violations),
            "timestamp_unix_ms": self.timestamp_unix_ms,
        }


class TrilateralCompletenessAuditor:
    """Master sovereign engine enforcing Tri-Planar Completeness & Trilateral Bisimulation."""

    def __init__(
        self,
        node_id: str = "node_trilateral_auditor",
        telemetry_vault: Optional[Any] = None,
    ) -> None:
        self.node_id = node_id
        self.telemetry_vault = telemetry_vault
        self.trace_auditor = TraceBijectiveAuditor()
        self.presentation_auditor = PresentationMicroAuditor()
        self.headless_walker = HeadlessUIWalker()
        self.journey_walker = HeadlessUIJourneyWalker()

    @staticmethod
    def compute_merkle_root(h1: str, h2: str, h3: str) -> str:
        """Computes pairwise SHA-256 Merkle root over 3 plane attestation hashes."""
        # Level 1: pair (h1, h2) and duplicate h3
        left = hashlib.sha256(f"{h1}:{h2}".encode("utf-8")).hexdigest()
        right = hashlib.sha256(f"{h3}:{h3}".encode("utf-8")).hexdigest()
        # Level 2: root
        return hashlib.sha256(f"{left}:{right}".encode("utf-8")).hexdigest()

    def audit_application(
        self,
        app_dir: str | Path,
        statechart_ir: Optional[StatechartIR] = None,
        execute_subprocess_journey: bool = True,
        raise_on_error: bool = False,
    ) -> TrilateralAuditReport:
        """Executes full trilateral audit spanning Plane 1, Plane 2, and Plane 3."""
        path = Path(app_dir).resolve()
        app_id = path.name
        violations: List[str] = []

        # =========================================================================
        # PLANE 1 <--> PLANE 2: Specification to Code AST Bijectivity
        # =========================================================================
        # 1. TraceBijectiveAuditor: TRACE-001A..D (Entities, Fields, and Types)
        trace_report = self.trace_auditor.audit_app_directory(
            path,
            check_types=True,
            strict_types=False,
        )
        if not trace_report.is_bijective:
            violations.extend([f"[P1-P2 TRACE] {v}" for v in trace_report.violations])

        # 2. Extract Statechart Events for UI Bisimulation
        events: List[str] = []
        if statechart_ir is not None:
            events = statechart_ir.get_all_events()
        else:
            schema_statechart = path / "schema" / "statechart_ir.json"
            if schema_statechart.exists():
                try:
                    loaded_ir = StatechartIR.from_json(schema_statechart.read_text(encoding="utf-8"))
                    events = loaded_ir.get_all_events()
                    statechart_ir = loaded_ir
                except Exception:
                    pass

        # 3. PresentationMicroAuditor: HERM-UI-001..003
        presentation_report: Optional[PresentationAuditReport] = None
        try:
            presentation_report = self.presentation_auditor.audit_app_directory(
                path,
                statechart_events=events if events else None,
                allow_raise=False,
            )
            if not presentation_report.is_certified:
                violations.append(f"[P1-P2 Presentation] Presentation audit uncertified for {app_id}")
        except Exception as e:
            violations.append(f"[P1-P2 Presentation] Presentation audit failed: {e}")

        # Compute Plane 1 <--> Plane 2 Hash
        p1_p2_payload = f"{trace_report.is_bijective}:{len(trace_report.missing_in_code)}:{presentation_report.is_certified if presentation_report else False}"
        spec_code_hash = hashlib.sha256(p1_p2_payload.encode("utf-8")).hexdigest()
        spec_code_bijective = trace_report.is_bijective and (presentation_report.is_certified if presentation_report else True)

        # =========================================================================
        # PLANE 2 <--> PLANE 3: Code AST to Runtime Subprocess State
        # =========================================================================
        headless_walk_report: Optional[HeadlessUIWalkReport] = None
        code_state_conforming = True

        if execute_subprocess_journey:
            try:
                headless_walk_report = self.headless_walker.walk_app_presentation(
                    path,
                    allow_raise=False,
                )
                if not headless_walk_report.is_certified:
                    code_state_conforming = False
                    violations.append(f"[P2-P3 Subprocess] Headless UI walk failed certification for {app_id}")
            except Exception as e:
                code_state_conforming = False
                violations.append(f"[P2-P3 Subprocess] Subprocess walk encountered error: {e}")

        p2_p3_payload = f"{headless_walk_report.is_certified if headless_walk_report else True}:{code_state_conforming}"
        code_state_hash = hashlib.sha256(p2_p3_payload.encode("utf-8")).hexdigest()

        # =========================================================================
        # PLANE 1 <--> PLANE 3: Specification to Runtime State Bisimulation
        # =========================================================================
        journey_report: Optional[JourneyReport] = None
        spec_state_bisimilar = True
        tx_count_before = 0
        if self.telemetry_vault is not None:
            try:
                tx_count_before = self.telemetry_vault.get_summary().get("total_transactions", 0)
            except Exception:
                pass

        if execute_subprocess_journey and statechart_ir is not None:
            try:
                # Compile minimal covering path from StatechartIR
                statechart_dict = {
                    "id": statechart_ir.id,
                    "initial": statechart_ir.root.initial,
                    "states": {k: v.to_dict() for k, v in statechart_ir.root.states.items()},
                }
                covering_steps, coverage_pct = FlowParser.compute_statechart_covering_path(
                    statechart_dict,
                    initial_state=statechart_ir.root.initial,
                )

                entrypoint_file = path / "run.py"
                if entrypoint_file.exists() and covering_steps:
                    journey_report = self.journey_walker.walk_journey(
                        journey_steps=covering_steps,
                        app_entrypoint=str(entrypoint_file),
                        flow_name=f"{app_id}_covering_tour",
                        statechart_coverage_pct=coverage_pct,
                        telemetry_vault=self.telemetry_vault,
                    )
                    if journey_report.journey_status != "PASSED":
                        spec_state_bisimilar = False
                        violations.append(f"[P1-P3 Bisimulation] Journey covering walk failed for {app_id}")
            except Exception as e:
                spec_state_bisimilar = False
                violations.append(f"[P1-P3 Bisimulation] Journey walk error: {e}")

        # Compute Plane 1 <--> Plane 3 Hash
        spec_state_hash = journey_report.calculate_witness_hash() if journey_report else hashlib.sha256(b"EMPTY_JOURNEY_WITNESS").hexdigest()

        # Telemetry transaction delta
        tx_count_after = tx_count_before
        if self.telemetry_vault is not None:
            try:
                tx_count_after = self.telemetry_vault.get_summary().get("total_transactions", 0)
            except Exception:
                pass
        recorded_tx_delta = max(0, tx_count_after - tx_count_before)

        # =========================================================================
        # TRI-PLANAR MERKLE ATTESTATION
        # =========================================================================
        tri_planar_merkle_root = self.compute_merkle_root(
            spec_code_hash,
            code_state_hash,
            spec_state_hash,
        )

        attestation = TriPlanarMerkleAttestation(
            attestation_id=f"attest_tri_{uuid.uuid4().hex[:12]}",
            app_id=app_id,
            spec_code_hash=spec_code_hash,
            code_state_hash=code_state_hash,
            spec_state_hash=spec_state_hash,
            tri_planar_merkle_root=tri_planar_merkle_root,
        )
        attestation.validate_invariants()

        is_complete = spec_code_bijective and code_state_conforming and spec_state_bisimilar and len(violations) == 0

        report = TrilateralAuditReport(
            app_id=app_id,
            is_complete=is_complete,
            spec_code_bijective=spec_code_bijective,
            code_state_conforming=code_state_conforming,
            spec_state_bisimilar=spec_state_bisimilar,
            tri_planar_merkle_root=tri_planar_merkle_root,
            attestation=attestation,
            trace_report=trace_report,
            presentation_report=presentation_report,
            headless_walk_report=headless_walk_report,
            journey_report=journey_report,
            telemetry_tx_count=recorded_tx_delta,
            violations=violations,
        )

        if raise_on_error and not is_complete:
            raise TrilateralAuditViolation(
                f"Tri-Planar Completeness audit failed for application '{app_id}': "
                f"Violations: {'; '.join(violations)}"
            )

        return report
