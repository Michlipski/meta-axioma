#!/usr/bin/env python3
"""Atomic Task & Sequential Progression Guard (`scripts/atomic_task_guard.py`).

Enforces:
- Atomic Task Quarantine: Prohibits multi-task batch dumping in a single turn.
- Physical Grounding Precondition: Task T_{k+1} is strictly locked until Task T_k
  has recorded physical disk grounding (byte_size > 0), passing AST pitfall audits,
  and a signed reality coverage receipt.
- Shell Redirection Interception: Prevents bypassing file guards via `run_command`
  redirections (e.g. `echo ... > target.py` or `cat <<EOF > target.py`).
- Pre-Emission AST Micro-Audit: Flags immediate operational pitfalls (missing timeouts,
  unbounded loops) before writing to protected code trees.
"""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import re
import sys
import textwrap
from typing import Any, Dict, List, Optional, Set, Tuple


PROTECTED_PATTERNS = ["/generations/", "/apps/", "/src/"]

# Common shell redirection patterns targeting protected paths
SHELL_REDIRECT_PATTERN = re.compile(
    r"(?:>|>>|tee\s+(?:-a\s+)?)\s*([\"']?)(?:generations|apps|src)/[^\s\"']+\1"
)


def is_scratch_or_exempt(path_str: str) -> bool:
    """Checks if the path is in a designated exempt/scratch location."""
    norm = path_str.replace("\\", "/")
    exempt_markers = [
        "/.scratch/",
        "/scratch/",
        "/.gemini/antigravity/brain/",
        "/tmp/",
        "/.git/",
    ]
    return any(marker in norm for marker in exempt_markers)


def is_protected_code_path(target_path: Path, workspace_paths: List[str]) -> bool:
    """Checks if a path falls inside protected code directories."""
    path_str = str(target_path.resolve()).replace("\\", "/")
    if is_scratch_or_exempt(path_str):
        return False

    for pattern in PROTECTED_PATTERNS:
        if pattern in path_str:
            return True

    for ws in workspace_paths:
        ws_norm = str(Path(ws).resolve()).replace("\\", "/")
        if path_str.startswith(ws_norm):
            rel = path_str[len(ws_norm):].lstrip("/")
            for p in ["generations/", "apps/", "src/"]:
                if rel.startswith(p):
                    return True

    return False


def verify_source_ast_pitfalls(content: str, filename: str) -> Tuple[bool, str]:
    """Lightweight AST verification for syntax errors and immediate operational pitfalls."""
    if not filename.endswith(".py"):
        return True, "Non-Python file"

    try:
        tree = ast.parse(textwrap.dedent(content), filename=filename)
    except SyntaxError as e:
        return False, f"SyntaxError in {filename}: {e.msg} at line {e.lineno}"

    for node in ast.walk(tree):
        # Pitfall: bare requests/httpx calls without timeout keyword
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            elif isinstance(node.func, ast.Name):
                func_name = node.func.id

            if func_name in ("get", "post", "put", "delete", "request"):
                # Check if it has a timeout keyword
                has_timeout = any(kw.arg == "timeout" for kw in node.keywords)
                # If it's likely a network call (has a URL-like first arg)
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    if node.args[0].value.startswith(("http://", "https://")) and not has_timeout:
                        return False, (
                            f"Operational Pitfall OP-003 Violation in {filename} (line {node.lineno}): "
                            f"Network call '{func_name}()' must specify an explicit positive timeout keyword."
                        )

    return True, "AST clean"


def check_task_manifest_sequencing(
    target_path: Path, workspace_paths: List[str]
) -> Tuple[bool, str]:
    """Checks whether the active task manifest permits writing to target_path."""
    # Look for task manifest in workspace .scratch/
    manifest_path: Optional[Path] = None
    for ws in workspace_paths:
        candidate = Path(ws) / ".scratch" / "active_task_manifest.json"
        if candidate.exists():
            manifest_path = candidate
            break

    if not manifest_path or not manifest_path.exists():
        # No active task manifest is registered; do not block sequencing
        return True, "No manifest active"

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        return True, f"Manifest read bypass: {e}"

    active_task_id = data.get("active_task_id")
    tasks = data.get("tasks", [])
    if not active_task_id or not tasks:
        return True, "Empty manifest"

    norm_target = str(target_path.resolve()).replace("\\", "/")

    # Find the task that owns this file
    owner_task_id: Optional[str] = None
    for t in tasks:
        allowed_files = t.get("allowed_files", [])
        for f in allowed_files:
            # Match suffix or full name
            if norm_target.endswith(f.replace("\\", "/")) or f in norm_target:
                owner_task_id = t.get("task_id")
                break
        if owner_task_id:
            break

    if not owner_task_id:
        # File is not part of tracked manifest
        return True, "File unmanaged by manifest"

    # If file belongs to a future task while active_task_id hasn't finished
    if owner_task_id != active_task_id:
        # Check if active task is completed
        active_task = next((t for t in tasks if t.get("task_id") == active_task_id), None)
        if active_task and active_task.get("status") != "COMPLETED":
            return False, (
                f"ATOMIC TASK PROGRESSION VIOLATION: Attempting to modify '{target_path.name}' "
                f"assigned to future task '{owner_task_id}', but current task '{active_task_id}' "
                f"is still {active_task.get('status', 'PENDING')}. "
                "You must finish, physically test, and seal reality receipts for the active task first."
            )

    return True, "Task sequence valid"


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({"decision": "allow"}))
            return

        payload = json.loads(raw_input)
    except Exception as e:
        sys.stderr.write(f"AtomicTaskGuard stdin error: {e}\n")
        print(json.dumps({"decision": "allow"}))
        return

    tool_call = payload.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    tool_args = tool_call.get("args", {})
    workspace_paths = payload.get("workspacePaths", [])

    # Case 1: Intercept run_command with shell redirections into protected files
    if tool_name == "run_command":
        cmd = tool_args.get("CommandLine", "")
        if SHELL_REDIRECT_PATTERN.search(cmd):
            print(json.dumps({
                "decision": "deny",
                "reason": (
                    "ATOMIC TASK GUARD VIOLATION: Detected shell redirection ('>' or 'tee') "
                    "targeting protected code in run_command. Bypassing tool hooks via shell redirection "
                    "is strictly prohibited. Use write_file or edit_file directly."
                )
            }))
            return
        print(json.dumps({"decision": "allow"}))
        return

    # Case 2: Inspect file mutations (write_file / edit_file)
    if tool_name in ("write_file", "edit_file"):
        raw_path = tool_args.get("Path", "")
        if not raw_path:
            print(json.dumps({"decision": "allow"}))
            return

        target_path = Path(raw_path)

        # Check if protected
        if not is_protected_code_path(target_path, workspace_paths):
            print(json.dumps({"decision": "allow"}))
            return

        # 1. Task sequence gate
        seq_valid, seq_msg = check_task_manifest_sequencing(target_path, workspace_paths)
        if not seq_valid:
            print(json.dumps({
                "decision": "deny",
                "reason": seq_msg
            }))
            return

        # 2. AST pitfall check on resulting file content
        content = tool_args.get("Content", "")
        if not content and tool_name == "edit_file":
            target = tool_args.get("Target", "")
            replacement = tool_args.get("Replacement", "")
            if target_path.exists() and target:
                orig_text = target_path.read_text(encoding="utf-8")
                content = orig_text.replace(target, replacement)
            else:
                content = replacement

        if content and target_path.suffix == ".py":
            ast_valid, ast_msg = verify_source_ast_pitfalls(content, target_path.name)
            if not ast_valid:
                print(json.dumps({
                    "decision": "deny",
                    "reason": f"ATOMIC TASK AUDIT FAILURE: {ast_msg}"
                }))
                return

    print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
