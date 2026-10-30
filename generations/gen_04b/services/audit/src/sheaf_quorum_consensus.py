"""Sheaf-Quorum Adversarial Consensus Engine (`soc_g4b_audit`).

Enforces:
- Invariant [NEG-PRIMITIVE-001]: Centralized coordinator or leader node is strictly forbidden.
- 2-of-3 Non-Blocking Decentralized Consensus over the Peer Verification Triad:
  1. node_hermetic_sentry (SentrySyntax)
  2. node_smt_oracle (OracleSMT)
  3. node_chaos_adversary (AdversaryChaos)
- Asymmetric Sheaf Boundary Consensus: Consensus threshold is satisfied when >= 2 of 3 peer nodes certify.
- Emits cryptographically signed `QuorumConsensusWitness`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from .domain_models import (
    AuditDomainInvariantViolation,
    ByzantineFuzzReport,
    HermeticAuditReport,
    MorphismCheckStatus,
    QuorumConsensusWitness,
    QuorumVerdict,
    SMTModelCheckResult,
)


@dataclass
class PeerVote:
    """Individual cryptographic vote emitted by a verification peer."""
    node_id: str
    leaf_id: str
    vote_passed: bool
    voted_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    signature: str = ""

    def compute_hash(self) -> str:
        payload = f"{self.node_id}:{self.leaf_id}:{self.vote_passed}:{self.voted_at_unix_ms}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class SheafQuorumConsensusEngine:
    """Adjudicates 2-of-3 non-blocking peer consensus across SentrySyntax, OracleSMT, and AdversaryChaos."""

    PEER_NODES = {
        "node_hermetic_sentry",
        "node_smt_oracle",
        "node_chaos_adversary",
    }

    def __init__(self, anchor_node_id: str = "node_merkle_sheaf") -> None:
        self.anchor_node_id = anchor_node_id
        # In-flight vote ballot box: leaf_id -> {node_id -> PeerVote}
        self._ballots: Dict[str, Dict[str, PeerVote]] = {}

    def cast_peer_vote(
        self,
        node_id: str,
        leaf_id: str,
        vote_passed: bool,
        signature: Optional[str] = None,
    ) -> PeerVote:
        """Casts an immutable cryptographic vote from a peer node."""
        if node_id not in self.PEER_NODES:
            raise AuditDomainInvariantViolation(
                f"Unauthorized node '{node_id}' cannot vote in Sheaf Quorum Triad. Allowed: {self.PEER_NODES}"
            )
        if not leaf_id:
            raise AuditDomainInvariantViolation("leaf_id must not be empty.")

        if leaf_id not in self._ballots:
            self._ballots[leaf_id] = {}

        sig = signature or hashlib.sha256(f"sig_{node_id}_{leaf_id}_{vote_passed}".encode("utf-8")).hexdigest()
        vote = PeerVote(
            node_id=node_id,
            leaf_id=leaf_id,
            vote_passed=vote_passed,
            signature=sig,
        )
        self._ballots[leaf_id][node_id] = vote
        return vote

    def evaluate_quorum(self, leaf_id: str) -> QuorumConsensusWitness:
        """Evaluates votes in the ballot box and adjudicates the quorum verdict."""
        if leaf_id not in self._ballots or len(self._ballots[leaf_id]) == 0:
            raise AuditDomainInvariantViolation(f"No votes recorded for leaf_id '{leaf_id}'.")

        ballot = self._ballots[leaf_id]
        sentry_vote = ballot.get("node_hermetic_sentry")
        smt_vote = ballot.get("node_smt_oracle")
        chaos_vote = ballot.get("node_chaos_adversary")

        sentry_pass = sentry_vote.vote_passed if sentry_vote else False
        smt_pass = smt_vote.vote_passed if smt_vote else False
        chaos_pass = chaos_vote.vote_passed if chaos_vote else False

        votes = [
            ("node_hermetic_sentry", sentry_pass),
            ("node_smt_oracle", smt_pass),
            ("node_chaos_adversary", chaos_pass),
        ]

        pass_count = sum(1 for _, passed in votes if passed)
        dissenting_nodes = [node for node, passed in votes if not passed]
        consensus_ratio = pass_count / 3.0

        if pass_count == 3:
            verdict = QuorumVerdict.UNANIMOUS_PASS
        elif pass_count == 2:
            verdict = QuorumVerdict.QUORUM_PASS
        elif pass_count == 1:
            verdict = QuorumVerdict.SPLIT_FAIL
        else:
            verdict = QuorumVerdict.UNANIMOUS_FAIL

        witness_id = f"wit_quorum_{uuid.uuid4().hex[:12]}"
        witness = QuorumConsensusWitness(
            witness_id=witness_id,
            leaf_id=leaf_id,
            verdict=verdict,
            sentry_syntax_vote=sentry_pass,
            oracle_smt_vote=smt_pass,
            adversary_chaos_vote=chaos_pass,
            consensus_ratio=consensus_ratio,
            dissenting_nodes=dissenting_nodes,
        )
        witness.consensus_hash = witness.compute_hash()
        witness.validate_invariants()
        return witness

    def adjudicate_triad(
        self,
        hermetic_report: HermeticAuditReport,
        smt_result: SMTModelCheckResult,
        fuzz_report: ByzantineFuzzReport,
    ) -> QuorumConsensusWitness:
        """Directly adjudicates the full 3-peer verification outputs into a signed consensus witness."""
        hermetic_report.validate_invariants()
        smt_result.validate_invariants()
        fuzz_report.validate_invariants()

        leaf_id = hermetic_report.leaf_id
        if smt_result.leaf_id != leaf_id or fuzz_report.leaf_id != leaf_id:
            raise AuditDomainInvariantViolation(
                f"Mismatched leaf IDs in peer reports: {leaf_id} vs {smt_result.leaf_id} vs {fuzz_report.leaf_id}"
            )

        # Peer 1: SentrySyntax
        sentry_pass = hermetic_report.is_hermetic and len(hermetic_report.violations) == 0
        self.cast_peer_vote("node_hermetic_sentry", leaf_id, sentry_pass)

        # Peer 2: OracleSMT
        smt_pass = (
            smt_result.morphism_status == MorphismCheckStatus.PROVEN_VALID
            and smt_result.is_deadlock_free
        )
        self.cast_peer_vote("node_smt_oracle", leaf_id, smt_pass)

        # Peer 3: AdversaryChaos
        chaos_pass = (fuzz_report.trap_rate == 1.0 and fuzz_report.unhandled_faults == 0)
        self.cast_peer_vote("node_chaos_adversary", leaf_id, chaos_pass)

        return self.evaluate_quorum(leaf_id)
