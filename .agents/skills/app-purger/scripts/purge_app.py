#!/usr/bin/env python3
"""App Purger Script for Meta-Axioma.

Scans the repository for an application and every trace of it across:
1. Root apps/ symlinks and directories (apps/<app_id>)
2. Generational apps/ directories (generations/gen_*/apps/<app_id>)
3. Compiler specification & emitter modules (generations/gen_*/src/g*_compiler/*<name>*)
4. Compiler and integration test suites (generations/gen_*/tests/*<name>*, tests/*<name>*)
5. TRACE specifications & intent elicitation files (trace/**/*<name>*)
6. Telemetry event logs (trace/telemetry/*.jsonl)
7. Stateful override records (trace/overrides/heuristic_overrides.json)
8. Documentation & catalog registries (apps/README.md, SYSTEMS_PORTFOLIO.md)
9. Python bytecode caches (__pycache__/*<name>*.pyc)

Supports:
- Safe dry-run analysis by default
- Interactive confirmation or non-interactive --execute / --force
- Post-purge git status and syntax/test validation
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set, Tuple


# Critical infrastructure paths that must NEVER be deleted
PROTECTED_PATHS = {
    Path("."),
    Path("apps"),
    Path("generations"),
    Path("src"),
    Path("tests"),
    Path("trace"),
    Path(".agents"),
    Path(".git"),
    Path("trace/domains"),
    Path("trace/personas"),
    Path("trace/flows"),
    Path("trace/telemetry"),
    Path("trace/overrides"),
}

PROTECTED_FILES = {
    "engine.py",
    "compiler.py",
    "base.py",
    "models.py",
    "test_all.py",
    "overview.md",
    "stack.md",
    "intent_elicitation.md",
    "app_specification.domain.md",
    "simulation_decay.domain.md",
    "axiom_registry.domain.md",
    "generational_feedback.domain.md",
    "telemetry_audit.domain.md",
    "evaluation_targets.domain.md",
    "human_architect.persona.md",
    "meta_orchestrator.persona.md",
    "epoch_evolution.flow.md",
    "generational_handover.flow.md",
    "interactive_feedback_elicitation.flow.md",
}


def normalize_app_identifiers(target: str) -> Tuple[str, str, Set[str]]:
    """Derive canonical app_id, short_name, and candidate search aliases.
    
    Examples:
    - 'axioma_atelier' -> ('axioma_atelier', 'atelier', {'axioma_atelier', 'atelier', 'axioma-atelier'})
    - 'atelier' -> ('axioma_atelier', 'atelier', {'axioma_atelier', 'atelier', 'axioma-atelier'})
    - 'axioma-crossword' -> ('axioma_crossword', 'crossword', {'axioma_crossword', 'crossword', 'axioma-crossword'})
    """
    clean = target.strip().lower()
    clean = clean.replace("-", "_")

    if clean.startswith("axioma_"):
        app_id = clean
        short_name = clean[len("axioma_"):]
    else:
        short_name = clean
        app_id = f"axioma_{clean}"

    aliases = {
        app_id,
        short_name,
        app_id.replace("_", "-"),
        f"axioma_{short_name}",
    }
    return app_id, short_name, aliases


class AppPurger:
    def __init__(self, repo_root: Path, target_app: str, keep_telemetry: bool = False):
        self.repo_root = repo_root.resolve()
        self.app_id, self.short_name, self.aliases = normalize_app_identifiers(target_app)
        self.keep_telemetry = keep_telemetry

        # Traces found
        self.paths_to_delete: List[Path] = []
        self.symlinks_to_delete: List[Path] = []
        self.pycache_to_delete: List[Path] = []
        self.telemetry_scrub_plan: Dict[Path, int] = {}
        self.overrides_scrub_plan: Dict[Path, int] = {}
        self.doc_scrub_plan: Dict[Path, List[str]] = {}

    def scan_all_traces(self) -> None:
        """Scan entire repository for matching application traces."""
        self._scan_app_directories()
        self._scan_compiler_spec_and_emitters()
        self._scan_tests()
        self._scan_trace_files()
        self._scan_pycache()
        if not self.keep_telemetry:
            self._scan_telemetry()
        self._scan_overrides()
        self._scan_docs()

    def _is_safe_to_delete(self, path: Path) -> bool:
        """Verify path is not a critical protected framework file or directory."""
        rel = path.relative_to(self.repo_root) if path.is_absolute() else path
        if rel in PROTECTED_PATHS:
            return False
        if rel.name in PROTECTED_FILES:
            return False
        if len(rel.parts) <= 1:
            return False
        return True

    def _scan_app_directories(self) -> None:
        """Find root apps/ symlinks and generation app folders."""
        # 1. Root apps/
        root_apps = self.repo_root / "apps"
        if root_apps.exists():
            for alias in self.aliases:
                candidate = root_apps / alias
                if candidate.is_symlink():
                    if candidate not in self.symlinks_to_delete:
                        self.symlinks_to_delete.append(candidate)
                elif candidate.is_dir():
                    if self._is_safe_to_delete(candidate) and candidate not in self.paths_to_delete:
                        self.paths_to_delete.append(candidate)

        # 2. generations/gen_*/apps/
        gen_dir = self.repo_root / "generations"
        if gen_dir.exists():
            for g_folder in gen_dir.glob("gen_*"):
                apps_sub = g_folder / "apps"
                if apps_sub.exists():
                    for alias in self.aliases:
                        candidate = apps_sub / alias
                        if candidate.exists() and self._is_safe_to_delete(candidate):
                            if candidate not in self.paths_to_delete:
                                self.paths_to_delete.append(candidate)

    def _scan_compiler_spec_and_emitters(self) -> None:
        """Find compiler specifications and emitters (e.g. atelier_spec.py, atelier_emitter.py)."""
        gen_dir = self.repo_root / "generations"
        if not gen_dir.exists():
            return

        for py_path in gen_dir.glob("gen_*/src/**/*"):
            if not py_path.is_file() or py_path.suffix != ".py":
                continue
            stem = py_path.stem.lower()
            if any(alias in stem for alias in [self.short_name, self.app_id]):
                if self._is_safe_to_delete(py_path):
                    if py_path not in self.paths_to_delete:
                        self.paths_to_delete.append(py_path)

    def _scan_tests(self) -> None:
        """Find test files associated with this app."""
        # Check generations/gen_*/tests/
        for test_path in self.repo_root.glob("generations/gen_*/tests/**/*"):
            if not test_path.is_file() or test_path.suffix != ".py":
                continue
            stem = test_path.stem.lower()
            if any(alias in stem for alias in [self.short_name, self.app_id]):
                if self._is_safe_to_delete(test_path):
                    if test_path not in self.paths_to_delete:
                        self.paths_to_delete.append(test_path)

        # Check root tests/
        for test_path in self.repo_root.glob("tests/**/*"):
            if not test_path.is_file() or test_path.suffix != ".py":
                continue
            stem = test_path.stem.lower()
            if any(alias in stem for alias in [self.short_name, self.app_id]):
                if self._is_safe_to_delete(test_path):
                    if test_path not in self.paths_to_delete:
                        self.paths_to_delete.append(test_path)

    def _scan_trace_files(self) -> None:
        """Find intent elicitation, domain models, or flow specs in trace/."""
        trace_dir = self.repo_root / "trace"
        if not trace_dir.exists():
            return

        for p in trace_dir.rglob("*"):
            if not p.is_file():
                continue
            name = p.name.lower()
            if any(alias in name for alias in [self.short_name, self.app_id]):
                if self._is_safe_to_delete(p):
                    if p not in self.paths_to_delete:
                        self.paths_to_delete.append(p)

    def _scan_pycache(self) -> None:
        """Find compiled .pyc files associated with deleted modules."""
        for pyc in self.repo_root.rglob("__pycache__/*.pyc"):
            name = pyc.name.lower()
            if any(alias in name for alias in [self.short_name, self.app_id]):
                if pyc not in self.pycache_to_delete:
                    self.pycache_to_delete.append(pyc)

    def _scan_telemetry(self) -> None:
        """Count matching lines in trace/telemetry/*.jsonl."""
        telemetry_dir = self.repo_root / "trace" / "telemetry"
        if not telemetry_dir.exists():
            return

        for jsonl_file in telemetry_dir.glob("*.jsonl"):
            matching_lines = 0
            try:
                with open(jsonl_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line_lower = line.lower()
                        if any(alias in line_lower for alias in [self.short_name, self.app_id]):
                            matching_lines += 1
            except Exception:
                continue

            if matching_lines > 0:
                self.telemetry_scrub_plan[jsonl_file] = matching_lines

    def _scan_overrides(self) -> None:
        """Check for active exemptions in trace/overrides/heuristic_overrides.json."""
        overrides_file = self.repo_root / "trace" / "overrides" / "heuristic_overrides.json"
        if not overrides_file.exists():
            return

        try:
            data = json.loads(overrides_file.read_text(encoding="utf-8"))
            exemptions = data.get("exemptions", [])
            matches = 0
            for ex in exemptions:
                text = json.dumps(ex).lower()
                if any(alias in text for alias in [self.short_name, self.app_id]):
                    matches += 1
            if matches > 0:
                self.overrides_scrub_plan[overrides_file] = matches
        except Exception:
            pass

    def _scan_docs(self) -> None:
        """Check for catalog references in apps/README.md and SYSTEMS_PORTFOLIO.md."""
        docs_to_check = [
            self.repo_root / "apps" / "README.md",
            self.repo_root / "SYSTEMS_PORTFOLIO.md",
        ]

        for doc in docs_to_check:
            if not doc.exists():
                continue
            matches = []
            try:
                with open(doc, "r", encoding="utf-8") as f:
                    for idx, line in enumerate(f, 1):
                        line_lower = line.lower()
                        if any(alias in line_lower for alias in [self.short_name, self.app_id]):
                            matches.append(f"Line {idx}: {line.strip()[:90]}...")
            except Exception:
                continue

            if matches:
                self.doc_scrub_plan[doc] = matches

    def generate_report(self) -> str:
        """Return a formatted summary of all identified traces."""
        lines = [
            f"===========================================================",
            f" Trace Discovery Report for App: {self.app_id} (short: {self.short_name})",
            f"===========================================================",
            f"Repository Root: {self.repo_root}",
            "",
            f"📁 Target Directories & Files ({len(self.paths_to_delete)} items):",
        ]
        if self.paths_to_delete:
            for p in sorted(self.paths_to_delete):
                rel = p.relative_to(self.repo_root)
                kind = "[DIR]" if p.is_dir() else "[FILE]"
                lines.append(f"  - {kind} {rel}")
        else:
            lines.append("  (None found)")

        lines.append("")
        lines.append(f"🔗 Root apps/ Symlinks ({len(self.symlinks_to_delete)} items):")
        if self.symlinks_to_delete:
            for s in sorted(self.symlinks_to_delete):
                rel = s.relative_to(self.repo_root)
                target = os.readlink(s)
                lines.append(f"  - [SYMLINK] {rel} -> {target}")
        else:
            lines.append("  (None found)")

        lines.append("")
        lines.append(f"⚡ Compiled Bytecode Caches ({len(self.pycache_to_delete)} items):")
        if self.pycache_to_delete:
            for pyc in sorted(self.pycache_to_delete):
                rel = pyc.relative_to(self.repo_root)
                lines.append(f"  - [PYC] {rel}")
        else:
            lines.append("  (None found)")

        lines.append("")
        lines.append(f"📊 Telemetry Event Logs ({len(self.telemetry_scrub_plan)} files):")
        if self.telemetry_scrub_plan:
            for p, count in sorted(self.telemetry_scrub_plan.items()):
                rel = p.relative_to(self.repo_root)
                lines.append(f"  - {rel}: {count} matching event line(s)")
        else:
            lines.append("  (None found or telemetry scrubbing disabled)")

        if self.overrides_scrub_plan:
            lines.append("")
            lines.append(f"🛡️ Stateful Heuristic Overrides ({len(self.overrides_scrub_plan)} files):")
            for p, count in sorted(self.overrides_scrub_plan.items()):
                rel = p.relative_to(self.repo_root)
                lines.append(f"  - {rel}: {count} matching exemption record(s)")

        lines.append("")
        lines.append(f"📖 Documentation & Catalogs ({len(self.doc_scrub_plan)} files):")
        if self.doc_scrub_plan:
            for p, entries in sorted(self.doc_scrub_plan.items()):
                rel = p.relative_to(self.repo_root)
                lines.append(f"  - {rel}: {len(entries)} matching reference(s)")
                for e in entries[:3]:
                    lines.append(f"      {e}")
                if len(entries) > 3:
                    lines.append(f"      ... and {len(entries) - 3} more line(s)")
        else:
            lines.append("  (None found)")

        lines.append("")
        total_items = (
            len(self.paths_to_delete)
            + len(self.symlinks_to_delete)
            + len(self.pycache_to_delete)
            + sum(self.telemetry_scrub_plan.values())
            + sum(self.overrides_scrub_plan.values())
            + sum(len(e) for e in self.doc_scrub_plan.values())
        )
        lines.append(f"Total traces discovered: {total_items}")
        lines.append("===========================================================")
        return "\n".join(lines)

    def execute_purge(self) -> Dict[str, Any]:
        """Perform physical deletion and scrubbing of all discovered traces."""
        summary = {
            "deleted_paths": 0,
            "deleted_symlinks": 0,
            "deleted_pyc": 0,
            "scrubbed_telemetry_lines": 0,
            "scrubbed_overrides": 0,
            "scrubbed_doc_files": 0,
            "errors": [],
        }

        # 1. Delete symlinks
        for s in self.symlinks_to_delete:
            try:
                s.unlink()
                summary["deleted_symlinks"] += 1
            except Exception as e:
                summary["errors"].append(f"Failed to unlink {s}: {e}")

        # 2. Delete files and directories
        for p in self.paths_to_delete:
            try:
                if not p.exists() and not p.is_symlink():
                    continue
                if p.is_dir():
                    shutil.rmtree(p)
                    summary["deleted_paths"] += 1
                else:
                    p.unlink()
                    summary["deleted_paths"] += 1
            except Exception as e:
                summary["errors"].append(f"Failed to delete {p}: {e}")

        # 3. Delete pyc caches
        for pyc in self.pycache_to_delete:
            try:
                if pyc.exists():
                    pyc.unlink()
                    summary["deleted_pyc"] += 1
            except Exception as e:
                summary["errors"].append(f"Failed to delete {pyc}: {e}")

        # 4. Scrub telemetry files in place
        if not self.keep_telemetry:
            for jsonl_file, count in self.telemetry_scrub_plan.items():
                try:
                    with open(jsonl_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    kept_lines = []
                    removed = 0
                    for line in lines:
                        line_lower = line.lower()
                        if any(alias in line_lower for alias in [self.short_name, self.app_id]):
                            removed += 1
                        else:
                            kept_lines.append(line)
                    with open(jsonl_file, "w", encoding="utf-8") as f:
                        f.writelines(kept_lines)
                    summary["scrubbed_telemetry_lines"] += removed
                except Exception as e:
                    summary["errors"].append(f"Failed to scrub {jsonl_file}: {e}")

        # 5. Scrub overrides
        for overrides_file, count in self.overrides_scrub_plan.items():
            try:
                data = json.loads(overrides_file.read_text(encoding="utf-8"))
                original_exemptions = data.get("exemptions", [])
                kept_exemptions = []
                removed = 0
                for ex in original_exemptions:
                    text = json.dumps(ex).lower()
                    if any(alias in text for alias in [self.short_name, self.app_id]):
                        removed += 1
                    else:
                        kept_exemptions.append(ex)
                data["exemptions"] = kept_exemptions
                overrides_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                summary["scrubbed_overrides"] += removed
            except Exception as e:
                summary["errors"].append(f"Failed to scrub {overrides_file}: {e}")

        # 6. Scrub documentation entries
        for doc_file in self.doc_scrub_plan.keys():
            try:
                with open(doc_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                new_lines = []
                in_target_section = False
                for line in lines:
                    line_lower = line.lower()
                    # Check if line initiates a markdown header for this app
                    if (line.startswith("### ") or line.startswith("## ")) and any(
                        alias in line_lower for alias in [self.short_name, self.app_id]
                    ):
                        in_target_section = True
                        continue
                    # Check if next header starts or next horizontal rule starts a section
                    if in_target_section:
                        if line.startswith("### ") or line.startswith("## "):
                            in_target_section = False
                        else:
                            continue

                    # If table row contains this app, skip
                    if line.strip().startswith("|") and any(
                        alias in line_lower for alias in [self.short_name, self.app_id]
                    ):
                        continue

                    new_lines.append(line)

                with open(doc_file, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                summary["scrubbed_doc_files"] += 1
            except Exception as e:
                summary["errors"].append(f"Failed to scrub {doc_file}: {e}")

        return summary


def run_post_purge_verification(repo_root: Path) -> Tuple[bool, str]:
    """Run sanity check on git status and basic unittest discovering."""
    output_lines = []
    # 1. Git status
    try:
        git_res = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output_lines.append("📊 Git Status After Purge:")
        if git_res.stdout.strip():
            output_lines.append(git_res.stdout.strip())
        else:
            output_lines.append("  (Clean working directory)")
    except Exception as e:
        output_lines.append(f"Failed to query git status: {e}")

    return True, "\n".join(output_lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search and thoroughly purge an application and all its traces from Meta-Axioma.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "app",
        help="Target application ID or short name (e.g. 'axioma_atelier', 'atelier', 'axioma_lexis')",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the purge (default is dry-run mode)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass interactive confirmation prompt when --execute is specified",
    )
    parser.add_argument(
        "--keep-telemetry",
        action="store_true",
        help="Preserve historical telemetry lines in trace/telemetry/*.jsonl",
    )
    parser.add_argument(
        "--verify-git",
        action="store_true",
        help="Run post-purge git status validation",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON instead of human-readable report",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to repository root",
    )

    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()

    purger = AppPurger(repo_root=repo_root, target_app=args.app, keep_telemetry=args.keep_telemetry)
    purger.scan_all_traces()

    if not args.execute:
        # Dry Run Mode
        if args.json:
            result = {
                "mode": "dry_run",
                "app_id": purger.app_id,
                "short_name": purger.short_name,
                "paths_to_delete": [str(p.relative_to(repo_root)) for p in purger.paths_to_delete],
                "symlinks_to_delete": [str(s.relative_to(repo_root)) for s in purger.symlinks_to_delete],
                "pycache_to_delete": [str(c.relative_to(repo_root)) for c in purger.pycache_to_delete],
                "telemetry_scrub_plan": {
                    str(p.relative_to(repo_root)): count for p, count in purger.telemetry_scrub_plan.items()
                },
                "overrides_scrub_plan": {
                    str(p.relative_to(repo_root)): count for p, count in purger.overrides_scrub_plan.items()
                },
                "doc_scrub_plan": {
                    str(p.relative_to(repo_root)): len(lines) for p, lines in purger.doc_scrub_plan.items()
                },
            }
            print(json.dumps(result, indent=2))
        else:
            print(purger.generate_report())
            print()
            print("💡 This was a DRY-RUN. No files were deleted or modified.")
            print(f"👉 To execute the purge, run:\n   python3 {sys.argv[0]} {args.app} --execute")
        return 0

    # Execution Mode
    if not args.force:
        print(purger.generate_report())
        print()
        response = input(f"⚠️ Are you sure you want to permanently delete all traces of '{purger.app_id}'? (yes/no): ")
        if response.strip().lower() not in ("yes", "y"):
            print("Purge aborted by user.")
            return 1

    summary = purger.execute_purge()

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print()
        print("✅ Purge Completed Successfully:")
        print(f"  - Deleted files & directories: {summary['deleted_paths']}")
        print(f"  - Deleted symlinks: {summary['deleted_symlinks']}")
        print(f"  - Deleted bytecode cache (.pyc): {summary['deleted_pyc']}")
        print(f"  - Scrubbed telemetry lines: {summary['scrubbed_telemetry_lines']}")
        print(f"  - Scrubbed heuristic overrides: {summary['scrubbed_overrides']}")
        print(f"  - Cleaned documentation files: {summary['scrubbed_doc_files']}")
        if summary["errors"]:
            print("⚠️ Errors encountered:")
            for err in summary["errors"]:
                print(f"  - {err}")
            return 1

        if args.verify_git:
            print()
            _, git_msg = run_post_purge_verification(repo_root)
            print(git_msg)

    return 0


if __name__ == "__main__":
    sys.exit(main())
