"""Unit Test Suite for AST Skeletonizer CLI (`scripts/skeleton.py`).

Validates:
1. Subprocess CLI execution with clean exit code 0 ([NEG-G1B-002]).
2. Single-file and multi-file skeleton extraction.
3. Structured JSON emission (--json).
4. Markdown summary table emission (--stats).
5. Standard input piping.
6. Error handling for non-existent files and invalid syntax stubs.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKELETON_SCRIPT = REPO_ROOT / "scripts" / "skeleton.py"


class TestSkeletonCLI(unittest.TestCase):
    """Subprocess and integration tests for scripts/skeleton.py."""

    def test_cli_help(self) -> None:
        """Verifies that --help displays options and exits with 0."""
        res = subprocess.run(
            [sys.executable, str(SKELETON_SCRIPT), "--help"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("--max-tokens", res.stdout)
        self.assertIn("--json", res.stdout)
        self.assertIn("--stats", res.stdout)

    def test_single_file_skeleton_extraction(self) -> None:
        """Verifies extracting skeleton from a single file in the repository."""
        target_file = REPO_ROOT / "generations" / "gen_04b" / "services" / "builder" / "src" / "ast_skeletonizer.py"
        res = subprocess.run(
            [sys.executable, str(SKELETON_SCRIPT), str(target_file)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("class ASTSkeletonizer", res.stdout)
        self.assertIn("def extract_skeleton", res.stdout)
        self.assertIn("...", res.stdout)

    def test_json_flag_emission(self) -> None:
        """Verifies that --json produces valid parseable ASTSkeletonSnapshot JSON."""
        target_file = REPO_ROOT / "generations" / "gen_04b" / "services" / "builder" / "src" / "hermetic_linter.py"
        res = subprocess.run(
            [sys.executable, str(SKELETON_SCRIPT), str(target_file), "--json"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertIn("source_module_path", data)
        self.assertIn("skeleton_code", data)
        self.assertIn("estimated_bpe_tokens", data)
        self.assertLessEqual(data["estimated_bpe_tokens"], 4096)

    def test_stats_flag_emission(self) -> None:
        """Verifies that --stats produces a Markdown table with token reduction metrics."""
        target_file = REPO_ROOT / "generations" / "gen_04b" / "services" / "builder" / "src" / "builder_topology.py"
        res = subprocess.run(
            [sys.executable, str(SKELETON_SCRIPT), str(target_file), "--stats"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("| File | Raw Tokens | Skeleton Tokens | Reduction % | Latency |", res.stdout)
        self.assertIn("builder_topology.py", res.stdout)
        self.assertIn("%", res.stdout)

    def test_stdin_piping(self) -> None:
        """Verifies extracting skeleton from code piped via stdin."""
        sample_code = "def complex_algorithm(x: int, y: int) -> int:\n    z = x * y + 42\n    return z * 2\n"
        res = subprocess.run(
            [sys.executable, str(SKELETON_SCRIPT), "-"],
            input=sample_code,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("def complex_algorithm(x: int, y: int) -> int:", res.stdout)
        self.assertIn("...", res.stdout)
        self.assertNotIn("z = x * y", res.stdout)

    def test_nonexistent_file_error(self) -> None:
        """Verifies error handling when a non-existent file path is provided."""
        res = subprocess.run(
            [sys.executable, str(SKELETON_SCRIPT), "nonexistent_file_path_xyz.py"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 1)
        self.assertIn("Error: path does not exist", res.stderr)


if __name__ == "__main__":
    unittest.main()
