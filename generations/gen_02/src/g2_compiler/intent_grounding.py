"""Mandatory Human Intent Elicitation & Grounding Boundary [L1-G2-005 & NEG-G2-001].

Empirical Epistemology & Anti-Verification-Illusion Principle:
    Compile(App) ⟹ Witness(HumanIntent) ∈ trace/ ∧ Status(Witness) == SIGNED_OFF
    No non-generator application may compile without an explicit, verifiable
    HumanIntentWitness establishing real-world human workflow, pain points, and utility function.
    Direct application compilation without prior human elicitation aborts immediately with
    GenerationalRegressionFault (Inherited LES-G1-001 / NEG-G2-001).
"""

from pathlib import Path
from typing import Dict, List, Optional
import hashlib
import json
import time

from g2_compiler.types import GenerationalRegressionFault, HumanIntentWitness


class HumanIntentGroundingGate:
    """Enforces the Phase 0 Human Intent Elicitation gate before application compilation."""

    def __init__(self, trace_dir: Optional[Path] = None):
        self.trace_dir = trace_dir or Path("trace")
        self._witness_registry: Dict[str, HumanIntentWitness] = {}

    def register_witness(self, witness: HumanIntentWitness) -> None:
        """Registers a verified human intent witness."""
        self._witness_registry[witness.application_id] = witness

    def create_witness(
        self,
        application_id: str,
        persona_name: str,
        jtbd_summary: str,
        daily_workflow: str,
        utility_metric_definition: str,
        signed_off_by_human: bool,
    ) -> HumanIntentWitness:
        """Constructs a cryptographic human intent witness."""
        now = time.time()
        witness_id = f"witness_{application_id}_{int(now)}"
        message = (
            f"{witness_id}|{application_id}|{persona_name}|"
            f"{jtbd_summary}|{daily_workflow}|{utility_metric_definition}|{signed_off_by_human}|{now}"
        )
        witness_hash = hashlib.sha256(message.encode("utf-8")).hexdigest()

        witness = HumanIntentWitness(
            witness_id=witness_id,
            application_id=application_id,
            persona_name=persona_name,
            jtbd_summary=jtbd_summary,
            daily_workflow=daily_workflow,
            utility_metric_definition=utility_metric_definition,
            signed_off_by_human=signed_off_by_human,
            signed_at=now,
            witness_hash=witness_hash,
        )
        self.register_witness(witness)
        return witness

    def verify_elicitation_gate(self, application_id: str) -> HumanIntentWitness:
        """Verifies that an application has an active, signed human intent witness.
        
        Raises GenerationalRegressionFault if the witness is missing or unsigned,
        enforcing NEG-G2-001 and NEG-G2-002.
        """
        # 1. Check in-memory registry
        witness = self._witness_registry.get(application_id)

        # 2. If not in memory, check trace/ directory on disk
        if witness is None:
            witness = self._search_trace_for_witness(application_id)

        if witness is None:
            raise GenerationalRegressionFault(
                f"[NEG-G2-001 VETO] Compilation of application '{application_id}' rejected! "
                f"No HumanIntentWitness found. Mandate: You must elicit user workflow and JTBD "
                f"from the human architect before compiling non-generator code (Inherited LES-G1-001)."
            )

        if not witness.signed_off_by_human:
            raise GenerationalRegressionFault(
                f"[NEG-G2-002 VETO] Compilation of application '{application_id}' rejected! "
                f"HumanIntentWitness '{witness.witness_id}' exists but has not been signed off by the human architect."
            )

        return witness

    def _search_trace_for_witness(self, application_id: str) -> Optional[HumanIntentWitness]:
        """Scans trace/ directory for elicitation files matching application_id."""
        if not self.trace_dir.exists():
            return None

        # Look for trace/intent_elicitation_{application_id}.json or trace/intent_elicitation.json
        candidate_files = [
            self.trace_dir / f"intent_elicitation_{application_id}.json",
            self.trace_dir / "intent_elicitation.json",
        ]

        for c_file in candidate_files:
            if c_file.exists():
                try:
                    with open(c_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if data.get("application_id") == application_id:
                        return HumanIntentWitness(
                            witness_id=data.get("witness_id", "witness_disk"),
                            application_id=data.get("application_id"),
                            persona_name=data.get("persona_name", "Unknown"),
                            jtbd_summary=data.get("jtbd_summary", ""),
                            daily_workflow=data.get("daily_workflow", ""),
                            utility_metric_definition=data.get("utility_metric_definition", ""),
                            signed_off_by_human=data.get("signed_off_by_human", False),
                            signed_at=data.get("signed_at", time.time()),
                            witness_hash=data.get("witness_hash", "hash_disk"),
                        )
                except Exception:
                    continue

        return None
