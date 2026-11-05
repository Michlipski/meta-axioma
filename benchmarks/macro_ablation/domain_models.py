"""Domain Models for the Meta-Axioma Macro-Ablation Benchmark (`Axioma Macro-Bench`).

Defines:
- AblationMode: The 5 formal evaluation configurations.
- BenchmarkArchetype: Specification, prompt, expected verbs/endpoints/models, and test suites.
- Tier0LivenessResult: Result of the mandatory OS subprocess smoke boot gate.
- EvaluationPassResult: Detailed result of each scoring dimension.
- MacroScorecard: Per-archetype, per-ablation evaluation scorecard.
- MacroBenchmarkReport: Aggregate multi-archetype benchmark report and markdown matrix.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import json
import time
from typing import Any, Dict, List, Optional


class AblationMode(str, Enum):
    """The 5 formal ablation configurations evaluated in Meta-Axioma Macro-Bench."""
    FULL_G4B = "full_g4b"
    FLAT_PROMPT_LLM = "flat_prompt_llm"
    WO_CONTRACTS_SMT = "wo_contracts_smt"
    WO_AST_AUDITORS = "wo_ast_auditors"
    WO_SUBPROCESS_SMOKE = "wo_subprocess_smoke"

    @property
    def display_name(self) -> str:
        mapping = {
            AblationMode.FULL_G4B: "Full Architecture (G4b Baseline)",
            AblationMode.FLAT_PROMPT_LLM: "Ablation 1: Flat Prompt LLM (Unverified)",
            AblationMode.WO_CONTRACTS_SMT: "Ablation 2: w/o Formal Contracts & SMT",
            AblationMode.WO_AST_AUDITORS: "Ablation 3: w/o Zero-Trust AST Micro-Auditors",
            AblationMode.WO_SUBPROCESS_SMOKE: "Ablation 4: w/o Subprocess Smoke Gate",
        }
        return mapping.get(self, self.value)

    @property
    def description(self) -> str:
        mapping = {
            AblationMode.FULL_G4B: "Complete Meta-Axioma stack: Waterloo SoC -> ContractIR -> Z3 SMT -> Statecharts -> Micro-Auditing -> Subprocess Smoke -> Byzantine QA.",
            AblationMode.FLAT_PROMPT_LLM: "Direct single-pass prompt-to-code generation simulating standard Copilot/Claude without formal constraints.",
            AblationMode.WO_CONTRACTS_SMT: "Synthesis without domain contract preconditions/postconditions or symbolic proofs.",
            AblationMode.WO_AST_AUDITORS: "Synthesis without AST pre-emission linting or hermetic call interception.",
            AblationMode.WO_SUBPROCESS_SMOKE: "Synthesis relying strictly on in-memory mock unit tests without physical OS subprocess smoke execution.",
        }
        return mapping.get(self, "")


@dataclass
class BenchmarkArchetype:
    """Formal specification for a macro-level benchmark application archetype."""
    id: str
    name: str
    domain: str
    prompt: str
    specification: Dict[str, Any]
    expected_verbs: List[str]
    expected_endpoints: List[str]
    expected_models: List[str]
    state_transitions: List[Dict[str, Any]]
    chaos_payloads: List[Dict[str, Any]]
    target_loc_budget: int = 350
    target_token_budget: int = 15000

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Tier0LivenessResult:
    """Outcome of the Tier 0 Operational Liveness Gatekeeper ([NEG-G1B-002])."""
    passed: bool
    startup_time_ms: float = 0.0
    clean_shutdown: bool = True
    port_bound: Optional[int] = None
    error_message: Optional[str] = None
    exit_code: Optional[int] = None
    stdout_excerpt: str = ""
    stderr_excerpt: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvaluationPassResult:
    """Result of an individual graded evaluation pass (Passes 1–5)."""
    pass_name: str
    weight: float
    raw_score: float  # Bounded [0.0, 100.0]
    weighted_score: float  # raw_score * weight
    details: Dict[str, Any] = field(default_factory=dict)
    passed: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MacroScorecard:
    """Full evaluation scorecard for a single archetype under a specific ablation mode."""
    archetype_id: str
    ablation_mode: AblationMode
    tier0_liveness: Tier0LivenessResult
    tier0_multiplier: float  # 1.0 if passed else 0.0
    pass_results: Dict[str, EvaluationPassResult]
    graded_score: float
    composite_score: float
    execution_time_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)
    app_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["ablation_mode"] = self.ablation_mode.value
        return d


@dataclass
class MacroBenchmarkReport:
    """Aggregate benchmark report across archetypes and ablation modes."""
    report_id: str
    timestamp: float
    scorecards: List[MacroScorecard]
    summary_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "scorecards": [s.to_dict() for s in self.scorecards],
            "summary_matrix": self.summary_matrix,
        }

    def to_markdown(self) -> str:
        """Renders the comparative ablation matrix in standard GitHub Flavored Markdown."""
        lines = [
            "# Axioma Macro-Bench: Comparative Application Ablation Report",
            f"**Report ID:** `{self.report_id}`  ",
            f"**Timestamp:** `{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(self.timestamp))} UTC`  ",
            "",
            "## 1. Executive Summary Matrix (Composite Score: 0.0 - 100.0)",
            "",
            "| Archetype | Full G4b (Baseline) | Ablation 1 (Flat LLM) | Ablation 2 (w/o Contracts) | Ablation 3 (w/o Auditors) | Ablation 4 (w/o Smoke Gate) |",
            "| :--- | :---: | :---: | :---: | :---: | :---: |",
        ]

        # Gather distinct archetypes
        archetypes = list(self.summary_matrix.keys())
        for arch in sorted(archetypes):
            row_data = self.summary_matrix[arch]
            g4b = f"**{row_data.get(AblationMode.FULL_G4B.value, 0.0):.1f}**"
            llm = f"{row_data.get(AblationMode.FLAT_PROMPT_LLM.value, 0.0):.1f}"
            contracts = f"{row_data.get(AblationMode.WO_CONTRACTS_SMT.value, 0.0):.1f}"
            auditors = f"{row_data.get(AblationMode.WO_AST_AUDITORS.value, 0.0):.1f}"
            smoke = f"{row_data.get(AblationMode.WO_SUBPROCESS_SMOKE.value, 0.0):.1f}"
            lines.append(f"| **{arch}** | {g4b} | {llm} | {contracts} | {auditors} | {smoke} |")

        lines.extend([
            "",
            "## 2. Tier 0 Liveness Impact Note",
            "> [!IMPORTANT]",
            "> Applications where **Tier 0 Operational Liveness = FAIL** (due to top-level import crash, startup panic, or port binding failure) are assigned a **Composite Score of identically 0.0**, enforcing [NEG-G1B-002].",
            "",
            "## 3. Detailed Per-Archetype Dimension Breakdown",
            "",
        ])

        for sc in self.scorecards:
            lines.extend([
                f"### Archetype: `{sc.archetype_id}` | Mode: `{sc.ablation_mode.value}`",
                f"- **Tier 0 Liveness:** {'PASSED (1.0x)' if sc.tier0_liveness.passed else 'FAILED (0.0x)'} (Startup: {sc.tier0_liveness.startup_time_ms:.1f}ms)",
                f"- **Graded Score:** {sc.graded_score:.2f} / 100.0",
                f"- **Composite Score:** **{sc.composite_score:.2f} / 100.0**",
                "",
                "| Pass | Weight | Raw Score | Weighted Score | Status |",
                "| :--- | :---: | :---: | :---: | :---: |",
            ])
            for pass_name, pres in sc.pass_results.items():
                status_icon = "PASS" if pres.passed else "WARN/FAIL"
                lines.append(f"| `{pass_name}` | {pres.weight * 100:.0f}% | {pres.raw_score:.1f} | {pres.weighted_score:.2f} | {status_icon} |")
            lines.append("")

        return "\n".join(lines)
