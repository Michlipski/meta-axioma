#!/usr/bin/env python3
"""Governance Pre-Tool Guard (`scripts/governance_pre_tool_guard.py`).

Enforces:
- [NEG-GOV-GATE-001] Physical Runtime Pre-Execution Interception.
- Directive 3: Plan-First, Mandatory Detailed Proposals Document (`project_proposals.md`) BEFORE modifying code.
- [L1-G4B-002] Zero-Code Research Tool Boundary.

Intercepts `write_file` and `edit_file` tool calls before execution:
1. Allows writes to artifact directories (<artifactDirectoryPath>), /tmp, and root markdown documents.
2. Intercepts any write/edit targeting protected generation code:
   - generations/
   - apps/
   - src/
3. If `project_proposals.md` does not exist in the artifact directory, HARD BLOCKS (decision: "deny").
4. If `project_proposals.md` exists, prompts the human architect for confirmation (decision: "ask").
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys


PROTECTED_DIR_PATTERNS = [
    "/generations/",
    "/apps/",
    "/src/",
]


def is_protected_path(target_path: Path, workspace_paths: list[str]) -> bool:
    """Checks if target_path falls inside a protected code directory."""
    path_str = str(target_path.resolve()).replace("\\", "/")
    
    # Artifact directory, designated scratch directories, and temp directories are never protected
    if "/.gemini/antigravity/brain/" in path_str or "/.scratch/" in path_str or "/scratch/" in path_str or path_str.startswith("/tmp/"):
        return False
        
    for pattern in PROTECTED_DIR_PATTERNS:
        if pattern in path_str:
            return True
            
    # Also check relative to workspace paths
    for ws in workspace_paths:
        ws_norm = str(Path(ws).resolve()).replace("\\", "/")
        if path_str.startswith(ws_norm):
            rel = path_str[len(ws_norm):].lstrip("/")
            for p in ["generations/", "apps/", "src/"]:
                if rel.startswith(p):
                    return True

    return False


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            # No payload; allow by default
            print(json.dumps({"decision": "allow"}))
            return

        payload = json.loads(raw_input)
    except Exception as e:
        sys.stderr.write(f"Guard stdin parsing error: {e}\n")
        print(json.dumps({"decision": "allow"}))
        return

    tool_call = payload.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    tool_args = tool_call.get("args", {})
    workspace_paths = payload.get("workspacePaths", [])
    artifact_dir = payload.get("artifactDirectoryPath", "")

    # Only inspect file modification tools
    if tool_name not in ("edit_file", "write_file"):
        print(json.dumps({"decision": "allow"}))
        return

    raw_path = tool_args.get("Path", "")
    if not raw_path:
        print(json.dumps({"decision": "allow"}))
        return

    target_path = Path(raw_path)

    # Check if target is inside protected generation or application directories
    if not is_protected_path(target_path, workspace_paths):
        print(json.dumps({"decision": "allow"}))
        return

    # Target IS protected. Check if project_proposals.md exists in artifactDirectoryPath
    has_proposals = False
    if artifact_dir:
        proposals_file = Path(artifact_dir) / "project_proposals.md"
        if proposals_file.exists() and proposals_file.stat().st_size > 50:
            has_proposals = True

    if not has_proposals:
        # HARD BLOCK: Zero proposals emitted
        deny_response = {
            "decision": "deny",
            "reason": (
                "FATAL GOVERNANCE VIOLATION [NEG-GOV-GATE-001 / DIRECTIVE 3]: "
                f"Direct modification to generation source code '{target_path.name}' is strictly prohibited. "
                "You have NOT emitted 'project_proposals.md' to your artifact directory. "
                "You must first: (1) analyze the Waterloo Situation of Concern, "
                "(2) physically write 'project_proposals.md' via write_file to your artifact directory, "
                "and (3) elicit approval from the human architect via ask_question before modifying code."
            )
        }
        print(json.dumps(deny_response))
        return

    # Proposals exist: Prompt human architect for explicit confirmation
    ask_response = {
        "decision": "ask",
        "reason": (
            f"Governance Gate: Proposals exist in artifact directory. "
            f"Confirming human architectural approval before modifying generation code file: '{target_path}'"
        )
    }
    print(json.dumps(ask_response))


if __name__ == "__main__":
    main()
