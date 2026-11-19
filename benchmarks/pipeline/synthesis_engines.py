"""Synthesis Engines for Meta-Axioma Benchmark Pipeline.

Provides:
- BaseSynthesisEngine: Abstract base class for benchmark application synthesis.
- VanillaSynthesisEngine: Single-agent unconstrained prompt synthesis (Antigravity Vanilla baseline).
- AxiomaCausalMeshEngine: 3-Phase Causal Reactive Pipeline orchestrating orthogonal
  subagents (Brain -> Muscle Synthesizer -> Physical Grounding -> Adversarial QA -> Red Team).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from benchmarks.macro_ablation.domain_models import BenchmarkArchetype
from generations.gen_04b.compiler.orchestrator import CompilationRequest, SystemG4bCompiler
from generations.gen_04b.protocols.acceptance_spec import DomainArchetype
from generations.gen_04b.protocols.ipc_transport import TransportMode


class SynthesisViolation(Exception):
    """Base exception for synthesis engine violations."""
    pass


class PhantomEmissionViolation(SynthesisViolation):
    """Raised when declared application files are missing or empty on disk ([NEG-G1B-001])."""
    pass


class SubprocessSmokeViolation(SynthesisViolation):
    """Raised when entrypoint script crashes during isolated subprocess execution ([NEG-G1B-002])."""
    pass


@dataclass
class SynthesisResult:
    """Certified outcome of a benchmark candidate synthesis run."""
    success: bool
    app_dir: Path
    subagent_witnesses: List[Dict[str, Any]] = field(default_factory=list)
    manifest: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    execution_duration_sec: float = 0.0


class BaseSynthesisEngine(ABC):
    """Abstract base class for benchmark candidate synthesis engines."""

    @abstractmethod
    def synthesize(
        self,
        archetype: BenchmarkArchetype,
        target_dir: Path,
        subagent_invoker: Optional[Callable[[str, str, str], str]] = None,
    ) -> SynthesisResult:
        """Synthesizes an application candidate into target_dir."""
        pass

    def compute_disk_grounding(self, target_dir: Path) -> Dict[str, Dict[str, Any]]:
        """Physically scans disk, asserting non-zero byte size and recording SHA-256 hashes."""
        target_dir = Path(target_dir).resolve()
        grounded_files = {}
        for f in sorted(target_dir.rglob("*")):
            if f.is_file() and "__pycache__" not in str(f):
                content = f.read_bytes()
                if len(content) == 0:
                    raise PhantomEmissionViolation(f"Zero-byte empty file detected: {f.relative_to(target_dir)}")
                rel_path = str(f.relative_to(target_dir))
                sha = hashlib.sha256(content).hexdigest()
                grounded_files[rel_path] = {
                    "bytes": len(content),
                    "sha256": sha,
                }
        if not grounded_files:
            raise PhantomEmissionViolation(f"No files were emitted into target directory: {target_dir}")
        return grounded_files

    def write_manifest(
        self,
        target_dir: Path,
        system_id: str,
        is_multi_agent: bool,
        subagents: List[Dict[str, Any]],
        archetype_id: str,
        grounded_files: Dict[str, Dict[str, Any]],
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Writes synthesis_manifest.json into target_dir for ProvenanceEvaluator inspection."""
        target_dir = Path(target_dir).resolve()
        manifest_data = {
            "timestamp": int(time.time()),
            "system_id": system_id,
            "archetype_id": archetype_id,
            "is_multi_agent": is_multi_agent,
            "subagents": subagents,
            "grounded_files_count": len(grounded_files),
            "files": grounded_files,
        }
        if extra_fields:
            manifest_data.update(extra_fields)
        manifest_path = target_dir / "synthesis_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)
        return manifest_path


class VanillaSynthesisEngine(BaseSynthesisEngine):
    """Single-Agent Unconstrained Synthesis Engine (Antigravity Vanilla Baseline)."""

    def __init__(
        self,
        system_id: str = "antigravity_vanilla",
        contract_parity: bool = True,
    ) -> None:
        self.system_id = system_id
        self.contract_parity = bool(contract_parity)

    def build_prompt(self, archetype: BenchmarkArchetype, target_dir: Path) -> str:
        """Builds the Vanilla prompt in either contract-parity (default) or legacy prose-only mode."""
        target_dir = Path(target_dir).resolve()
        if not self.contract_parity:
            return (
                f"You are an autonomous software developer working directly on a coding task.\n"
                f"Your task is to build a standalone, production-ready daemon in Python 3.14 based on this requirement:\n\n"
                f'"{archetype.prompt}"\n\n'
                f"Target Output Directory:\n"
                f"You must write all your implementation files into:\n"
                f"{target_dir}/\n\n"
                f"Requirements:\n"
                f"1. Provide an entrypoint executable script at:\n"
                f"   {target_dir}/run.py\n"
                f"   It must accept CLI arguments: `--port <port>` (default 8088), `--smoke-test` (prints an operational status confirmation and exits cleanly with 0).\n"
                f"2. Put any supporting modules into:\n"
                f"   {target_dir}/src/\n"
                f"3. Use standard Python 3.14 libraries only.\n"
                f"4. Physically write every module directly to disk.\n"
            )

        spec = getattr(archetype, "specification", None) or {}
        is_cli_stdin = (
            "micro" in archetype.id.lower()
            or str(spec.get("execution_mode", "")).upper() == "STREAMING_STDIN_CLI"
        )
        models_block = "\n".join(f"  - `{m}`" for m in (archetype.expected_models or [])) or "  - None specified"
        verbs_block = "\n".join(f"  - `{v}`" for v in (archetype.expected_verbs or [])) or "  - None specified"

        endpoints = archetype.expected_endpoints or []
        if endpoints:
            endpoints_section = (
                "Required HTTP Endpoints:\n"
                + "\n".join(f"  - `{ep}`" for ep in endpoints)
                + "\n\n"
            )
        else:
            endpoints_section = ""

        valid_transitions = [t for t in (archetype.state_transitions or []) if t.get("valid", True)]
        illegal_transitions = [t for t in (archetype.state_transitions or []) if not t.get("valid", True)]
        transitions_lines: List[str] = []
        if valid_transitions:
            transitions_lines.append("  Valid Transitions (must succeed and update state):")
            for t in valid_transitions:
                transitions_lines.append(
                    f"    - `{t.get('from')}` --(`{t.get('action')}`)--> `{t.get('to')}`"
                )
        if illegal_transitions:
            transitions_lines.append("  Illegal Transitions (must raise/reject and preserve state):")
            for t in illegal_transitions:
                transitions_lines.append(
                    f"    - `{t.get('from')}` --(`{t.get('action')}`)--> `{t.get('to')}` [FORBIDDEN]"
                )
        transitions_block = "\n".join(transitions_lines) or "  - None specified"

        if is_cli_stdin:
            cli_contract = (
                f"1. Provide an executable CLI entrypoint at `{target_dir}/run.py` using strict `argparse` "
                f"(must reject unknown CLI flags with non-zero exit code 2).\n"
                f"   - Support `--smoke-test` (runs self-contained verification, prints status, exits 0).\n"
                f"   - Default mode streams NDJSON from stdin and emits summary statistics cleanly on EOF or SIGINT.\n"
            )
        else:
            cli_contract = (
                f"1. Provide an executable entrypoint at `{target_dir}/run.py` using strict `argparse` "
                f"(must reject unknown CLI flags with non-zero exit code 2).\n"
                f"   - Support `--port <port>` (default 8088) and `--smoke-test` (prints operational status confirmation and exits cleanly with 0).\n"
            )

        return (
            f"You are an autonomous software developer working directly on a coding task.\n"
            f"Build a standalone, production-ready application in Python 3.14 based on this requirement:\n\n"
            f'"{archetype.prompt}"\n\n'
            f"Target Output Directory:\n"
            f"Write all implementation files into `{target_dir}/`.\n\n"
            f"Explicit Interface Contract (Contract-Parity Specification):\n"
            f"Required Domain Models (exact class names):\n"
            f"{models_block}\n\n"
            f"Required Verbs / Methods (exact function/method names):\n"
            f"{verbs_block}\n\n"
            f"{endpoints_section}"
            f"Required Statechart Transitions:\n"
            f"{transitions_block}\n\n"
            f"Runtime & Hygiene Requirements:\n"
            f"{cli_contract}"
            f"2. Use pure Python 3.14 standard library only (zero third-party dependencies).\n"
            f"3. Do NOT hardcode `/tmp` or `/private/tmp`; keep any scratch/data files relative to the working or configured data directory.\n"
            f"4. Physically write every module directly to disk.\n"
        )

    def synthesize(
        self,
        archetype: BenchmarkArchetype,
        target_dir: Path,
        subagent_invoker: Optional[Callable[[str, str, str], str]] = None,
    ) -> SynthesisResult:
        start_time = time.time()
        target_dir = Path(target_dir).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        prompt = self.build_prompt(archetype, target_dir)

        subagents_witnesses = []
        if subagent_invoker:
            cid = subagent_invoker(
                "Vanilla Developer Agent",
                prompt,
                "flash",
            )
            subagents_witnesses.append({
                "role": "Vanilla Developer Agent",
                "cognitive_role": "UNCONSTRAINED_DEVELOPER",
                "conversation_id": cid,
                "timestamp": int(time.time()),
            })

        # Phase 2B Disk Grounding
        grounded_files = self.compute_disk_grounding(target_dir)

        # Emit Provenance Manifest
        manifest_path = self.write_manifest(
            target_dir=target_dir,
            system_id=self.system_id,
            is_multi_agent=False,
            subagents=subagents_witnesses,
            archetype_id=archetype.id,
            grounded_files=grounded_files,
            extra_fields={"contract_parity": self.contract_parity},
        )

        duration = time.time() - start_time
        return SynthesisResult(
            success=True,
            app_dir=target_dir,
            subagent_witnesses=subagents_witnesses,
            manifest=json.loads(manifest_path.read_text(encoding="utf-8")),
            execution_duration_sec=duration,
        )


class AxiomaCausalMeshEngine(BaseSynthesisEngine):
    """3-Phase Causal Reactive Pipeline Synthesis Engine (Meta-Axioma Sovereign Mesh)."""

    def __init__(
        self,
        system_id: str = "meta_axioma_g4b",
        lenient_acceptance_gate: bool = False,
        max_remediation_cycles: int = 2,
    ) -> None:
        self.system_id = system_id
        self.lenient_acceptance_gate = lenient_acceptance_gate
        self.max_remediation_cycles = max(0, int(max_remediation_cycles))

    def _resolve_domain_archetype(self, archetype: BenchmarkArchetype) -> str:
        """Maps a BenchmarkArchetype to its corresponding Gen 4b DomainArchetype value."""
        explicit = getattr(archetype, "domain_archetype", None)
        if explicit:
            return str(explicit)
        arch_id = (getattr(archetype, "id", "") or "").lower()
        spec = getattr(archetype, "specification", None) or {}
        exec_mode = str(spec.get("execution_mode", "")).upper()
        if "micro" in arch_id or "CLI" in exec_mode or "STDIN" in exec_mode:
            return DomainArchetype.CLI_SYSTEM_TOOL.value
        return DomainArchetype.DISTRIBUTED_MESH_BACKEND.value

    def synthesize(
        self,
        archetype: BenchmarkArchetype,
        target_dir: Path,
        subagent_invoker: Optional[Callable[[str, str, str], str]] = None,
    ) -> SynthesisResult:
        start_time = time.time()
        target_dir = Path(target_dir).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        if not subagent_invoker:
            raise SynthesisViolation("AxiomaCausalMeshEngine requires a live subagent_invoker callback to enforce Directive 5")

        compiler = SystemG4bCompiler(transport_mode=TransportMode.LOCAL_IPC)
        request = CompilationRequest(
            app_id=archetype.id,
            app_name=archetype.name,
            target_output_dir=target_dir,
            waterloo_soc_prompt=getattr(archetype, "prompt", f"Build {archetype.name} under Waterloo Tier 1 SoC"),
            domain_archetype=self._resolve_domain_archetype(archetype),
            expected_verbs=getattr(archetype, "expected_verbs", None),
            expected_endpoints=getattr(archetype, "expected_endpoints", None),
            subagent_invoker=subagent_invoker,
            require_live_subagents=True,
            max_remediation_cycles=self.max_remediation_cycles,
            transport_mode=TransportMode.LOCAL_IPC.value,
            metadata={"lenient_acceptance_gate": self.lenient_acceptance_gate},
        )
        report = compiler.compile(request, subagent_invoker=subagent_invoker, require_live_subagents=True)
        if not report.success:
            raise SynthesisViolation(f"SystemG4bCompiler execution failed: {report.error_message}")

        grounded_files = self.compute_disk_grounding(target_dir)

        manifest_path = self.write_manifest(
            target_dir=target_dir,
            system_id=self.system_id,
            is_multi_agent=True,
            subagents=report.subagent_witnesses,
            archetype_id=archetype.id,
            grounded_files=grounded_files,
        )

        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_data["g4b_compilation"] = {
            "merkle_root": report.merkle_root,
            "acceptance_spec_hash": report.acceptance_spec_hash,
            "research_bundle_id": report.research_bundle_id,
            "statechart_coverage_pct": report.statechart_coverage_pct,
            "phases_executed": report.phases_executed,
            "verification_mode": report.verification_mode,
            "audit_passed": report.audit_passed,
            "governance_certified": report.governance_certified,
            "acceptance_gate_passed": report.audit_passed,
            "acceptance_gate_violations": list(report.acceptance_gate_violations),
            "red_team_passed": report.red_team_passed,
            "critical_vulnerabilities_found": report.critical_vulnerabilities_found,
            "red_team_verdict": report.red_team_verdict,
            "remediation_cycles_executed": report.remediation_cycles_executed,
        }
        manifest_data["merkle_root"] = report.merkle_root
        manifest_data["acceptance_spec_hash"] = report.acceptance_spec_hash
        manifest_data["research_bundle_id"] = report.research_bundle_id
        manifest_data["statechart_coverage_pct"] = report.statechart_coverage_pct
        manifest_data["subagent_witnesses"] = report.subagent_witnesses
        manifest_data["red_team_passed"] = report.red_team_passed
        manifest_data["critical_vulnerabilities_found"] = report.critical_vulnerabilities_found
        manifest_data["red_team_verdict"] = report.red_team_verdict
        manifest_data["remediation_cycles_executed"] = report.remediation_cycles_executed
        manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

        duration = time.time() - start_time
        return SynthesisResult(
            success=True,
            app_dir=target_dir,
            subagent_witnesses=report.subagent_witnesses,
            manifest=manifest_data,
            execution_duration_sec=duration,
        )
