r"""Pass 0: Multi-Agent Provenance & Context Separation Evaluator ($S_{prov}$, Weight = 15%).

Enforces:
- Verification of genuine multi-agent execution witnesses ([L1-G3B-014], [L1-G4B-001]).
- Anti-Collusion Invariant: Asserts that the conversation context that authored implementation
  code is strictly disjoint from the conversation context that authored the adversarial tests
  (Author(Code) != Author(Tests)).
- Context Separation: Asserts that >= 3 distinct subagent conversations were executed
  for multi-agent compilation (Brain != Synthesizer != Adversarial QA).
- Transcript Physical Liveness: Asserts that each declared `conversation_id` physically
  resolves to a non-empty `transcript.jsonl` on disk, eliminating fabricated mock UUIDs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from ..domain_models import AblationMode, BenchmarkArchetype, EvaluationPassResult


class ProvenanceViolation(Exception):
    """Base exception for provenance and context separation violations."""
    pass


class MonolithicSimulationViolation(ProvenanceViolation):
    """Raised when a candidate claims multi-agent synthesis but was produced by a single monolithic agent."""
    pass


class AgentCollusionViolation(ProvenanceViolation):
    """Raised when the builder agent and tester agent share the same conversation context."""
    pass


class FabricatedWitnessViolation(ProvenanceViolation):
    """Raised when declared conversation IDs do not correspond to physical transcripts on disk."""
    pass


class ProvenanceEvaluator:
    """Evaluates Multi-Agent Provenance & Context Separation as a Binary Gatekeeper."""

    def __init__(
        self,
        weight: float = 0.0,
        app_data_dir: Optional[Path] = None,
        min_multi_agent_count: int = 3,
    ) -> None:
        self.weight = weight
        if app_data_dir:
            self.app_data_dir = Path(app_data_dir).resolve()
        else:
            self.app_data_dir = Path(os.environ.get("ANTIGRAVITY_APP_DATA_DIR", Path.home() / ".gemini" / "antigravity")).resolve()
        self.min_multi_agent_count = min_multi_agent_count

    def evaluate(
        self,
        app_dir: Path,
        archetype: Optional[BenchmarkArchetype] = None,
        mode: AblationMode = AblationMode.FULL_G4B,
        provenance_manifest: Optional[Dict[str, Any]] = None,
    ) -> EvaluationPassResult:
        """Evaluates whether the candidate application was synthesized under certified context separation."""
        app_dir = Path(app_dir).resolve()

        # 1. Load Provenance Manifest
        manifest = provenance_manifest
        if manifest is None:
            manifest = self._load_manifest_from_disk(app_dir)

        # If no manifest exists at all
        if manifest is None:
            if mode in (AblationMode.FULL_G4B, AblationMode.WO_AST_AUDITORS, AblationMode.WO_CONTRACTS_SMT):
                return EvaluationPassResult(
                    pass_name="provenance",
                    weight=self.weight,
                    raw_score=0.0,
                    weighted_score=0.0,
                    details={
                        "error": "MonolithicSimulationViolation: No synthesis provenance manifest found for multi-agent candidate",
                        "violations": ["MISSING_PROVENANCE_MANIFEST"],
                    },
                    passed=False,
                )
            else:
                # Vanilla / Flat prompt modes may run without multi-agent manifests if unconfigured
                return EvaluationPassResult(
                    pass_name="provenance",
                    weight=self.weight,
                    raw_score=100.0,
                    weighted_score=round(100.0 * self.weight, 2),
                    details={"status": "unconstrained_control_mode", "mode": mode.value},
                    passed=True,
                )

        # 2. Evaluate Manifest Content
        is_multi_agent = manifest.get("is_multi_agent", (mode == AblationMode.FULL_G4B))
        subagents: List[Dict[str, Any]] = manifest.get("subagents", [])
        violations: List[str] = []
        details_log: List[str] = []

        # Check subagent count for multi-agent modes
        if is_multi_agent:
            if len(subagents) < self.min_multi_agent_count:
                violations.append(
                    f"INSUFFICIENT_SUBAGENTS: Found {len(subagents)} subagents, "
                    f"expected >= {self.min_multi_agent_count} for multi-agent mesh"
                )
            else:
                details_log.append(f"Subagent count requirement met: {len(subagents)} distinct roles")

            # Check distinct conversation IDs
            cids: List[str] = [str(s.get("conversation_id", "")).strip() for s in subagents if s.get("conversation_id")]
            unique_cids: Set[str] = set(cids)
            if len(unique_cids) < len(cids):
                violations.append(
                    f"COLLUSION_DETECTED: Duplicate conversation IDs found among subagents: {cids}"
                )
            elif len(unique_cids) >= self.min_multi_agent_count:
                details_log.append(f"Context separation verified: {len(unique_cids)} distinct conversation contexts")

            # Anti-Collusion: Builder != Tester
            builder_cid = None
            tester_cid = None
            for s in subagents:
                role = str(s.get("cognitive_role", s.get("role", ""))).upper()
                cid = str(s.get("conversation_id", "")).strip()
                # Use exact cognitive roles or unambiguous keywords
                is_qa = any(k in role for k in ("QA", "TESTER", "ADVERSARIAL", "AUDIT", "VERIF"))
                is_builder = any(k in role for k in ("BUILDER", "SYNTHESIZ", "CODE_EMIT")) or (
                    "ENGINE" in role and not is_qa
                )
                if is_builder:
                    builder_cid = cid
                if is_qa:
                    tester_cid = cid

            if builder_cid and tester_cid and builder_cid == tester_cid:
                violations.append(
                    f"SELF_GRADING_COLLUSION: Builder agent and QA agent share the same conversation context ({builder_cid})"
                )
            elif builder_cid and tester_cid:
                details_log.append(f"Anti-collusion verified: Builder ({builder_cid[:8]}) != QA ({tester_cid[:8]})")

        # 3. Transcript Physical Liveness Verification
        transcript_checks: List[Dict[str, Any]] = []
        for s in subagents:
            cid = str(s.get("conversation_id", "")).strip()
            role = s.get("role", "unknown")
            if not cid or cid.lower() in ("none", "mock", "placeholder", "fake"):
                violations.append(f"FABRICATED_WITNESS: Role '{role}' has invalid conversation_id='{cid}'")
                continue

            # Verify physical transcript file on disk
            transcript_path = self.app_data_dir / "brain" / cid / ".system_generated" / "logs" / "transcript.jsonl"
            custom_uri = s.get("transcript_uri")
            if custom_uri and custom_uri.startswith("file://"):
                candidate_path = Path(custom_uri[7:])
                if candidate_path.exists():
                    transcript_path = candidate_path

            if not transcript_path.exists():
                violations.append(f"MISSING_TRANSCRIPT: Transcript for conversation '{cid}' not found at {transcript_path}")
                transcript_checks.append({"conversation_id": cid, "role": role, "found": False})
            else:
                byte_size = transcript_path.stat().st_size
                if byte_size == 0:
                    violations.append(f"EMPTY_TRANSCRIPT: Transcript for conversation '{cid}' is zero-byte")
                    transcript_checks.append({"conversation_id": cid, "role": role, "found": True, "bytes": 0})
                else:
                    transcript_checks.append({"conversation_id": cid, "role": role, "found": True, "bytes": byte_size})
                    details_log.append(f"Transcript grounded: {role} ({cid[:8]}... - {byte_size} bytes)")

        # Calculate score
        if violations:
            raw_score = 0.0
            passed = False
        else:
            raw_score = 100.0
            passed = True

        weighted_score = round(raw_score * self.weight, 2)

        return EvaluationPassResult(
            pass_name="provenance",
            weight=self.weight,
            raw_score=raw_score,
            weighted_score=weighted_score,
            details={
                "is_multi_agent": is_multi_agent,
                "subagents_evaluated": len(subagents),
                "violations": violations,
                "log": details_log,
                "transcript_checks": transcript_checks,
            },
            passed=passed,
        )

    def _load_manifest_from_disk(self, app_dir: Path) -> Optional[Dict[str, Any]]:
        """Searches candidate directory and scratch parents for synthesis manifests."""
        candidate_paths = [
            app_dir / "synthesis_manifest.json",
            app_dir / "provenance.json",
            app_dir.parent / f"{app_dir.name}_manifest.json",
        ]
        for p in candidate_paths:
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
        return None
