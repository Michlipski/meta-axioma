"""Acceptance Contract Specification Emitter (`services/research/src/spec_emitter.py`).

Enforces:
- [SPEC-G4B-RESEARCH-001] Machine-Readable Acceptance Contracts (AcceptanceSpecIR).
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G4B-002] Zero-Code Research Tool Boundary (Emits formal schemas and prompt contracts).
- [INV-G4B-CAUSAL-001] Anti-Tautology Falsification Schema & Pre-Audit Verification.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Union

# Ensure protocols directory and repo root are accessible
_gen_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_gen_root) not in sys.path:
    sys.path.insert(0, str(_gen_root))
_repo_root = _gen_root.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

try:
    from generations.gen_04b.protocols.acceptance_spec import (
        AcceptanceProtocolViolation,
        AcceptanceSpecIR,
        DomainArchetype,
        FalsificationVector,
        MutationType,
    )
    from generations.gen_04b.protocols.deliverable_bundle import (
        DeliverableProtocolViolation,
        ResearchDeliverableBundle,
    )
except ImportError:
    from protocols.acceptance_spec import (
        AcceptanceProtocolViolation,
        AcceptanceSpecIR,
        DomainArchetype,
        FalsificationVector,
        MutationType,
    )
    from protocols.deliverable_bundle import (
        DeliverableProtocolViolation,
        ResearchDeliverableBundle,
    )


class DomainArchetypePresetCatalog:
    """Standardized operational constraint profiles and anti-shortcut patterns by application archetype."""

    @staticmethod
    def get_preset(archetype: Union[DomainArchetype, str]) -> Dict[str, Any]:
        """Retrieves default runtimes, banned AST patterns, and verification metrics for an archetype."""
        if isinstance(archetype, str):
            archetype = DomainArchetype(archetype)

        if archetype == DomainArchetype.WEB_CANVAS_INTERACTIVE:
            return {
                "domain_archetype": DomainArchetype.WEB_CANVAS_INTERACTIVE.value,
                "required_runtimes": ["python3", "node"],
                "banned_ast_patterns": [
                    {
                        "pattern": "dynamic_dom_elements",
                        "reason": "No in-memory DOM spoofing; require physical DOM or headless JS probe",
                    },
                    {
                        "pattern": "mock_dom_parser",
                        "reason": "No mock DOM stubs; require headless browser/node execution",
                    },
                    {
                        "pattern": "simulated_canvas_context",
                        "reason": "No synthetic 2D context spoofing without live render verification",
                    },
                ],
                "max_latency_per_step_ms": 100.0,
                "zero_console_panics_required": True,
                "min_statechart_coverage_pct": 95.0,
                "telemetry_digest_required": True,
            }

        elif archetype == DomainArchetype.DISTRIBUTED_MESH_BACKEND:
            return {
                "domain_archetype": DomainArchetype.DISTRIBUTED_MESH_BACKEND.value,
                "required_runtimes": ["python3"],
                "banned_ast_patterns": [
                    {
                        "pattern": "127.0.0.1",
                        "reason": "[L1-G3B-012] Anti-Loopback Invariant: no service or node may bind to loopback IPv4",
                    },
                    {
                        "pattern": "localhost",
                        "reason": "[L1-G3B-012] Anti-Loopback Invariant: loopback hostnames strictly prohibited",
                    },
                    {
                        "pattern": "time.sleep",
                        "reason": "Synchronous blocking sleep in async reactive event loop strictly prohibited",
                    },
                    {
                        "pattern": "MockStreamWriter",
                        "reason": "[NEG-G1B-002] Anti-Mock Subprocess Invariant: in-memory mock streams prohibited",
                    },
                ],
                "max_latency_per_step_ms": 50.0,
                "zero_console_panics_required": True,
                "min_statechart_coverage_pct": 90.0,
                "telemetry_digest_required": True,
            }

        elif archetype == DomainArchetype.CLI_SYSTEM_TOOL:
            return {
                "domain_archetype": DomainArchetype.CLI_SYSTEM_TOOL.value,
                "required_runtimes": ["python3", "bash"],
                "banned_ast_patterns": [
                    {
                        "pattern": "sys.exit(0)",
                        "reason": "Premature exit bypassing cleanup and telemetry flush handlers",
                    },
                    {
                        "pattern": "mock_popen",
                        "reason": "[NEG-G1B-002] Entrypoint smoke tests must spawn real OS subprocesses, not mocks",
                    },
                    {
                        "pattern": "os.system",
                        "reason": "Unsafe shell execution; use subprocess with explicit arg vectors",
                    },
                ],
                "max_latency_per_step_ms": 500.0,
                "zero_console_panics_required": True,
                "min_statechart_coverage_pct": 85.0,
                "telemetry_digest_required": True,
            }

        elif archetype == DomainArchetype.FORMAL_VERIFICATION_KERNEL:
            return {
                "domain_archetype": DomainArchetype.FORMAL_VERIFICATION_KERNEL.value,
                "required_runtimes": ["python3"],
                "banned_ast_patterns": [
                    {
                        "pattern": "return True  # tautological stub",
                        "reason": "Tautological pass in verification theorem strictly prohibited",
                    },
                    {
                        "pattern": "mock_z3_solver",
                        "reason": "Must invoke live Z3 / SMT solver for formal proofs",
                    },
                    {
                        "pattern": "pass  # stub prover",
                        "reason": "Prover must execute formal verification proof steps",
                    },
                ],
                "max_latency_per_step_ms": 1000.0,
                "zero_console_panics_required": True,
                "min_statechart_coverage_pct": 100.0,
                "telemetry_digest_required": True,
            }

        else:
            return {
                "domain_archetype": DomainArchetype.CUSTOM.value,
                "required_runtimes": ["python3"],
                "banned_ast_patterns": [],
                "max_latency_per_step_ms": 200.0,
                "zero_console_panics_required": True,
                "min_statechart_coverage_pct": 90.0,
                "telemetry_digest_required": True,
            }

    @classmethod
    def list_archetypes(cls) -> List[str]:
        return [a.value for a in DomainArchetype]


class AcceptanceSpecEmitter:
    """Authoritative generator of machine-checkable AcceptanceSpecIR contracts."""

    def __init__(self, researcher_id: str = "node_g4b_research_spec_emitter") -> None:
        self.researcher_id = researcher_id

    def derive_from_soc(
        self,
        soc: Any,
        target_enclave_path: str,
        archetype: Optional[DomainArchetype] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> AcceptanceSpecIR:
        """Derives an AcceptanceSpecIR dynamically from a Waterloo Situation of Concern."""
        soc_id = getattr(soc, "soc_id", None) or (soc.get("soc_id") if isinstance(soc, dict) else "SOC-UNKNOWN")
        title = getattr(soc, "title", None) or (soc.get("title") if isinstance(soc, dict) else "Untitled Feature")
        narrative = getattr(soc, "narrative", None) or (soc.get("narrative") if isinstance(soc, dict) else "")

        # Infer archetype from narrative keywords if not explicitly provided
        inferred_archetype = archetype or self._infer_archetype(title, narrative)
        preset = DomainArchetypePresetCatalog.get_preset(inferred_archetype)

        spec_id = f"SPEC-{soc_id}"
        feature_name = title

        # Extract environmental constraints and frictions to synthesize custom banned patterns and vectors
        custom_banned: List[Dict[str, str]] = list(preset.get("banned_ast_patterns", []))
        constraints = getattr(soc, "constraints", []) or (soc.get("constraints", []) if isinstance(soc, dict) else [])
        for c in constraints:
            desc = getattr(c, "description", "") or (c.get("description", "") if isinstance(c, dict) else str(c))
            if "no mock" in desc.lower():
                custom_banned.append({"pattern": "Mock", "reason": f"SoC constraint: {desc}"})
            if "non-loopback" in desc.lower() or "anti-loopback" in desc.lower():
                custom_banned.append({"pattern": "127.0.0.1", "reason": f"SoC constraint: {desc}"})

        # Synthesize standard falsification vectors if none provided
        falsification_vectors: List[FalsificationVector] = []
        frictions = getattr(soc, "frictions", []) or (soc.get("frictions", []) if isinstance(soc, dict) else [])
        for idx, f in enumerate(frictions[:3]):
            f_name = getattr(f, "title", None) or (f.get("title") if isinstance(f, dict) else f"friction_{idx}")
            falsification_vectors.append(
                FalsificationVector(
                    vector_id=f"FV-{soc_id}-{idx+1:02d}",
                    target_file_relative_path=f"{target_enclave_path}/kernel.py",
                    target_symbol_or_pattern=f_name.replace(" ", "_").lower(),
                    mutation_type=MutationType.RETURN_EMPTY.value,
                    expected_failure_exception="FalsificationVerificationFault",
                    reversion_witness_required=True,
                    description=f"Defect injection verifying friction handling for: {f_name}",
                )
            )

        spec_data: Dict[str, Any] = {
            "spec_id": spec_id,
            "feature_name": feature_name,
            "target_enclave_path": target_enclave_path,
            "domain_archetype": inferred_archetype.value,
            "required_runtimes": list(preset.get("required_runtimes", ["python3"])),
            "banned_ast_patterns": custom_banned,
            "falsification_vectors": falsification_vectors,
            "max_latency_per_step_ms": preset.get("max_latency_per_step_ms", 200.0),
            "zero_console_panics_required": preset.get("zero_console_panics_required", True),
            "min_statechart_coverage_pct": preset.get("min_statechart_coverage_pct", 90.0),
            "telemetry_digest_required": preset.get("telemetry_digest_required", True),
            "metadata": {"origin_soc_id": soc_id, "researcher_id": self.researcher_id},
        }

        if overrides:
            spec_data.update(overrides)

        spec = AcceptanceSpecIR.from_dict(spec_data)
        spec.validate_invariants()
        return spec

    def create_from_preset(
        self,
        archetype: DomainArchetype,
        spec_id: str,
        feature_name: str,
        target_enclave_path: str,
        custom_falsification_vectors: Optional[List[FalsificationVector]] = None,
        **kwargs: Any,
    ) -> AcceptanceSpecIR:
        """Instantiates an AcceptanceSpecIR directly from an archetype preset."""
        preset = DomainArchetypePresetCatalog.get_preset(archetype)
        data: Dict[str, Any] = {
            "spec_id": spec_id,
            "feature_name": feature_name,
            "target_enclave_path": target_enclave_path,
            "domain_archetype": archetype.value,
            "required_runtimes": kwargs.get("required_runtimes", preset["required_runtimes"]),
            "banned_ast_patterns": kwargs.get("banned_ast_patterns", preset["banned_ast_patterns"]),
            "falsification_vectors": [
                v.to_dict() if hasattr(v, "to_dict") else v
                for v in (custom_falsification_vectors or [])
            ],
            "max_latency_per_step_ms": kwargs.get("max_latency_per_step_ms", preset["max_latency_per_step_ms"]),
            "zero_console_panics_required": kwargs.get("zero_console_panics_required", preset["zero_console_panics_required"]),
            "min_statechart_coverage_pct": kwargs.get("min_statechart_coverage_pct", preset["min_statechart_coverage_pct"]),
            "telemetry_digest_required": kwargs.get("telemetry_digest_required", preset["telemetry_digest_required"]),
            "metadata": kwargs.get("metadata", {"researcher_id": self.researcher_id}),
        }
        spec = AcceptanceSpecIR.from_dict(data)
        spec.validate_invariants()
        return spec

    def emit_to_file(self, spec: AcceptanceSpecIR, output_path: Union[str, Path]) -> Path:
        """Persists the AcceptanceSpecIR to disk as acceptance_spec.json, asserting non-zero byte emission."""
        path = Path(output_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)

        spec.validate_invariants()
        serialized = json.dumps(spec.to_dict(), indent=2, sort_keys=True)
        path.write_text(serialized, encoding="utf-8")

        if not path.exists() or path.stat().st_size == 0:
            raise AcceptanceProtocolViolation(f"Failed to physically emit non-zero bytes to {path}")

        return path

    def generate_builder_prompt_contract(self, spec: AcceptanceSpecIR) -> str:
        """Generates the strongly-typed prompt constraint block injected into Builder synthesis prompts."""
        runtimes_bullet = ", ".join([f"`{r}`" for r in spec.required_runtimes])
        banned_bullets = "\n".join(
            [f"- **BANNED AST PATTERN:** `{p['pattern']}` — *Rationale:* {p['reason']}" for p in spec.banned_ast_patterns]
        ) or "- None specified."
        falsification_bullets = "\n".join(
            [
                f"- **VECTOR `{v.vector_id}`:** Target `{v.target_file_relative_path}` (`{v.target_symbol_or_pattern}`) — "
                f"Mutation `{v.mutation_type}` must raise `{v.expected_failure_exception}`"
                for v in spec.falsification_vectors
            ]
        ) or "- None specified."

        return f"""### Machine-Checkable Acceptance Contract (`AcceptanceSpecIR: {spec.spec_id}`)
- **Target Enclave Path:** `{spec.target_enclave_path}`
- **Domain Archetype:** `{spec.domain_archetype}`
- **Required External Runtimes:** {runtimes_bullet}
- **Maximum Step Latency:** `{spec.max_latency_per_step_ms}ms`
- **Minimum Statechart Coverage:** `{spec.min_statechart_coverage_pct}%`
- **Spec Digest (SHA-256):** `{spec.compute_spec_hash()}`

#### Strictly Prohibited AST Patterns (Zero-Bypass Interception):
{banned_bullets}

#### Physical Falsification Sinks (Anti-Tautology Verification):
{falsification_bullets}
"""

    def generate_qa_falsification_contract(self, spec: AcceptanceSpecIR) -> str:
        """Generates the automated verification contract injected into Adversarial QA prompts."""
        return f"""### Adversarial QA Falsification Protocol (`{spec.spec_id}`)
1. **Runtime Verification:** Ensure tests execute against live {spec.required_runtimes} runtimes in independent OS subprocesses.
2. **AST Static Scanning:** Inspect emitted files in `{spec.target_enclave_path}` for {len(spec.banned_ast_patterns)} banned patterns.
3. **Physical Mutation Injections:** Execute {len(spec.falsification_vectors)} falsification vectors, proving non-tautological test failures before issuing Merkle attestation.
"""

    def _infer_archetype(self, title: str, narrative: str) -> DomainArchetype:
        """Heuristically infers domain archetype from problem description text."""
        import re
        combined = f"{title} {narrative}".lower()
        if re.search(r"\b(?:canvas|ui|dom|frontend|visual|renderer|interactive)\b", combined):
            return DomainArchetype.WEB_CANVAS_INTERACTIVE
        elif re.search(r"\b(?:mesh|distributed|sheaf|consensus|cluster|socket|network)\b", combined):
            return DomainArchetype.DISTRIBUTED_MESH_BACKEND
        elif re.search(r"\b(?:cli|terminal|command|launcher|argparse)\b", combined):
            return DomainArchetype.CLI_SYSTEM_TOOL
        elif re.search(r"\b(?:z3|smt|formal|prover|theorem|model check)\b", combined):
            return DomainArchetype.FORMAL_VERIFICATION_KERNEL
        return DomainArchetype.CUSTOM
