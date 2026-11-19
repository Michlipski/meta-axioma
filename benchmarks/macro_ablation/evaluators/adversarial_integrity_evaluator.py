"""Pass 6: Adversarial & Behavioral Integrity Evaluator (Red Team + Physical Mutation Accountability).

Enforces:
- [INV-G4B-REDTEAM-001] Unresolved Red Team critical vulnerabilities MUST prevent a 100.00 ceiling.
- [INV-G4B-MUTATION-001] Emitted test suites must kill real behavioral mutations in core source code
  (executed non-destructively against an isolated `.scratch/` clone with mandatory baseline exit-0 check).
"""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple
import uuid

from ..domain_models import BenchmarkArchetype, EvaluationPassResult

try:
    from generations.gen_04b.services.audit.src.mutation_fuzzer import (
        PhysicalMutationFalsifier,
        TautologicalTestViolation,
    )
except Exception:  # pragma: no cover - fallback when gen_04b audit is unavailable
    PhysicalMutationFalsifier = None  # type: ignore[assignment]
    TautologicalTestViolation = Exception  # type: ignore[assignment,misc]


_WORKSPACE_ROOT = Path(__file__).resolve().parents[3]


def _make_mutation_scratch_dir(prefix: str = "mut_eval_") -> Path:
    scratch_root = _WORKSPACE_ROOT / ".scratch"
    scratch_root.mkdir(parents=True, exist_ok=True)
    clone_dir = scratch_root / f"{prefix}{uuid.uuid4().hex[:10]}"
    return clone_dir


class AdversarialIntegrityEvaluator:
    """Accountability evaluator checking Red Team certification and non-tautological mutation kill rate."""

    def __init__(
        self,
        weight: float = 0.0,
        app_data_dir: Optional[Path] = None,
        max_mutants: int = 2,
        mutation_timeout_sec: float = 12.0,
        critical_penalty_each: float = 6.0,
        max_critical_penalty: float = 36.0,
    ) -> None:
        self.weight = weight
        if app_data_dir:
            self.app_data_dir = Path(app_data_dir).resolve()
        else:
            self.app_data_dir = Path(
                os.environ.get("ANTIGRAVITY_APP_DATA_DIR", Path.home() / ".gemini" / "antigravity")
            ).resolve()
        self.max_mutants = max(1, int(max_mutants))
        self.mutation_timeout_sec = float(mutation_timeout_sec)
        self.critical_penalty_each = float(critical_penalty_each)
        self.max_critical_penalty = float(max_critical_penalty)

    def _load_manifest(
        self,
        app_dir: Path,
        provenance_manifest: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        if provenance_manifest is not None:
            return provenance_manifest
        manifest_path = app_dir / "synthesis_manifest.json"
        if manifest_path.exists():
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except Exception:
                return None
        return None

    def _extract_red_team_status(
        self,
        app_dir: Path,
        manifest: Optional[Dict[str, Any]],
    ) -> Tuple[Optional[bool], int, str, List[str]]:
        """Resolves (red_team_pass, critical_vulnerabilities_found, source, findings)."""
        # 1. Physical red_team_verdict.json on disk
        verdict_file = app_dir / "red_team_verdict.json"
        if verdict_file.exists():
            try:
                data = json.loads(verdict_file.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    rt_pass = data.get("red_team_pass")
                    if rt_pass is None:
                        rt_pass = data.get("red_team_passed")
                    crit = data.get("critical_vulnerabilities_found")
                    findings = list(data.get("findings") or [])
                    if crit is not None:
                        crit_int = max(0, int(crit))
                        passed_bool = bool(rt_pass) if rt_pass is not None else (crit_int == 0)
                        if crit_int > 0:
                            passed_bool = False
                        return passed_bool, crit_int, "PHYSICAL_VERDICT_FILE", [str(f) for f in findings[:10]]
                    if rt_pass is not None:
                        passed_bool = bool(rt_pass)
                        return passed_bool, (0 if passed_bool else max(1, len(findings))), "PHYSICAL_VERDICT_FILE", [str(f) for f in findings[:10]]
            except Exception as exc:
                return False, 1, "MALFORMED_VERDICT_FILE", [f"Malformed red_team_verdict.json: {exc}"]

        # 2. Explicit fields in synthesis_manifest.json / g4b_compilation
        if isinstance(manifest, dict):
            containers = [manifest.get("g4b_compilation"), manifest]
            for container in containers:
                if not isinstance(container, dict):
                    continue
                if "red_team_verdict" in container and isinstance(container["red_team_verdict"], dict):
                    v = container["red_team_verdict"]
                    crit_int = max(0, int(v.get("critical_vulnerabilities_found", 0)))
                    rt_pass = bool(v.get("red_team_pass", crit_int == 0)) and crit_int == 0
                    return rt_pass, crit_int, "MANIFEST_RED_TEAM_VERDICT", [str(f) for f in (v.get("findings") or [])[:10]]
                if "red_team_passed" in container or "critical_vulnerabilities_found" in container:
                    crit_int = max(0, int(container.get("critical_vulnerabilities_found", 0)))
                    rt_pass = bool(container.get("red_team_passed", crit_int == 0)) and crit_int == 0
                    if not rt_pass and crit_int == 0:
                        crit_int = 1
                    return rt_pass, crit_int, "MANIFEST_COMPILATION_FIELDS", []

            # 3. Legacy manifest with Red Team subagent witness -> parse physical transcript.jsonl if readable
            subagents = manifest.get("subagents") or manifest.get("subagent_witnesses") or []
            saw_red_team_subagent = False
            for entry in reversed(subagents):
                if not isinstance(entry, dict):
                    continue
                role_str = str(entry.get("cognitive_role") or entry.get("role") or "").upper()
                if "RED_TEAM" not in role_str and "RED TEAM" not in role_str and "REDTEAM" not in role_str:
                    continue
                saw_red_team_subagent = True
                cid = str(entry.get("conversation_id", "")).strip()
                if not cid:
                    continue
                t_path = self.app_data_dir / "brain" / cid / ".system_generated" / "logs" / "transcript.jsonl"
                if not t_path.exists():
                    continue
                parsed = self._parse_red_team_transcript(t_path)
                if parsed is not None:
                    return parsed

            if saw_red_team_subagent:
                # Red Team subagent ran, yet neither red_team_verdict.json nor manifest recorded a
                # structured pass verdict (advisory-only witness -> fail-closed against 100.00 ceiling).
                return (
                    None,
                    0,
                    "UNSTRUCTURED_ADVISORY_RED_TEAM",
                    ["Red Team subagent executed without a structured red_team_pass verdict in manifest or red_team_verdict.json"],
                )

        return None, 0, "NOT_APPLICABLE", []

    def _parse_red_team_transcript(
        self,
        transcript_path: Path,
    ) -> Optional[Tuple[bool, int, str, List[str]]]:
        """Extracts Red Team Certification Witness markers from a physical transcript.jsonl."""
        try:
            lines = transcript_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            return None

        pass_re = re.compile(r"red_team_pass[`'\"\s:=]+(true|false)", re.IGNORECASE)
        crit_re = re.compile(r"critical_vulnerabilities_found[`'\"\s:=]+(\d+)", re.IGNORECASE)

        for raw_line in reversed(lines):
            if not raw_line.strip():
                continue
            try:
                step = json.loads(raw_line)
            except Exception:
                continue
            if not isinstance(step, dict):
                continue

            # Inspect assistant message content and send_message tool call payloads
            text_blobs: List[str] = []
            content = step.get("content")
            if isinstance(content, str) and content.strip():
                text_blobs.append(content)
            for tc in step.get("tool_calls") or []:
                if isinstance(tc, dict) and tc.get("name") == "send_message":
                    args = tc.get("args") or {}
                    msg = args.get("Message") or args.get("message")
                    if isinstance(msg, str) and msg.strip():
                        text_blobs.append(msg)

            for blob in text_blobs:
                m_pass = pass_re.search(blob)
                m_crit = crit_re.search(blob)
                if m_pass or m_crit:
                    crit_int = int(m_crit.group(1)) if m_crit else (0 if (m_pass and m_pass.group(1).lower() == "true") else 1)
                    rt_pass = (m_pass.group(1).lower() == "true") if m_pass else (crit_int == 0)
                    if crit_int > 0:
                        rt_pass = False
                    elif not rt_pass and crit_int == 0:
                        crit_int = 1
                    findings = [
                        ln.strip().lstrip("-* ").strip()[:180]
                        for ln in blob.replace("\\n", "\n").splitlines()
                        if re.search(r"\[CRIT-\d+\]", ln)
                    ]
                    return rt_pass, crit_int, "RED_TEAM_TRANSCRIPT_WITNESS", findings[:10]
        return None

    def _discover_mutation_candidates(self, clone_dir: Path) -> List[Tuple[Path, Tuple[str, str], str]]:
        """Selects real behavioral AST mutation pairs inside core non-test production modules."""
        candidates: List[Tuple[Path, Tuple[str, str], str]] = []
        src_dir = clone_dir / "src"
        py_targets: List[Path] = []
        if src_dir.exists():
            # Prefer engine.py / server.py / wal.py / router.py before models
            all_src = sorted(
                p for p in src_dir.glob("*.py")
                if p.name != "__init__.py" and not p.name.startswith("test_")
            )
            priority = [p for p in all_src if any(k in p.stem.lower() for k in ("engine", "server", "wal", "store", "core", "router"))]
            rest = [p for p in all_src if p not in priority]
            py_targets = priority + rest
        else:
            py_targets = sorted(
                p for p in clone_dir.glob("*.py")
                if p.name != "__init__.py" and not p.name.startswith("test_") and p.name != "run.py"
            )
            if not py_targets and (clone_dir / "run.py").exists():
                py_targets = [clone_dir / "run.py"]

        for py_path in py_targets:
            if len(candidates) >= self.max_mutants:
                break
            try:
                text = py_path.read_text(encoding="utf-8")
                tree = ast.parse(text, filename=str(py_path))
                lines = text.splitlines(keepends=True)
            except Exception:
                continue

            # Walk functions/methods (skip __init__, __repr__, log_message) looking for behavioral if/return lines
            for node in ast.walk(tree):
                if len(candidates) >= self.max_mutants:
                    break
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name in ("__init__", "__repr__", "__str__", "log_message", "to_dict"):
                    continue
                for stmt in node.body:
                    if len(candidates) >= self.max_mutants:
                        break
                    lineno = getattr(stmt, "lineno", 0)
                    if lineno < 1 or lineno > len(lines):
                        continue
                    orig_line = lines[lineno - 1]
                    stripped = orig_line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue

                    mut_pair: Optional[Tuple[str, str]] = None
                    desc = ""
                    if isinstance(stmt, ast.If):
                        if " == " in orig_line:
                            mut_pair = (orig_line, orig_line.replace(" == ", " != ", 1))
                            desc = f"{py_path.name}:{lineno} ({node.name}) invert =="
                        elif " != " in orig_line:
                            mut_pair = (orig_line, orig_line.replace(" != ", " == ", 1))
                            desc = f"{py_path.name}:{lineno} ({node.name}) invert !="
                        elif " < " in orig_line:
                            mut_pair = (orig_line, orig_line.replace(" < ", " >= ", 1))
                            desc = f"{py_path.name}:{lineno} ({node.name}) invert <"
                        elif " > " in orig_line:
                            mut_pair = (orig_line, orig_line.replace(" > ", " <= ", 1))
                            desc = f"{py_path.name}:{lineno} ({node.name}) invert >"
                    elif isinstance(stmt, ast.Return) and stmt.value is not None:
                        if not (isinstance(stmt.value, ast.Constant) and stmt.value.value is None):
                            indent = len(orig_line) - len(orig_line.lstrip())
                            mut_pair = (orig_line, " " * indent + "return None  # MUTANT_RETURN_NONE\n")
                            desc = f"{py_path.name}:{lineno} ({node.name}) return None"

                    if mut_pair is not None and text.count(mut_pair[0]) == 1:
                        candidates.append((py_path, mut_pair, desc))
                        break  # At most 1 mutant per function to cover distinct code paths

        return candidates

    def _run_non_destructive_mutation_check(self, app_dir: Path) -> Dict[str, Any]:
        """Clones app_dir into .scratch/, verifies baseline tests exit 0, and tests real mutations."""
        tests_dir = app_dir / "tests"
        has_tests_dir = tests_dir.exists() and any(tests_dir.glob("test_*.py"))
        top_level_tests = [p for p in app_dir.glob("test_*.py") if p.is_file()]
        tests_found = has_tests_dir or bool(top_level_tests)

        result: Dict[str, Any] = {
            "tests_found": tests_found,
            "baseline_passed": False,
            "mutants_tested": 0,
            "mutants_killed": 0,
            "kill_rate": 0.0,
            "tautological_tests_detected": False,
            "mutant_log": [],
        }
        if not tests_found:
            return result

        clone_dir = _make_mutation_scratch_dir(prefix="mut_eval_")
        try:
            shutil.copytree(
                app_dir,
                clone_dir,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".telemetry_vault.sqlite*"),
            )
            test_start_dir = str(clone_dir / "tests") if has_tests_dir else str(clone_dir)
            test_cmd = [sys.executable, "-u", "-m", "unittest", "discover", "-s", test_start_dir]
            env = {
                **os.environ,
                "PYTHONUNBUFFERED": "1",
                "PYTHONPATH": str(clone_dir),
            }

            # Mandatory baseline exit-0 pre-flight check [VULN-09]
            try:
                base_proc = subprocess.run(
                    test_cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.mutation_timeout_sec,
                    cwd=str(clone_dir),
                    env=env,
                )
                baseline_passed = (base_proc.returncode == 0)
            except Exception as exc:
                baseline_passed = False
                result["mutant_log"].append(f"Baseline test execution error: {type(exc).__name__}")

            result["baseline_passed"] = baseline_passed
            if not baseline_passed:
                result["mutant_log"].append("Baseline test suite failed on unmutated code; skipping mutant injection")
                return result

            candidates = self._discover_mutation_candidates(clone_dir)
            if not candidates:
                result["mutant_log"].append("No eligible behavioral mutation sites discovered in core modules")
                return result

            for target_file, (orig_pat, mut_pat), desc in candidates:
                result["mutants_tested"] += 1
                orig_bytes = target_file.read_bytes()
                try:
                    orig_text = orig_bytes.decode("utf-8")
                    mutated_text = orig_text.replace(orig_pat, mut_pat, 1)
                    target_file.write_text(mutated_text, encoding="utf-8")
                    try:
                        m_proc = subprocess.run(
                            test_cmd,
                            capture_output=True,
                            text=True,
                            timeout=self.mutation_timeout_sec,
                            cwd=str(clone_dir),
                            env=env,
                        )
                        killed = (m_proc.returncode != 0)
                    except subprocess.TimeoutExpired:
                        killed = True
                    if killed:
                        result["mutants_killed"] += 1
                        result["mutant_log"].append(f"KILLED: {desc}")
                    else:
                        result["tautological_tests_detected"] = True
                        result["mutant_log"].append(f"SURVIVED (tautological): {desc}")
                finally:
                    target_file.write_bytes(orig_bytes)

            if result["mutants_tested"] > 0:
                result["kill_rate"] = round(result["mutants_killed"] / result["mutants_tested"], 3)
            return result
        finally:
            if clone_dir.exists():
                shutil.rmtree(clone_dir, ignore_errors=True)

    def evaluate(
        self,
        app_dir: Path,
        archetype: BenchmarkArchetype,
        provenance_manifest: Optional[Dict[str, Any]] = None,
    ) -> EvaluationPassResult:
        """Evaluates Red Team certification accountability and non-tautological test kill rate."""
        app_dir = Path(app_dir).resolve()
        manifest = self._load_manifest(app_dir, provenance_manifest)

        rt_pass, crit_count, rt_source, rt_findings = self._extract_red_team_status(app_dir, manifest)
        mut_info = self._run_non_destructive_mutation_check(app_dir)

        penalty_points = 0.0
        score_cap = 100.0
        reasons: List[str] = []

        # 1. Red Team critical accountability
        if rt_pass is False or crit_count > 0:
            effective_crits = max(1, crit_count)
            rt_penalty = min(self.max_critical_penalty, effective_crits * self.critical_penalty_each)
            penalty_points += rt_penalty
            score_cap = min(score_cap, 85.0)
            reasons.append(
                f"Unresolved Red Team criticals ({effective_crits}, source={rt_source}): -{rt_penalty:.1f} pts, cap <= 85.0"
            )
        elif rt_source == "UNSTRUCTURED_ADVISORY_RED_TEAM":
            penalty_points += 10.0
            score_cap = min(score_cap, 90.0)
            reasons.append(
                "Advisory-only Red Team subagent without structured pass verdict in manifest/red_team_verdict.json: -10.0 pts, cap <= 90.0"
            )

        # 2. Physical Mutation Falsification accountability
        if not mut_info["tests_found"]:
            penalty_points += 5.0
            reasons.append("No emitted unittest suite found for physical mutation falsification: -5.0 pts")
        elif not mut_info["baseline_passed"]:
            penalty_points += 15.0
            score_cap = min(score_cap, 85.0)
            reasons.append("Emitted test suite failed baseline execution on unmutated code: -15.0 pts, cap <= 85.0")
        elif mut_info["mutants_tested"] > 0 and mut_info["tautological_tests_detected"]:
            penalty_points += 15.0
            score_cap = min(score_cap, 85.0)
            reasons.append(
                f"Tautological test survivor detected (kill_rate={mut_info['kill_rate']:.2f}): -15.0 pts, cap <= 85.0"
            )

        raw_score = round(max(0.0, 100.0 - penalty_points), 2)
        passed = (
            rt_pass is not False
            and crit_count == 0
            and rt_source != "UNSTRUCTURED_ADVISORY_RED_TEAM"
            and not mut_info["tautological_tests_detected"]
            and (not mut_info["tests_found"] or mut_info["baseline_passed"])
        )

        return EvaluationPassResult(
            pass_name="adversarial_integrity",
            weight=self.weight,
            raw_score=raw_score,
            weighted_score=round(-penalty_points, 2),
            details={
                "red_team_pass": rt_pass,
                "critical_vulnerabilities_found": crit_count,
                "red_team_source": rt_source,
                "red_team_findings": rt_findings,
                "tests_found": mut_info["tests_found"],
                "baseline_passed": mut_info["baseline_passed"],
                "mutants_tested": mut_info["mutants_tested"],
                "mutants_killed": mut_info["mutants_killed"],
                "kill_rate": mut_info["kill_rate"],
                "tautological_tests_detected": mut_info["tautological_tests_detected"],
                "mutant_log": mut_info["mutant_log"][:10],
                "penalty_points": round(penalty_points, 2),
                "score_cap": score_cap,
                "reasons": reasons,
            },
            passed=passed,
        )
