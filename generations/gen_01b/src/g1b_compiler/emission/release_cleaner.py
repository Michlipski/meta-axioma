"""Release Cleaner and Scaffolding Stripper for System G1b.

Grounded in [NEG-G2-006] (Clean-Slate Production State Invariant).
Strips development debug hooks, inspection banners, and unverified scaffolding
from the compiled production release artifact.
"""

from pathlib import Path
import re
from typing import Dict, List


class ReleaseCleaner:
    """Sanitizes emitted application directories prior to release packaging."""

    # Patterns to strip from production client files
    SCAFFOLDING_STRIP_PATTERNS = [
        (r"/\* __DEBUG_SCAFFOLDING_START__ \*/[\s\S]*?/\* __DEBUG_SCAFFOLDING_END__ \*/", ""),
        (r"console\.debug\(.*?\);?", ""),
        (r"window\.__DEV_TOOLS_HOOK__\s*=.*?;", ""),
    ]

    def sanitize_file(self, file_path: Path):
        """Reads file, strips scaffolding patterns, and overwrites if modified."""
        if not file_path.exists() or file_path.is_dir():
            return

        content = file_path.read_text(encoding="utf-8")
        modified = content
        for pattern, replacement in self.SCAFFOLDING_STRIP_PATTERNS:
            modified = re.sub(pattern, replacement, modified)

        if modified != content:
            file_path.write_text(modified, encoding="utf-8")

    def clean_release_directory(self, target_dir: Path):
        """Recursively sanitizes all text files in the target release directory."""
        if not target_dir.exists():
            return

        for p in target_dir.rglob("*"):
            if p.is_file() and p.suffix in [".html", ".js", ".ts", ".css", ".json", ".py"]:
                self.sanitize_file(p)
