#!/usr/bin/env python3
"""Adversarial Plan Guard (`scripts/adversarial_plan_guard.py`).

Enforces:
- [L1-G4B-009] Pre-Proposal Adversarial Red Team Certification Gate.
- [INV-G4B-REDTEAM-001] Falsification-Driven Plan Review (Anti-Cosmetic Critique).

Intercepts `ask_question` tool calls when presenting project proposals:
1. Detects if the prompt or proposals artifact presents architectural options.
2. Inspects `project_proposals.md` in the artifact directory.
3. Asserts that the dossier contains a verified Adversarial Red Team Certification Witness:
   - Must document >= 2 reproducible failure modes / critical vulnerabilities.
   - Prohibits superficial hand-waving (e.g. "mitigated by clean architecture", "no risks").
   - Requires every failure mode to link to a concrete architectural mitigation.
4. Hard-blocks with `{"decision": "deny"}` if adversarial rigor is absent.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional


COSMETIC_PHRASES = [
    "mitigated by clean architecture",
    "no significant risks",
    "no critical vulnerabilities",
    "minimal risk",
    "trivially handled",
    "handled by standard best practices",
]


def evaluate_proposals_adversarial_rigor(proposals_content: str) -> tuple[bool, str]:
    """Evaluates whether the proposal document contains a genuine, non-cosmetic adversarial review."""
    stripped = proposals_content.strip()
    if not stripped or len(stripped) < 40:
        return False, "Proposal document is too short or empty."

    # Check for cosmetic hand-waving first
    lower_content = proposals_content.lower()
    for phrase in COSMETIC_PHRASES:
        if phrase in lower_content:
            return False, (
                f"Cosmetic review detected: found phrase '{phrase}'. "
                "The adversarial review must identify concrete, reproducible failure modes and specify "
                "exact architectural mitigations, not hand-waving."
            )

    # Check for adversarial red team section or witness
    has_red_team_section = bool(
        re.search(r"Adversarial\s+(?:Risk|Red\s+Team)", proposals_content, re.IGNORECASE)
    )
    has_witness = bool(
        re.search(r"Adversarial\s+(?:Red\s+Team\s+)?Certification\s+Witness", proposals_content, re.IGNORECASE)
    )

    if not has_red_team_section and not has_witness:
        return False, (
            "No 'Adversarial Risk & Red Team Critique' section or 'Adversarial Red Team Certification Witness' "
            "found in project_proposals.md. Proposals must undergo rigorous adversarial stress-testing."
        )

    # Check for failure scenarios / vulnerability itemization
    vuln_matches = re.findall(
        r"(?:VULN-|Stress-Test|Failure\s+Mode|Attack\s+Vector|Scenario\s+\d+|Critique\s+\d+)",
        proposals_content,
        re.IGNORECASE,
    )
    if len(vuln_matches) < 2:
        return False, (
            f"Insufficient adversarial depth: found only {len(vuln_matches)} failure scenarios. "
            "At least 2 concrete, falsifiable failure modes (e.g. scale contention, partition, schema corruption) "
            "are required before a proposal can be presented."
        )

    # Check for mitigations
    mitigation_matches = re.findall(
        r"(?:mitigation|mitigated|countermeasure|fail-safe|circuit\s+breaker)",
        proposals_content,
        re.IGNORECASE,
    )
    if len(mitigation_matches) < 2:
        return False, (
            "Identified failure modes lack explicit mitigations. Every adversarial vulnerability "
            "must link directly to a structural mitigation in the proposed architecture."
        )

    return True, "Adversarial certification verified."


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({"decision": "allow"}))
            return

        payload = json.loads(raw_input)
    except Exception as e:
        sys.stderr.write(f"AdversarialPlanGuard stdin error: {e}\n")
        print(json.dumps({"decision": "allow"}))
        return

    tool_call = payload.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    tool_args = tool_call.get("args", {})
    artifact_dir = payload.get("artifactDirectoryPath", "")

    # Only inspect ask_question calls
    if tool_name != "ask_question":
        print(json.dumps({"decision": "allow"}))
        return

    questions = tool_args.get("questions", [])
    if not questions:
        print(json.dumps({"decision": "allow"}))
        return

    # Check if this question is presenting an option selection or proposal approval
    is_proposal_gate = False
    for q in questions:
        q_text = (q.get("question", "") + " " + " ".join(q.get("options", []))).lower()
        if any(keyword in q_text for keyword in ["proceed with option", "select an option", "choose option", "proposal", "architecture"]):
            is_proposal_gate = True
            break

    if not is_proposal_gate:
        # Standard clarification or dialogue question; allow
        print(json.dumps({"decision": "allow"}))
        return

    # This is a proposal selection gate. Validate project_proposals.md
    if not artifact_dir:
        print(json.dumps({
            "decision": "deny",
            "reason": "ADVERSARIAL PLAN GATE VIOLATION: No artifactDirectoryPath provided to verify proposal dossier."
        }))
        return

    proposals_file = Path(artifact_dir) / "project_proposals.md"
    if not proposals_file.exists():
        print(json.dumps({
            "decision": "deny",
            "reason": (
                "ADVERSARIAL PLAN GATE VIOLATION [NEG-GOV-GATE-001]: "
                "project_proposals.md does not exist in the artifact directory. "
                "You must physically emit the proposal dossier before asking the user for option selection."
            )
        }))
        return

    try:
        content = proposals_file.read_text(encoding="utf-8")
        is_rigorous, msg = evaluate_proposals_adversarial_rigor(content)
        if not is_rigorous:
            print(json.dumps({
                "decision": "deny",
                "reason": f"ADVERSARIAL PLAN GATE REJECTION: {msg}"
            }))
            return
    except Exception as e:
        print(json.dumps({
            "decision": "deny",
            "reason": f"ADVERSARIAL PLAN GATE ERROR: Failed to read project_proposals.md: {e}"
        }))
        return

    # Passed adversarial gate
    print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
