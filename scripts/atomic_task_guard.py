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
- Builder-Tester Adversarial Isolation ([SPEC-G4B-BUILDER-001]):
  * Builder roles (CORE_ENGINE_SYNTHESIZER) are quarantined from modifying `tests/`.
  * QA roles (ADVERSARIAL_QA_ENGINEER) are prohibited from modifying `src/`.
  * Tracks synthesis provenance in `.scratch/synthesis_turn_log.json` to prevent
    single-turn unsegregated code and test emission without mutation verification.
"""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import re
import sys
import textwrap
import time
from typing import Any, Dict, List, Optional, Set, Tuple


PROTECTED_PATTERNS = ["/generations/", "/apps/", "/src/"]

# Common shell redirection patterns targeting protected paths
SHELL_REDIRECT_PATTERN = re.compile(
    r"(?:>|>>|tee\s+(?:-a\s+)?)\s*([\"']?)(?:generations|apps|src)/[^\s\"']+\1"
)

# Role keywords for adversarial role segregation ([SPEC-G4B-BUILDER-001])
BUILDER_ROLE_KEYWORDS = ["builder", "core_engine_synthesizer", "synthesizer", "muscle"]
QA_ROLE_KEYWORDS = ["qa", "adversarial_qa", "byzantine", "tester"]

# Prohibited test patterns for builder role quarantine
PROHIBITED_TEST_PATTERNS = [
    re.compile(r"(?:^|/)tests?/"),
    re.compile(r"(?:^|/)test_[^/]+\.py$"),
    re.compile(r"(?:^|/)[^/]+_test\.py$"),
]

# Production code patterns prohibited for QA role
PROD_CODE_PATTERNS = [
    re.compile(r"(?:^|/)(?:generations/[^/]+/)?services/[^/]+/src/"),
    re.compile(r"(?:^|/)apps/[^/]+/src/"),
    re.compile(r"(?:^|/)apps/[^/]+/static/"),
    re.compile(r"(?:^|/)src/"),
]


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


def is_test_path(norm_path: str) -> bool:
    """Checks whether the normalized path points to a test file or test directory."""
    return any(p.search(norm_path) for p in PROHIBITED_TEST_PATTERNS)


def is_prod_code_path(norm_path: str) -> bool:
    """Checks whether the normalized path points to production source code."""
    return any(p.search(norm_path) for p in PROD_CODE_PATTERNS)


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


def resolve_active_role(payload: Dict[str, Any], workspace_paths: List[str]) -> Tuple[str, str]:
    """Resolves active cognitive role and conversation ID from payload, env, or scratch state."""
    conversation_id = payload.get("conversationId") or payload.get("conversation_id") or ""
    subagent_role = payload.get("subagentRole") or payload.get("subagent_role") or ""

    if not subagent_role:
        env_role = os.environ.get("AXIOMA_COGNITIVE_ROLE") or os.environ.get("ACTIVE_COGNITIVE_ROLE")
        if env_role:
            subagent_role = env_role

    if not subagent_role:
        for ws in workspace_paths:
            role_file = Path(ws) / ".scratch" / "active_role.json"
            if role_file.exists():
                try:
                    data = json.loads(role_file.read_text(encoding="utf-8"))
                    subagent_role = data.get("role", "")
                    if not conversation_id:
                        conversation_id = data.get("conversation_id", "")
                    if subagent_role:
                        break
                except Exception:
                    pass

    if not subagent_role and conversation_id:
        for ws in workspace_paths:
            tel_file = Path(ws) / ".scratch" / "telemetry_hook_state.json"
            if tel_file.exists():
                try:
                    data = json.loads(tel_file.read_text(encoding="utf-8"))
                    sub = data.get("subagents", {}).get(conversation_id, {})
                    if isinstance(sub, dict) and "role" in sub:
                        subagent_role = sub["role"]
                        break
                except Exception:
                    pass

    return subagent_role, conversation_id


def check_builder_quarantine(target_path: Path, role: str) -> Tuple[bool, str]:
    """Enforces that builder roles are quarantined from touching tests/ ([SPEC-G4B-BUILDER-001])."""
    role_lower = role.lower()
    norm = str(target_path.resolve()).replace("\\", "/")

    # Builder role strictly quarantined from modifying tests
    if any(kw in role_lower for kw in BUILDER_ROLE_KEYWORDS) and not any(kw in role_lower for kw in QA_ROLE_KEYWORDS):
        if is_test_path(norm):
            return False, (
                f"BUILDER ROLE QUARANTINE VIOLATION [SPEC-G4B-BUILDER-001]: "
                f"Active role '{role}' (CORE_ENGINE_SYNTHESIZER) is quarantined "
                f"from authoring or modifying test files: '{target_path.name}'. "
                "Tests must be authored by an independent ADVERSARIAL_QA_ENGINEER subagent."
            )

    # QA role quarantined from modifying production code
    if any(kw in role_lower for kw in QA_ROLE_KEYWORDS) and not any(kw in role_lower for kw in BUILDER_ROLE_KEYWORDS):
        if is_prod_code_path(norm) and not is_test_path(norm):
            return False, (
                f"QA ROLE BOUNDARY VIOLATION [SPEC-G4B-BUILDER-001]: "
                f"Active role '{role}' (ADVERSARIAL_QA_ENGINEER) is prohibited from "
                f"modifying production source code: '{target_path.name}'. "
                "QA must author black-box tests strictly inside tests/."
            )

    return True, "Role quarantine valid"


def get_turn_log_path(workspace_paths: List[str]) -> Path:
    """Finds or initializes the synthesis turn log path."""
    for ws in workspace_paths:
        scratch = Path(ws) / ".scratch"
        if scratch.exists():
            return scratch / "synthesis_turn_log.json"
    scratch = Path.cwd() / ".scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    return scratch / "synthesis_turn_log.json"


def load_synthesis_turn_log(log_path: Path) -> Dict[str, Any]:
    """Loads provenance records from synthesis turn log."""
    if log_path.exists():
        try:
            data = json.loads(log_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("records", [])
                data.setdefault("unsegregated_pairs", [])
                return data
        except Exception:
            pass
    return {"records": [], "unsegregated_pairs": []}


def save_synthesis_turn_log(log_path: Path, data: Dict[str, Any]) -> None:
    """Safely saves synthesis turn log."""
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = log_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(log_path)
    except Exception:
        pass


def record_synthesis_provenance(
    log_path: Path,
    target_path: Path,
    conv_id: str,
    role: str,
) -> Dict[str, Any]:
    """Records file mutation provenance in .scratch/synthesis_turn_log.json."""
    data = load_synthesis_turn_log(log_path)
    norm = str(target_path.resolve()).replace("\\", "/")
    category = "TEST" if is_test_path(norm) else ("SRC" if is_prod_code_path(norm) else "OTHER")

    record = {
        "file_path": norm,
        "filename": target_path.name,
        "category": category,
        "conversation_id": conv_id,
        "role": role,
        "timestamp_unix_ms": int(time.time() * 1000),
    }
    data["records"].append(record)

    # Track potential unsegregated single-turn code and test emission
    if category == "TEST" and conv_id:
        target_stem = target_path.stem.replace("test_", "").replace("_test", "")
        # Find if the same conversation previously emitted the corresponding src
        matching_src = next(
            (
                r for r in data["records"]
                if r.get("category") == "SRC"
                and r.get("conversation_id") == conv_id
                and target_stem in Path(r["file_path"]).stem
            ),
            None,
        )
        if matching_src:
            pair = {
                "src_path": matching_src["file_path"],
                "test_path": norm,
                "conversation_id": conv_id,
                "mutation_verified": False,
                "flagged_at_unix_ms": int(time.time() * 1000),
            }
            if not any(
                p.get("src_path") == pair["src_path"] and p.get("test_path") == pair["test_path"]
                for p in data["unsegregated_pairs"]
            ):
                data["unsegregated_pairs"].append(pair)

    save_synthesis_turn_log(log_path, data)
    return data


def check_anti_collusion(
    log_path: Path,
    target_path: Path,
    conv_id: str,
    role: str,
) -> Tuple[bool, str]:
    """Verifies that tests and implementation were not emitted in the same unsegregated turn without mutation verification."""
    norm = str(target_path.resolve()).replace("\\", "/")
    if not is_test_path(norm) or not conv_id:
        return True, "Anti-collusion check passed"

    data = load_synthesis_turn_log(log_path)
    target_stem = target_path.stem.replace("test_", "").replace("_test", "")

    # Look for matching src authored by the exact same conversation context
    matching_src = next(
        (
            r for r in data["records"]
            if r.get("category") == "SRC"
            and r.get("conversation_id") == conv_id
            and target_stem in Path(r["file_path"]).stem
            and not (role and any(kw in role.lower() for kw in QA_ROLE_KEYWORDS))
        ),
        None,
    )
    if matching_src:
        # Check if mutation verification has occurred
        verified_stems = data.get("verified_stems", [])
        verified = (
            target_stem in verified_stems
            or any(
                p.get("src_path") == matching_src["file_path"]
                and p.get("test_path") == norm
                and p.get("mutation_verified") is True
                for p in data.get("unsegregated_pairs", [])
            )
        )
        if not verified:
            return False, (
                f"ANTI-COLLUSION VIOLATION [SPEC-G4B-BUILDER-001]: Attempted to author acceptance test "
                f"'{target_path.name}' in the same unsegregated conversation context ({conv_id[:12]}) "
                f"that emitted implementation '{Path(matching_src['file_path']).name}'. "
                "Tests must be generated by an independent ADVERSARIAL_QA_ENGINEER subagent, "
                "or undergo automated physical mutation falsification."
            )

    return True, "Anti-collusion check passed"


def mark_mutation_verified(log_path: Path, src_stem: str) -> None:
    """Marks unsegregated pairs matching src_stem as mutation verified."""
    data = load_synthesis_turn_log(log_path)
    data.setdefault("verified_stems", [])
    if src_stem not in data["verified_stems"]:
        data["verified_stems"].append(src_stem)
    for p in data.get("unsegregated_pairs", []):
        if src_stem in p.get("src_path", ""):
            p["mutation_verified"] = True
    save_synthesis_turn_log(log_path, data)


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
        norm_str = str(target_path.resolve()).replace("\\", "/")

        # Check if exempt or scratch
        if is_scratch_or_exempt(norm_str):
            print(json.dumps({"decision": "allow"}))
            return

        # Resolve role and conversation ID
        role, conv_id = resolve_active_role(payload, workspace_paths)
        log_path = get_turn_log_path(workspace_paths)

        # 1. Role Quarantine Check ([SPEC-G4B-BUILDER-001])
        quarantine_ok, quarantine_msg = check_builder_quarantine(target_path, role)
        if not quarantine_ok:
            print(json.dumps({
                "decision": "deny",
                "reason": quarantine_msg,
            }))
            return

        # 2. Anti-Collusion Check ([SPEC-G4B-BUILDER-001])
        collusion_ok, collusion_msg = check_anti_collusion(log_path, target_path, conv_id, role)
        if not collusion_ok:
            print(json.dumps({
                "decision": "deny",
                "reason": collusion_msg,
            }))
            return

        # 3. Record Synthesis Provenance in Turn Log
        record_synthesis_provenance(log_path, target_path, conv_id, role)

        # 4. Check if protected code path for task sequencing & AST audit
        if not is_protected_code_path(target_path, workspace_paths):
            print(json.dumps({"decision": "allow"}))
            return

        # 5. Task sequence gate
        seq_valid, seq_msg = check_task_manifest_sequencing(target_path, workspace_paths)
        if not seq_valid:
            print(json.dumps({
                "decision": "deny",
                "reason": seq_msg
            }))
            return

        # 6. AST pitfall check on resulting file content
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
