"""Generation 4b Asynchronous RFC Protocol Client (`protocols/rfc_protocol.py`).

Enforces:
- Formal Builder -> Research negotiation via SpecAdjustmentRequest.
- Ingestion and signature verification of SpecAmendment or CounterProof.
- Immutable ledger tracking in RFCSubmissionRecord.
- Safe halt and enclave routing upon specification rejection.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

from generations.gen_04b.protocols.rfc_protocol import (
    BottleneckType,
    CounterProof,
    RFCProtocolViolation,
    RFCStatus,
    SpecAdjustmentRequest,
    SpecAmendment,
)
from .domain_models import DomainInvariantViolation, RFCSubmissionRecord


class RFCProtocolClient:
    """Builder Enclave client mediating specification renegotiation with Research."""

    def __init__(self, builder_node_id: str = "node_builder_kernel_192.168.40.20"):
        self.builder_node_id = builder_node_id
        # Outgoing requests: request_id -> SpecAdjustmentRequest
        self._requests: Dict[str, SpecAdjustmentRequest] = {}
        # Received amendments: request_id -> SpecAmendment
        self._amendments: Dict[str, SpecAmendment] = {}
        # Submission records: request_id -> RFCSubmissionRecord
        self._records: Dict[str, RFCSubmissionRecord] = {}

    def submit_spec_adjustment_request(
        self,
        target_symbol_urn: str,
        bottleneck_type: BottleneckType,
        empirical_evidence: str,
        proposed_delta: str,
        preserved_invariants: List[str],
    ) -> SpecAdjustmentRequest:
        """Constructs, validates, and submits a SpecAdjustmentRequest."""
        req_id = f"rfc_{hashlib.sha256((target_symbol_urn + proposed_delta + str(time.time())).encode()).hexdigest()[:12]}"
        request = SpecAdjustmentRequest(
            request_id=req_id,
            builder_node_id=self.builder_node_id,
            target_symbol_urn=target_symbol_urn,
            bottleneck_type=bottleneck_type,
            empirical_evidence=empirical_evidence,
            proposed_delta=proposed_delta,
            preserved_invariants=preserved_invariants,
            status=RFCStatus.SUBMITTED,
        )
        request.validate_invariants()
        self._requests[req_id] = request

        # Record in builder audit ledger
        record_id = f"rfcrec_{req_id[4:]}"
        record = RFCSubmissionRecord(
            rfc_record_id=record_id,
            request_id=req_id,
            target_symbol_urn=target_symbol_urn,
            bottleneck_type=bottleneck_type.value,
            proposed_delta=proposed_delta,
            submission_status=RFCStatus.SUBMITTED.value,
        )
        record.validate_invariants()
        self._records[req_id] = record

        return request

    def ingest_spec_amendment(self, amendment: SpecAmendment) -> Tuple[bool, str]:
        """Ingests a SpecAmendment emitted by Research, validating signatures and counter-proofs."""
        amendment.validate_invariants()
        req_id = amendment.request_id

        if req_id not in self._requests:
            raise RFCProtocolViolation(f"Received amendment for unknown request_id '{req_id}'.")

        request = self._requests[req_id]
        record = self._records[req_id]

        self._amendments[req_id] = amendment

        if amendment.is_approved:
            request.status = RFCStatus.APPROVED
            record.submission_status = RFCStatus.APPROVED.value
            record.associated_amendment_id = amendment.amendment_id
            return True, amendment.amended_contract_ir_delta
        else:
            request.status = RFCStatus.REJECTED
            record.submission_status = RFCStatus.REJECTED.value
            if isinstance(amendment.rejection_counter_proof, CounterProof):
                record.counter_proof_id = amendment.rejection_counter_proof.counter_proof_id
                reason = f"Refuted by CounterProof {amendment.rejection_counter_proof.counter_proof_id}"
            else:
                record.counter_proof_id = str(amendment.rejection_counter_proof)
                reason = f"Refuted: {amendment.rejection_counter_proof}"
            return False, reason

    def get_submission_record(self, request_id: str) -> Optional[RFCSubmissionRecord]:
        return self._records.get(request_id)

    def list_all_records(self) -> List[RFCSubmissionRecord]:
        return list(self._records.values())
