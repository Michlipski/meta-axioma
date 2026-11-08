#!/usr/bin/env python3
"""Sync Next-Gen Notes CLI (`scripts/sync_next_gen_notes.py`).

Extracts Generation 5 ($G_5$) succession notes, friction points, deferred scope,
and formal invariant desiderata from `project_proposals.md` and idempotently
synchronizes them into `generations/gen_04b/next_gen/`.

Enforces:
- Schema-validated `G5SuccessionNote` extraction (JSON block and heuristic fallback).
- Idempotent comment-guarded splicing (`<!-- BEGIN G5_SYNC: <id> -->`).
- CommonMark heading preservation.
- Atomic `README.md` indexing for novel RFCs.
- Local bit-for-bit reversible undo snapshots in `.scratch/next_gen_undo_snapshots/`.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import datetime
import difflib
import json
import os
from pathlib import Path
import re
import shutil
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_NEXT_GEN_DIR = REPO_ROOT / "generations" / "gen_04b" / "next_gen"
SNAPSHOT_DIR = REPO_ROOT / ".scratch" / "next_gen_undo_snapshots"
LATEST_SNAPSHOT_FILE = SNAPSHOT_DIR / "latest_snapshot.json"


@dataclass
class G5SuccessionNote:
    """Structured representation of a Generation 5 succession note."""

    note_id: str
    source_proposal_option: str
    scope_type: str  # "service" | "general"
    target_relative_path: str  # e.g., "services/research.md", "general/candidate_services.md"
    target_service: str  # e.g., "research", "builder", "audit", "telemetry", "governance", "general"
    title: str
    friction_summary: list[str] = field(default_factory=list)
    desired_capabilities: list[str] = field(default_factory=list)
    proposed_invariants: list[str] = field(default_factory=list)
    research_spikes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any], default_option: str = "") -> G5SuccessionNote:
        def _to_list(val: Any) -> list[str]:
            if isinstance(val, list):
                return [str(item).strip() for item in val if str(item).strip()]
            if isinstance(val, str) and val.strip():
                lines = [line.strip().lstrip("-* ").strip() for line in val.strip().splitlines()]
                return [line for line in lines if line]
            return []

        note_id = str(data.get("note_id", "")).strip()
        source_opt = str(data.get("source_proposal_option", default_option)).strip()
        scope_type = str(data.get("scope_type", "general")).strip().lower()
        if scope_type not in ("service", "general"):
            scope_type = "general"

        target_path = str(data.get("target_relative_path", "")).strip().lstrip("/")
        target_service = str(data.get("target_service", "general")).strip().lower()
        title = str(data.get("title", "")).strip()

        return cls(
            note_id=note_id,
            source_proposal_option=source_opt,
            scope_type=scope_type,
            target_relative_path=target_path,
            target_service=target_service,
            title=title,
            friction_summary=_to_list(data.get("friction_summary")),
            desired_capabilities=_to_list(data.get("desired_capabilities")),
            proposed_invariants=_to_list(data.get("proposed_invariants")),
            research_spikes=_to_list(data.get("research_spikes")),
        )

    def validate(self) -> list[str]:
        """Validates schema invariants, returning a list of validation errors."""
        errors: list[str] = []
        if not self.note_id:
            errors.append("Missing required field 'note_id'")
        elif not re.match(r"^[a-zA-Z0-9_-]+$", self.note_id):
            errors.append(f"Invalid 'note_id' format '{self.note_id}': must be alphanumeric/hyphens/underscores")

        if not self.source_proposal_option:
            errors.append("Missing required field 'source_proposal_option'")

        if not self.target_relative_path:
            errors.append("Missing required field 'target_relative_path'")
        elif ".." in self.target_relative_path or self.target_relative_path.startswith("/"):
            errors.append(f"Path traversal detected in 'target_relative_path': '{self.target_relative_path}'")

        if not self.title:
            errors.append("Missing required field 'title'")

        if not self.friction_summary and not self.desired_capabilities:
            errors.append("At least one of 'friction_summary' or 'desired_capabilities' must be non-empty")

        return errors


def slugify(text: str) -> str:
    """Converts a string to a clean filename/identifier slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def auto_discover_proposals_file() -> Path | None:
    """Auto-discovers the latest `project_proposals.md` file."""
    candidates: list[Path] = []

    # 1. Check current directory
    cwd_proposal = Path.cwd() / "project_proposals.md"
    if cwd_proposal.exists():
        candidates.append(cwd_proposal)

    # 2. Check Antigravity brain directory
    brain_dir = Path.home() / ".gemini" / "antigravity" / "brain"
    if brain_dir.is_dir():
        try:
            for root, _, files in os.walk(brain_dir):
                if "project_proposals.md" in files:
                    p = Path(root) / "project_proposals.md"
                    candidates.append(p)
        except (PermissionError, OSError):
            pass

    # 3. Check repo workspace
    try:
        for root, dirs, files in os.walk(REPO_ROOT):
            # Exclude noisy dirs
            dirs[:] = [d for d in dirs if d not in (".git", ".scratch", "node_modules", "__pycache__")]
            if "project_proposals.md" in files:
                p = Path(root) / "project_proposals.md"
                candidates.append(p)
    except (PermissionError, OSError):
        pass

    if not candidates:
        return None

    # Pick candidate with newest mtime
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def parse_proposal_options(content: str) -> list[tuple[str, str, str]]:
    """Splits markdown content into proposal options.

    Returns a list of tuples: (option_key, option_title, option_body).
    Example: ("1", "Option 1: Lightweight CLI script", "body content...")
    """
    lines = content.splitlines()
    option_blocks: list[tuple[str, str, list[str]]] = []
    current_key = ""
    current_title = ""
    current_body: list[str] = []

    # Matches headers like:
    # ### Option 1: ...
    # ### Option 2 - ...
    # ## Option 1: ...
    option_header_pattern = re.compile(
        r"^(#{2,4})\s+(Option\s+(\d+|[A-Za-z0-9_-]+)[:\s\-\–]([^\n]+))",
        re.IGNORECASE,
    )

    for line in lines:
        match = option_header_pattern.match(line)
        if match:
            if current_title:
                option_blocks.append((current_key, current_title, current_body))
            opt_num = match.group(3).strip()
            full_title = match.group(2).strip()
            current_key = opt_num
            current_title = full_title
            current_body = [line]
        else:
            if current_title:
                current_body.append(line)

    if current_title:
        option_blocks.append((current_key, current_title, current_body))

    return [(k, title, "\n".join(body)) for k, title, body in option_blocks]


def extract_note_from_option(option_key: str, option_title: str, option_body: str) -> G5SuccessionNote | None:
    """Extracts G5SuccessionNote from option body via JSON block or heuristic fallback."""
    # 1. Deterministic JSON Block Extraction
    json_block_pattern = re.compile(
        r"```(?:json:g5_succession_note|g5_succession_note|json\s*//\s*g5_succession_note)\s*\n([\s\S]*?)\n```",
        re.IGNORECASE,
    )
    match = json_block_pattern.search(option_body)
    if not match:
        # Also check for standard ```json with "note_id" and "g5"
        generic_json = re.compile(r"```json\s*\n(\{[^`]*\"note_id\"[^`]*\})\s*\n```")
        match = generic_json.search(option_body)

    if match:
        try:
            data = json.loads(match.group(1).strip())
            note = G5SuccessionNote.from_dict(data, default_option=option_title)
            return note
        except Exception as e:
            sys.stderr.write(f"Warning: JSON decode error in {option_title}: {e}\n")

    # 2. Heuristic Fallback Extraction from Section 3 Scope Cuts & Adversarial Risk
    deferred_pattern = re.compile(
        r"(?:####\s*[A-Z]?\.?\s*(?:Deliberately Deferred|Deferred Scope|Cut Scope)[^\n]*\n)([\s\S]*?)(?=\n####|\n###|\n---|\Z)",
        re.IGNORECASE,
    )
    adversarial_pattern = re.compile(
        r"(?:####\s*[A-Z]?\.?\s*(?:Adversarial Risk|Red Team Critique)[^\n]*\n)([\s\S]*?)(?=\n####|\n###|\n---|\Z)",
        re.IGNORECASE,
    )

    def_match = deferred_pattern.search(option_body)
    adv_match = adversarial_pattern.search(option_body)

    if def_match or adv_match:
        frictions: list[str] = []
        capabilities: list[str] = []
        invariants: list[str] = []
        spikes: list[str] = []

        if adv_match:
            for raw_line in adv_match.group(1).splitlines():
                line = raw_line.strip().lstrip("-* ").strip()
                if line:
                    frictions.append(line)
                    # Extract any invariant tags like [NEG-...] or [L1-...]
                    for inv in re.findall(r"\[(?:NEG|L1|INV)[^\]]+\]", line):
                        if inv not in invariants:
                            invariants.append(inv)

        if def_match:
            for raw_line in def_match.group(1).splitlines():
                line = raw_line.strip().lstrip("-* ").strip()
                if line:
                    if "rationale" in line.lower() or "spike" in line.lower() or "question" in line.lower():
                        spikes.append(line)
                    else:
                        capabilities.append(line)

        # Detect service keyword
        lower_body = option_body.lower()
        services = ["research", "builder", "audit", "telemetry", "governance"]
        target_service = "general"
        scope_type = "general"
        target_rel_path = f"general/{slugify(option_title)}.md"

        for svc in services:
            if svc in lower_body:
                target_service = svc
                scope_type = "service"
                target_rel_path = f"services/{svc}.md"
                break

        note_id = f"g5-{slugify(option_title)}"
        return G5SuccessionNote(
            note_id=note_id,
            source_proposal_option=option_title,
            scope_type=scope_type,
            target_relative_path=target_rel_path,
            target_service=target_service,
            title=f"Succession Desiderata from {option_title}",
            friction_summary=frictions,
            desired_capabilities=capabilities,
            proposed_invariants=invariants,
            research_spikes=spikes,
        )

    return None


def format_bullet_list(items: list[str], default_text: str = "*None specified.*") -> str:
    """Formats a list of strings into clean CommonMark bullets."""
    if not items:
        return default_text
    formatted = []
    for item in items:
        item_str = str(item).strip()
        if not item_str.startswith("- ") and not item_str.startswith("* "):
            item_str = f"- {item_str}"
        formatted.append(item_str)
    return "\n".join(formatted)


def build_spliced_block(note: G5SuccessionNote) -> str:
    """Builds the comment-guarded markdown block for insertion or update."""
    begin_guard = f"<!-- BEGIN G5_SYNC: {note.note_id} -->"
    end_guard = f"<!-- END G5_SYNC: {note.note_id} -->"

    body = [
        begin_guard,
        f"### {note.title} (Sync from {note.source_proposal_option})",
        "",
        "#### 2. Friction Points & Architectural Limitations",
        format_bullet_list(note.friction_summary),
        "",
        "#### 3. Generation 5 Desired Capabilities & Specification",
        format_bullet_list(note.desired_capabilities),
        "",
        "#### 4. Formal Invariants & Negative Constraints",
        format_bullet_list(note.proposed_invariants),
        "",
        "#### 5. Open Questions & Research Spikes",
        format_bullet_list(note.research_spikes),
        end_guard,
    ]
    return "\n".join(body)


def build_rfc_from_template(template_content: str, note: G5SuccessionNote, file_slug: str) -> str:
    """Instantiates evolution_note_template.md with G5SuccessionNote fields."""
    begin_guard = f"<!-- BEGIN G5_SYNC: {note.note_id} -->"
    end_guard = f"<!-- END G5_SYNC: {note.note_id} -->"

    now_date = datetime.date.today().isoformat()
    scope_display = "Service Enclave: " + note.target_service if note.scope_type == "service" else "General Generational"

    content = template_content
    content = content.replace("[Topic / Service / Feature Name]", note.title)
    content = content.replace("(`evolution_note_template.md`)", f"(`{file_slug}.md`)")
    content = re.sub(
        r"\*\*Target Scope:\*\* [^\n]+",
        f"**Target Scope:** {scope_display}",
        content,
    )
    content = re.sub(
        r"\*\*Author:\*\* [^\n]+",
        f"**Author:** Sovereign Systems Architect (Sync from {note.source_proposal_option})",
        content,
    )
    content = re.sub(
        r"\*\*Created Date:\*\* [^\n]+",
        f"**Created Date:** {now_date}",
        content,
    )
    content = re.sub(
        r"\*\*Status:\*\* [^\n]+",
        "**Status:** PROPOSED",
        content,
    )
    content = re.sub(
        r"\*\*Related URNs:\*\* [^\n]+",
        f"**Related URNs:** `urn:axioma:g5:{note.note_id}`",
        content,
    )

    # Replace section 2
    frictions_block = format_bullet_list(note.friction_summary)
    content = re.sub(
        r"(## 2\. Friction Points & Architectural Limitations\n)[\s\S]*?(?=\n---\n\n## 3)",
        rf"\g<1>{frictions_block}\n",
        content,
    )

    # Replace section 3
    capabilities_block = format_bullet_list(note.desired_capabilities)
    content = re.sub(
        r"(## 3\. Generation 5 Desired Capabilities & Specification\n)[\s\S]*?(?=\n---\n\n## 4)",
        rf"\g<1>{capabilities_block}\n",
        content,
    )

    # Replace section 4
    invariants_block = format_bullet_list(note.proposed_invariants)
    content = re.sub(
        r"(## 4\. Formal Invariants & Negative Constraints\n)[\s\S]*?(?=\n---\n\n## 5)",
        rf"\g<1>{invariants_block}\n",
        content,
    )

    # Replace section 6
    spikes_block = format_bullet_list(note.research_spikes)
    content = re.sub(
        r"(## 6\. Open Questions & Research Spikes\n)[\s\S]*?$",
        rf"\g<1>{spikes_block}\n",
        content,
    )

    # Wrap entire RFC in comment guard
    return f"{begin_guard}\n{content.strip()}\n{end_guard}\n"


def splice_into_target(
    target_path: Path,
    note: G5SuccessionNote,
    template_path: Path,
) -> tuple[str, str, bool]:
    """Slices note into target file, returning (original_content, new_content, is_new_file)."""
    begin_guard = f"<!-- BEGIN G5_SYNC: {note.note_id} -->"
    end_guard = f"<!-- END G5_SYNC: {note.note_id} -->"

    if not target_path.exists():
        # New standalone file; instantiate template
        if template_path.exists():
            tmpl = template_path.read_text(encoding="utf-8")
        else:
            tmpl = (
                f"# {note.title} Evolution Note\n\n"
                "## 2. Friction Points & Architectural Limitations\n\n"
                "## 3. Generation 5 Desired Capabilities & Specification\n\n"
                "## 4. Formal Invariants & Negative Constraints\n\n"
                "## 6. Open Questions & Research Spikes\n"
            )
        new_content = build_rfc_from_template(tmpl, note, target_path.stem)
        return "", new_content, True

    orig_content = target_path.read_text(encoding="utf-8")
    spliced_block = build_spliced_block(note)

    # Check if comment guard already exists in file
    guard_pattern = re.compile(
        rf"{re.escape(begin_guard)}[\s\S]*?{re.escape(end_guard)}",
    )
    if guard_pattern.search(orig_content):
        # In-place idempotent replacement
        new_content = guard_pattern.sub(spliced_block, orig_content)
        return orig_content, new_content, False

    # Insert into file preserving CommonMark structure
    # Try inserting before section 4 (Formal Invariants) or before section 6, or append at end
    insert_marker = re.search(r"\n## 4\.", orig_content)
    if not insert_marker:
        insert_marker = re.search(r"\n## 6\.", orig_content)

    if insert_marker:
        pos = insert_marker.start()
        new_content = (
            orig_content[:pos].rstrip()
            + "\n\n"
            + spliced_block
            + "\n\n"
            + orig_content[pos:].lstrip("\n")
        )
    else:
        new_content = orig_content.rstrip() + "\n\n" + spliced_block + "\n"

    return orig_content, new_content, False


def update_readme_index(readme_path: Path, note: G5SuccessionNote) -> tuple[str, str, bool]:
    """Updates generations/gen_04b/next_gen/README.md to index a new RFC document."""
    if not readme_path.exists():
        return "", "", False

    orig_content = readme_path.read_text(encoding="utf-8")
    rel_link = note.target_relative_path

    # If link already present in README, no update needed
    if f"({rel_link})" in orig_content or f"({note.target_relative_path})" in orig_content:
        return orig_content, orig_content, False

    lines = orig_content.splitlines()
    new_lines: list[str] = []
    inserted = False

    # Target Section 3: Generational Level (Cross-Cutting Architecture)
    gen_section_idx = -1
    for i, line in enumerate(lines):
        if "### Generational Level" in line:
            gen_section_idx = i
            break

    if gen_section_idx != -1:
        # Find highest numbered list item under this section
        last_item_idx = gen_section_idx
        max_num = 0
        for i in range(gen_section_idx + 1, len(lines)):
            line = lines[i]
            if line.startswith("### "):  # Next section
                break
            num_match = re.match(r"^(\d+)\.\s+\*\*\[", line)
            if num_match:
                max_num = max(max_num, int(num_match.group(1)))
                last_item_idx = i

        next_num = max_num + 1 if max_num > 0 else 1
        summary_text = (
            note.friction_summary[0]
            if note.friction_summary
            else (note.desired_capabilities[0] if note.desired_capabilities else note.title)
        )
        new_item = f"{next_num}. **[{note.title}]({rel_link})**: {summary_text}"

        for i, line in enumerate(lines):
            new_lines.append(line)
            if i == last_item_idx:
                new_lines.append(new_item)
                inserted = True

    if not inserted:
        # Fallback: append item under Section 3
        new_content = (
            orig_content.rstrip()
            + f"\n\n- **[{note.title}]({rel_link})**: {note.title}\n"
        )
        return orig_content, new_content, True

    new_content = "\n".join(new_lines) + "\n"
    return orig_content, new_content, True


def safe_rel_path(path: Path) -> str:
    """Safely converts path to relative to REPO_ROOT, falling back to str(path)."""
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(path)


def save_backup_snapshot(
    operations: list[dict[str, Any]],
    note_id: str,
    snapshot_dir: Path = SNAPSHOT_DIR,
) -> Path:
    """Saves file snapshots before modifying disk to support exact --undo."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    snapshot_subfolder = snapshot_dir / f"{timestamp}_{note_id}"
    snapshot_subfolder.mkdir(parents=True, exist_ok=True)

    manifest_ops: list[dict[str, Any]] = []

    for op in operations:
        target_path = Path(op["file"])
        action = op["action"]  # "create" or "modify"
        if action == "modify" and target_path.exists():
            backup_name = f"{target_path.stem}_{hash(str(target_path))}{target_path.suffix}"
            backup_path = snapshot_subfolder / backup_name
            shutil.copy2(target_path, backup_path)
            manifest_ops.append({
                "file": str(target_path.resolve()),
                "action": "modify",
                "backup_file": str(backup_path.resolve()),
            })
        elif action == "create":
            manifest_ops.append({
                "file": str(target_path.resolve()),
                "action": "create",
                "backup_file": None,
            })

    manifest = {
        "timestamp": timestamp,
        "note_id": note_id,
        "operations": manifest_ops,
    }
    manifest_path = snapshot_subfolder / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Update latest pointer
    latest_snapshot_file = snapshot_dir / "latest_snapshot.json"
    latest_snapshot_file.write_text(json.dumps({
        "latest_manifest": str(manifest_path.resolve()),
        "timestamp": timestamp,
        "note_id": note_id,
    }, indent=2), encoding="utf-8")

    return snapshot_subfolder


def execute_undo(snapshot_dir: Path = SNAPSHOT_DIR) -> int:
    """Restores the exact pre-sync state from the latest snapshot."""
    latest_snapshot_file = snapshot_dir / "latest_snapshot.json"
    if not latest_snapshot_file.exists():
        sys.stderr.write(f"No undo snapshot found in {snapshot_dir}\n")
        return 1

    try:
        latest_data = json.loads(latest_snapshot_file.read_text(encoding="utf-8"))
        manifest_path = Path(latest_data["latest_manifest"])
        if not manifest_path.exists():
            sys.stderr.write(f"Snapshot manifest missing: {manifest_path}\n")
            return 1
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        sys.stderr.write(f"Failed to read undo snapshot: {e}\n")
        return 1

    ops = manifest.get("operations", [])
    print(f"[UNDO] Reverting synchronization '{manifest.get('note_id')}' ({manifest.get('timestamp')}):")

    for op in ops:
        target_path = Path(op["file"])
        action = op["action"]
        if action == "create":
            if target_path.exists():
                target_path.unlink()
                print(f"  Removed created file: {safe_rel_path(target_path)}")
        elif action == "modify":
            backup_file = op.get("backup_file")
            if backup_file and Path(backup_file).exists():
                shutil.copy2(backup_file, target_path)
                print(f"  Restored original file: {safe_rel_path(target_path)}")

    # Remove snapshot pointer
    latest_snapshot_file.unlink(missing_ok=True)
    print("[UNDO] Synchronization rollback complete.")
    return 0


def generate_diff(orig: str, new: str, filepath: str) -> str:
    """Generates a clean unified diff string."""
    orig_lines = orig.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(
        orig_lines,
        new_lines,
        fromfile=f"a/{filepath}",
        tofile=f"b/{filepath}",
    )
    return "".join(diff)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract and synchronize G5 succession notes into generations/gen_04b/next_gen/."
    )
    parser.add_argument(
        "--proposals-file",
        type=Path,
        default=None,
        help="Path to project_proposals.md (defaults to auto-discovery).",
    )
    parser.add_argument(
        "--option",
        type=str,
        default=None,
        help="Specific proposal option name or index (e.g., 'Option 1' or '1').",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Extract and preview diff without writing files.",
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Auto-confirm without interactive prompt.",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Revert the last synchronization using local backup snapshots.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that proposal options contain well-formed G5SuccessionNote blocks.",
    )
    parser.add_argument(
        "--next-gen-dir",
        type=Path,
        default=DEFAULT_NEXT_GEN_DIR,
        help="Root path for next_gen documentation (defaults to generations/gen_04b/next_gen).",
    )
    parser.add_argument(
        "--snapshot-dir",
        type=Path,
        default=SNAPSHOT_DIR,
        help="Directory to store undo snapshots (defaults to .scratch/next_gen_undo_snapshots).",
    )

    args = parser.parse_args()

    # Handle --undo
    if args.undo:
        return execute_undo(snapshot_dir=args.snapshot_dir)

    # Discover proposals file
    proposals_path = args.proposals_file
    if proposals_path is None:
        proposals_path = auto_discover_proposals_file()

    if proposals_path is None or not proposals_path.exists():
        sys.stderr.write("Error: Could not locate 'project_proposals.md'. Specify path via --proposals-file.\n")
        return 1

    content = proposals_path.read_text(encoding="utf-8")
    options = parse_proposal_options(content)

    if not options:
        sys.stderr.write(f"Error: No proposal options found in '{proposals_path}'.\n")
        return 1

    # Handle --check
    if args.check:
        print(f"[CHECK] Validating G5SuccessionNote blocks in '{proposals_path}' ({len(options)} options found)...")
        has_errors = False
        for opt_key, opt_title, opt_body in options:
            note = extract_note_from_option(opt_key, opt_title, opt_body)
            if not note:
                print(f"  [WARN] Option {opt_key} ('{opt_title}'): No JSON or heuristic G5 note detected.")
            else:
                errs = note.validate()
                if errs:
                    has_errors = True
                    print(f"  [FAIL] Option {opt_key} ('{opt_title}'): Schema errors:")
                    for err in errs:
                        print(f"         - {err}")
                else:
                    print(f"  [PASS] Option {opt_key} ('{opt_title}'): Valid G5SuccessionNote '{note.note_id}' -> {note.target_relative_path}")
        return 1 if has_errors else 0

    # Select target option
    selected_option = None
    if args.option:
        opt_query = args.option.strip().lower()
        for opt_key, opt_title, opt_body in options:
            if opt_query in (opt_key.lower(), f"option {opt_key.lower()}", opt_title.lower()):
                selected_option = (opt_key, opt_title, opt_body)
                break
            if opt_query in opt_title.lower():
                selected_option = (opt_key, opt_title, opt_body)
                break
        if not selected_option:
            sys.stderr.write(f"Error: Option '{args.option}' not found. Available options: {[t[1] for t in options]}\n")
            return 1
    else:
        # Default to first option or recommended option
        for opt_key, opt_title, opt_body in options:
            if "recommended" in opt_title.lower():
                selected_option = (opt_key, opt_title, opt_body)
                break
        if not selected_option:
            selected_option = options[0]

    opt_key, opt_title, opt_body = selected_option
    print(f"Selected Proposal Option: {opt_title}")

    # Extract G5 note
    note = extract_note_from_option(opt_key, opt_title, opt_body)
    if not note:
        sys.stderr.write(f"Error: Could not extract G5 succession note from {opt_title}.\n")
        return 1

    validation_errors = note.validate()
    if validation_errors:
        sys.stderr.write("Validation errors in extracted G5SuccessionNote:\n")
        for err in validation_errors:
            sys.stderr.write(f"  - {err}\n")
        return 1

    print(f"Extracted Note: ID='{note.note_id}', Target='{note.target_relative_path}'")

    next_gen_dir: Path = args.next_gen_dir
    target_path = next_gen_dir / note.target_relative_path
    template_path = next_gen_dir / "templates" / "evolution_note_template.md"
    readme_path = next_gen_dir / "README.md"

    # Compute target file update
    orig_target, new_target, is_new_file = splice_into_target(target_path, note, template_path)
    target_diff = generate_diff(orig_target, new_target, str(note.target_relative_path))

    # Compute README update if new file
    orig_readme, new_readme, readme_updated = "", "", False
    readme_diff = ""
    if is_new_file:
        orig_readme, new_readme, readme_updated = update_readme_index(readme_path, note)
        if readme_updated:
            readme_diff = generate_diff(orig_readme, new_readme, "README.md")

    # If dry-run, display diff and exit
    if args.dry_run:
        print("\n--- [DRY-RUN] Preview Changes ---")
        if target_diff:
            print(target_diff)
        else:
            print(f"No changes required for {target_path} (already up to date).")
        if readme_diff:
            print("\n--- [DRY-RUN] README.md Changes ---")
            print(readme_diff)
        print("--- [DRY-RUN] End Preview ---")
        return 0

    # Confirmation prompt if interactive
    if not args.yes and sys.stdin.isatty():
        confirm = input(f"Proceed with synchronizing into {note.target_relative_path}? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            print("Aborted by user.")
            return 0

    # Prepare backup snapshot
    snapshot_ops: list[dict[str, Any]] = []
    snapshot_ops.append({
        "file": str(target_path),
        "action": "create" if is_new_file else "modify",
    })
    if readme_updated:
        snapshot_ops.append({
            "file": str(readme_path),
            "action": "modify",
        })

    snapshot_dir = save_backup_snapshot(snapshot_ops, note.note_id, snapshot_dir=args.snapshot_dir)
    print(f"[BACKUP] Snapshot saved to {safe_rel_path(snapshot_dir)}")

    # Write target file
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(new_target, encoding="utf-8")
    print(f"[SYNC] Written to {safe_rel_path(target_path)}")

    # Write README if updated
    if readme_updated:
        readme_path.write_text(new_readme, encoding="utf-8")
        print(f"[INDEX] Updated {safe_rel_path(readme_path)}")

    print(f"[SUCCESS] Generation 5 succession note '{note.note_id}' synchronized cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
