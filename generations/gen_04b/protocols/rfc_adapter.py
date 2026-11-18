"""Generation 4b RFC Protocol Schema Adapter (`protocols/rfc_adapter.py`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [CRIT-03] Package-qualified domain model imports preventing sys.modules namespace collisions.
- [CRIT-05] Bijective schema adaptation across Canonical RFC Protocol, Research Service,
  and Governance Service representations.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional, Union
import uuid

# Canonical Protocol models
from generations.gen_04b.protocols.rfc_protocol import (
    BottleneckType as CanonicalBottleneckType,
    CounterProof as CanonicalCounterProof,
    RFCProtocolViolation,
    RFCStatus as CanonicalRFCStatus,
    SolverResult as CanonicalSolverResult,
    SpecAdjustmentRequest as CanonicalSpecAdjustmentRequest,
    SpecAmendment as CanonicalSpecAmendment,
)

# Research Service domain models
from generations.gen_04b.services.research.src.domain_models import (
    BottleneckType as ResearchBottleneckType,
    SpecAdjustmentRequest as ResearchSpecAdjustmentRequest,
    SpecAmendment as ResearchSpecAmendment,
)

# Governance Service domain models
from generations.gen_04b.services.governance.src.domain_models import (
    BottleneckType as GovernanceBottleneckType,
    CounterProof as GovernanceCounterProof,
    RFCDispositionStatus as GovernanceRFCDispositionStatus,
    SpecAdjustmentRequest as GovernanceSpecAdjustmentRequest,
    SpecAmendment as GovernanceSpecAmendment,
)


class RFCAdapter:
    """Bijective translation adapter bridging schema differences between Canonical,

    Research, and Governance RFC representations.
    """

    @staticmethod
    def map_status_to_governance(status: Union[CanonicalRFCStatus, str]) -> GovernanceRFCDispositionStatus:
        """Translates canonical RFCStatus to governance RFCDispositionStatus."""
        val = status.value if isinstance(status, CanonicalRFCStatus) else str(status)
        mapping = {
            CanonicalRFCStatus.SUBMITTED.value: GovernanceRFCDispositionStatus.RECEIVED,
            CanonicalRFCStatus.ADJUDICATING.value: GovernanceRFCDispositionStatus.EVALUATING,
            CanonicalRFCStatus.APPROVED.value: GovernanceRFCDispositionStatus.AMENDED,
            CanonicalRFCStatus.REJECTED.value: GovernanceRFCDispositionStatus.COUNTER_PROVEN,
            CanonicalRFCStatus.WITHDRAWN.value: GovernanceRFCDispositionStatus.REJECTED_FINAL,
        }
        return mapping.get(val, GovernanceRFCDispositionStatus.RECEIVED)

    @staticmethod
    def map_status_to_canonical(status: Union[GovernanceRFCDispositionStatus, str]) -> CanonicalRFCStatus:
        """Translates governance RFCDispositionStatus to canonical RFCStatus."""
        val = status.value if isinstance(status, GovernanceRFCDispositionStatus) else str(status)
        mapping = {
            GovernanceRFCDispositionStatus.RECEIVED.value: CanonicalRFCStatus.SUBMITTED,
            GovernanceRFCDispositionStatus.EVALUATING.value: CanonicalRFCStatus.ADJUDICATING,
            GovernanceRFCDispositionStatus.AMENDED.value: CanonicalRFCStatus.APPROVED,
            GovernanceRFCDispositionStatus.COUNTER_PROVEN.value: CanonicalRFCStatus.REJECTED,
            GovernanceRFCDispositionStatus.ESCALATED_TO_HITL.value: CanonicalRFCStatus.ADJUDICATING,
            GovernanceRFCDispositionStatus.REJECTED_FINAL.value: CanonicalRFCStatus.REJECTED,
        }
        return mapping.get(val, CanonicalRFCStatus.SUBMITTED)

    @classmethod
    def to_canonical_request(cls, source: Any) -> CanonicalSpecAdjustmentRequest:
        """Converts any request representation (Canonical, Research, Governance, or dict) to Canonical."""
        if isinstance(source, CanonicalSpecAdjustmentRequest):
            return source

        if isinstance(source, dict):
            status_val = source.get("status")
            if not status_val and "disposition_status" in source:
                status_val = cls.map_status_to_canonical(source["disposition_status"]).value
            return CanonicalSpecAdjustmentRequest(
                request_id=str(source["request_id"]),
                builder_node_id=str(source["builder_node_id"]),
                target_symbol_urn=str(source["target_symbol_urn"]),
                bottleneck_type=CanonicalBottleneckType(
                    source["bottleneck_type"].value if hasattr(source["bottleneck_type"], "value") else source["bottleneck_type"]
                ),
                empirical_evidence=str(source["empirical_evidence"]),
                proposed_delta=str(source["proposed_delta"]),
                preserved_invariants=list(source.get("preserved_invariants", [])),
                status=CanonicalRFCStatus(status_val) if status_val else CanonicalRFCStatus.SUBMITTED,
                submitted_at_unix_ms=int(source.get("submitted_at_unix_ms", int(time.time() * 1000))),
            )

        # Handle object instances
        req_id = getattr(source, "request_id")
        b_node_id = getattr(source, "builder_node_id")
        urn = getattr(source, "target_symbol_urn")
        b_type_raw = getattr(source, "bottleneck_type")
        b_type = CanonicalBottleneckType(b_type_raw.value if hasattr(b_type_raw, "value") else str(b_type_raw))
        evidence = getattr(source, "empirical_evidence")
        delta = getattr(source, "proposed_delta")
        invariants = list(getattr(source, "preserved_invariants", []))

        status = CanonicalRFCStatus.SUBMITTED
        if hasattr(source, "status"):
            st_raw = getattr(source, "status")
            status = CanonicalRFCStatus(st_raw.value if hasattr(st_raw, "value") else str(st_raw))
        elif hasattr(source, "disposition_status"):
            disp_raw = getattr(source, "disposition_status")
            status = cls.map_status_to_canonical(disp_raw)

        submitted_ms = int(getattr(source, "submitted_at_unix_ms", int(time.time() * 1000)))

        instance = CanonicalSpecAdjustmentRequest(
            request_id=req_id,
            builder_node_id=b_node_id,
            target_symbol_urn=urn,
            bottleneck_type=b_type,
            empirical_evidence=evidence,
            proposed_delta=delta,
            preserved_invariants=invariants,
            status=status,
            submitted_at_unix_ms=submitted_ms,
        )
        instance.validate_invariants()
        return instance

    @classmethod
    def to_research_request(cls, source: Any) -> ResearchSpecAdjustmentRequest:
        """Converts any request representation to ResearchSpecAdjustmentRequest."""
        if isinstance(source, ResearchSpecAdjustmentRequest):
            return source

        canonical = cls.to_canonical_request(source)
        instance = ResearchSpecAdjustmentRequest(
            request_id=canonical.request_id,
            builder_node_id=canonical.builder_node_id,
            target_symbol_urn=canonical.target_symbol_urn,
            bottleneck_type=ResearchBottleneckType(canonical.bottleneck_type.value),
            empirical_evidence=canonical.empirical_evidence,
            proposed_delta=canonical.proposed_delta,
            preserved_invariants=list(canonical.preserved_invariants),
        )
        instance.validate_invariants()
        return instance

    @classmethod
    def to_governance_request(cls, source: Any) -> GovernanceSpecAdjustmentRequest:
        """Converts any request representation to GovernanceSpecAdjustmentRequest."""
        if isinstance(source, GovernanceSpecAdjustmentRequest):
            return source

        canonical = cls.to_canonical_request(source)
        gov_status = cls.map_status_to_governance(canonical.status)
        instance = GovernanceSpecAdjustmentRequest(
            request_id=canonical.request_id,
            builder_node_id=canonical.builder_node_id,
            target_symbol_urn=canonical.target_symbol_urn,
            bottleneck_type=GovernanceBottleneckType(canonical.bottleneck_type.value),
            empirical_evidence=canonical.empirical_evidence,
            proposed_delta=canonical.proposed_delta,
            preserved_invariants=list(canonical.preserved_invariants),
            disposition_status=gov_status,
            submitted_at_unix_ms=canonical.submitted_at_unix_ms,
        )
        instance.validate_invariants()
        return instance

    @classmethod
    def to_canonical_counter_proof(cls, source: Any) -> CanonicalCounterProof:
        """Converts CounterProof representation to CanonicalCounterProof."""
        if isinstance(source, CanonicalCounterProof):
            return source

        if isinstance(source, dict):
            return CanonicalCounterProof(
                counter_proof_id=str(source["counter_proof_id"]),
                request_id=str(source["request_id"]),
                violated_axioms=list(source.get("violated_axioms", [])),
                z3_unsat_core=source.get("z3_unsat_core"),
                counter_example_model=dict(source.get("counter_example_model", {})),
                adjudicator_node_id=str(source.get("adjudicator_node_id", "node_research_kernel")),
            )

        if isinstance(source, str):
            # Parse string as JSON or generate synthetic proof container
            try:
                parsed = json.loads(source)
                if isinstance(parsed, dict) and "counter_proof_id" in parsed:
                    return cls.to_canonical_counter_proof(parsed)
            except Exception:
                pass
            return CanonicalCounterProof(
                counter_proof_id=f"cp_str_{uuid.uuid4().hex[:8]}",
                request_id="req_unknown",
                violated_axioms=[source],
                z3_unsat_core=source,
                counter_example_model={},
                adjudicator_node_id="node_research_kernel",
            )

        # Governance object
        instance = CanonicalCounterProof(
            counter_proof_id=getattr(source, "counter_proof_id"),
            request_id=getattr(source, "request_id"),
            violated_axioms=list(getattr(source, "violated_axioms", [])),
            z3_unsat_core=getattr(source, "z3_unsat_core", None),
            counter_example_model=dict(getattr(source, "counter_example_model", {})),
            adjudicator_node_id=getattr(source, "adjudicator_node_id", "node_governance_kernel"),
        )
        instance.validate_invariants()
        return instance

    @classmethod
    def to_governance_counter_proof(cls, source: Any) -> GovernanceCounterProof:
        """Converts CounterProof representation to GovernanceCounterProof."""
        if isinstance(source, GovernanceCounterProof):
            return source

        if isinstance(source, dict):
            return GovernanceCounterProof(
                counter_proof_id=str(source["counter_proof_id"]),
                request_id=str(source["request_id"]),
                violated_axioms=list(source.get("violated_axioms", [])),
                z3_unsat_core=source.get("z3_unsat_core"),
                counter_example_model=dict(source.get("counter_example_model", {})),
                adjudicator_node_id=str(source.get("adjudicator_node_id", "node_governance_kernel")),
                generated_at_unix_ms=int(source.get("generated_at_unix_ms", int(time.time() * 1000))),
            )

        canonical = cls.to_canonical_counter_proof(source)
        instance = GovernanceCounterProof(
            counter_proof_id=canonical.counter_proof_id,
            request_id=canonical.request_id,
            violated_axioms=list(canonical.violated_axioms),
            z3_unsat_core=canonical.z3_unsat_core,
            counter_example_model=dict(canonical.counter_example_model),
            adjudicator_node_id=canonical.adjudicator_node_id,
            generated_at_unix_ms=int(getattr(source, "generated_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance

    @classmethod
    def to_canonical_amendment(cls, source: Any) -> CanonicalSpecAmendment:
        """Converts any SpecAmendment representation to CanonicalSpecAmendment."""
        if isinstance(source, CanonicalSpecAmendment):
            return source

        if isinstance(source, dict):
            cp_raw = source.get("rejection_counter_proof")
            cp_obj = None
            if cp_raw is not None:
                if isinstance(cp_raw, dict):
                    cp_obj = CanonicalCounterProof.from_dict(cp_raw)
                elif isinstance(cp_raw, str):
                    cp_obj = cp_raw

            return CanonicalSpecAmendment(
                amendment_id=str(source["amendment_id"]),
                request_id=str(source["request_id"]),
                is_approved=bool(source["is_approved"]),
                adjudicator_signature=str(source["adjudicator_signature"]),
                amended_contract_ir_delta=str(source.get("amended_contract_ir_delta", "")),
                rejection_counter_proof=cp_obj,
                adjudicated_at_unix_ms=int(source.get("adjudicated_at_unix_ms", int(time.time() * 1000))),
            )

        amend_id = getattr(source, "amendment_id")
        req_id = getattr(source, "request_id")
        approved = bool(getattr(source, "is_approved"))
        sig = getattr(source, "adjudicator_signature")
        delta = str(getattr(source, "amended_contract_ir_delta", ""))
        adjudicated_ms = int(getattr(source, "adjudicated_at_unix_ms", int(time.time() * 1000)))

        raw_proof = getattr(source, "rejection_counter_proof", None)
        counter_proof: Optional[Union[CanonicalCounterProof, str]] = None
        if raw_proof is not None:
            if isinstance(raw_proof, str):
                counter_proof = raw_proof
            elif hasattr(raw_proof, "to_dict"):
                counter_proof = cls.to_canonical_counter_proof(raw_proof)
            elif isinstance(raw_proof, dict):
                counter_proof = CanonicalCounterProof.from_dict(raw_proof)

        instance = CanonicalSpecAmendment(
            amendment_id=amend_id,
            request_id=req_id,
            is_approved=approved,
            adjudicator_signature=sig,
            amended_contract_ir_delta=delta,
            rejection_counter_proof=counter_proof,
            adjudicated_at_unix_ms=adjudicated_ms,
        )
        instance.validate_invariants()
        return instance

    @classmethod
    def to_research_amendment(cls, source: Any) -> ResearchSpecAmendment:
        """Converts any SpecAmendment representation to ResearchSpecAmendment."""
        if isinstance(source, ResearchSpecAmendment):
            return source

        canonical = cls.to_canonical_amendment(source)
        proof_str: Optional[str] = None
        if canonical.rejection_counter_proof is not None:
            if isinstance(canonical.rejection_counter_proof, str):
                proof_str = canonical.rejection_counter_proof
            elif hasattr(canonical.rejection_counter_proof, "to_dict"):
                proof_str = json.dumps(canonical.rejection_counter_proof.to_dict())
            else:
                proof_str = str(canonical.rejection_counter_proof)

        instance = ResearchSpecAmendment(
            amendment_id=canonical.amendment_id,
            request_id=canonical.request_id,
            is_approved=canonical.is_approved,
            adjudicator_signature=canonical.adjudicator_signature,
            amended_contract_ir_delta=canonical.amended_contract_ir_delta,
            rejection_counter_proof=proof_str,
        )
        instance.validate_invariants()
        return instance

    @classmethod
    def to_governance_amendment(cls, source: Any) -> GovernanceSpecAmendment:
        """Converts any SpecAmendment representation to GovernanceSpecAmendment."""
        if isinstance(source, GovernanceSpecAmendment):
            return source

        canonical = cls.to_canonical_amendment(source)
        gov_proof: Optional[GovernanceCounterProof] = None
        if canonical.rejection_counter_proof is not None:
            if isinstance(canonical.rejection_counter_proof, str):
                gov_proof = GovernanceCounterProof(
                    counter_proof_id=f"cp_{uuid.uuid4().hex[:8]}",
                    request_id=canonical.request_id,
                    violated_axioms=[canonical.rejection_counter_proof],
                    z3_unsat_core=canonical.rejection_counter_proof,
                    counter_example_model={},
                    adjudicator_node_id="node_governance_kernel",
                    generated_at_unix_ms=canonical.adjudicated_at_unix_ms,
                )
            else:
                gov_proof = cls.to_governance_counter_proof(canonical.rejection_counter_proof)

        instance = GovernanceSpecAmendment(
            amendment_id=canonical.amendment_id,
            request_id=canonical.request_id,
            is_approved=canonical.is_approved,
            adjudicator_signature=canonical.adjudicator_signature,
            amended_contract_ir_delta=canonical.amended_contract_ir_delta,
            rejection_counter_proof=gov_proof,
            adjudicated_at_unix_ms=canonical.adjudicated_at_unix_ms,
        )
        instance.validate_invariants()
        return instance
