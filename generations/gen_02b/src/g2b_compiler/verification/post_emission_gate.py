"""Mandatory Post-Emission Execution Gate for System G1b.

Enforces [NEG-G1B-001] (The Anti-Simulated Completion Invariant):
Forbids declaring compilation, verification, or emission complete without
physical non-zero file emission and passing post-emission execution of all
synthesized statechart suites on the concrete runtime substrate.
"""

from dataclasses import dataclass, field
import hashlib
import io
from pathlib import Path
import sys
import time
from typing import Dict, List, Optional, Set
import unittest


class PostEmissionExecutionFailure(Exception):
    """Raised when emitted application fails manifest check or runtime execution."""
    pass


class PhantomEmissionViolation(PostEmissionExecutionFailure):
    """Raised when compilation is attempted without a physical emission target."""
    pass


MANDATORY_MANIFEST: List[str] = [
    "static/index.html",
    "static/machine.js",
    "static/app.js",
    "static/style.css",
    "server.py",
    "run.py",
    "app.json",
    "data/app_state.json",
    "tests/test_runtime.py",
    "tests/test_statechart_execution.py",
]


@dataclass
class PostEmissionReport:
    """Empirical audit report generated after physical emission and test execution."""
    is_verified: bool
    manifest_verified: bool
    files_checked: List[str]
    tests_discovered: int
    tests_passed: int
    failures: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    witness_signature: str = ""
    output_directory: Optional[Path] = None


class PostEmissionGate:
    """Verifies physical presence of application assets and executes target test suites."""

    def __init__(self, manifest: Optional[List[str]] = None):
        self.manifest = manifest or list(MANDATORY_MANIFEST)

    def verify_manifest(self, output_dir: Path) -> List[str]:
        """Asserts that all mandatory files exist on disk with non-zero byte size."""
        checked_files: List[str] = []
        for rel_path in self.manifest:
            target_file = output_dir / rel_path
            if not target_file.exists():
                raise PostEmissionExecutionFailure(
                    f"[NEG-G1B-001 Violation] Missing required emission file: '{rel_path}' in {output_dir}"
                )
            if target_file.stat().st_size == 0:
                raise PostEmissionExecutionFailure(
                    f"[NEG-G1B-001 Violation] Required emission file '{rel_path}' is empty (0 bytes)."
                )
            checked_files.append(rel_path)
        return checked_files

    def execute_test_suite(self, tests_dir: Path) -> unittest.TestResult:
        """Executes Python unittest discovery within the emitted application's tests/ directory."""
        if not tests_dir.exists():
            raise PostEmissionExecutionFailure(
                f"[NEG-G1B-001 Violation] Test suite directory '{tests_dir}' does not exist."
            )

        tests_dir_str = str(tests_dir)
        sys_path_inserted = False
        if tests_dir_str not in sys.path:
            sys.path.insert(0, tests_dir_str)
            sys_path_inserted = True

        # Evict any cached test modules to prevent collision across multiple compilations
        for py_file in tests_dir.glob("*.py"):
            mod_name = py_file.stem
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        try:
            loader = unittest.TestLoader()
            suite = loader.discover(start_dir=tests_dir_str, pattern="test_*.py", top_level_dir=tests_dir_str)

            stream = io.StringIO()
            runner = unittest.TextTestRunner(stream=stream, verbosity=2)
            result = runner.run(suite)
            return result
        finally:
            if sys_path_inserted and tests_dir_str in sys.path:
                sys.path.remove(tests_dir_str)
            for py_file in tests_dir.glob("*.py"):
                mod_name = py_file.stem
                if mod_name in sys.modules:
                    del sys.modules[mod_name]

    def verify_and_execute(self, output_dir: Path) -> PostEmissionReport:
        """Runs full manifest audit and executes runtime test suite, generating an empirical witness."""
        output_dir = Path(output_dir)
        start_time = time.perf_counter()

        # Step 1: Manifest Check
        files_checked = self.verify_manifest(output_dir)

        # Step 2: Runtime Test Execution
        tests_dir = output_dir / "tests"
        result = self.execute_test_suite(tests_dir)
        duration = time.perf_counter() - start_time

        if result.testsRun == 0:
            raise PostEmissionExecutionFailure(
                f"[NEG-G1B-001 Violation] Post-emission verification ran 0 tests in {tests_dir}. "
                "Emitted test suites must contain executable statechart and runtime assertions."
            )

        if not result.wasSuccessful():
            failures_list: List[str] = []
            for test, tb in result.failures:
                failures_list.append(f"FAILURE in {test}:\n{tb}")
            for test, tb in result.errors:
                failures_list.append(f"ERROR in {test}:\n{tb}")
            raise PostEmissionExecutionFailure(
                f"[NEG-G1B-001 Violation] Emitted application failed runtime test execution "
                f"({len(result.failures)} failures, {len(result.errors)} errors):\n"
                + "\n".join(failures_list)
            )

        # Step 3: Compute Cryptographic Witness Signature
        hasher = hashlib.sha256()
        hasher.update(f"POST_EMISSION_WITNESS:{output_dir.name}:{result.testsRun}".encode())
        for rel in sorted(files_checked):
            sz = (output_dir / rel).stat().st_size
            hasher.update(f":{rel}:{sz}".encode())
        witness_sig = f"WITNESS_PE_{hasher.hexdigest()[:16].upper()}"

        return PostEmissionReport(
            is_verified=True,
            manifest_verified=True,
            files_checked=files_checked,
            tests_discovered=result.testsRun,
            tests_passed=result.testsRun,
            failures=[],
            errors=[],
            duration_seconds=duration,
            witness_signature=witness_sig,
            output_directory=output_dir,
        )
