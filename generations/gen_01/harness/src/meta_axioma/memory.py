"""Persistent Markdown Memory Engine for AXIOMS.md and ARCHITECTURE.md."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple, Optional

from meta_axioma.types import (
    Axiom,
    AxiomLevel,
    AxiomStatus,
    NegativeAxiom,
    PhaseState,
    TriFoldMetrics,
)


class PersistentMemoryManager:
    """Synchronizes in-memory system state with markdown persistent memory files."""

    def __init__(self, axioms_path: Path, architecture_path: Path):
        self.axioms_path = axioms_path
        self.architecture_path = architecture_path

    def load_axioms(self) -> Tuple[List[Axiom], List[NegativeAxiom]]:
        """Parses active and recorded axioms and negative invariants from axioms markdown file."""
        target_path = self.axioms_path
        if not target_path.exists():
            for alt in [target_path.parent / "AXIOMS.md", target_path.parent / "gen_01_axioms.md", target_path.parent / "generation_01_axioms.md"]:
                if alt.exists():
                    target_path = alt
                    break
        if not target_path.exists():
            return [], []

        content = target_path.read_text(encoding="utf-8")
        axioms: List[Axiom] = []
        negative_axioms: List[NegativeAxiom] = []

        # Parse Axiom blocks: ### [ID] Name
        axiom_pattern = re.compile(
            r"###\s*\[(?P<id>[\w\-]+)\]\s*(?P<name>[^\n]+)\n"
            r"(?:- \*\*Level:\*\*\s*(?P<level>[^\n]+)\n)?"
            r"(?:- \*\*Status:\*\*\s*(?P<status>[^\n]+)\n)?"
            r"(?:- \*\*Origin Epoch:\*\*\s*(?P<epoch>[^\n]+)\n)?"
            r"(?:- \*\*Statement:\*\*\s*(?P<statement>[^\n]+)\n)?"
            r"(?:- \*\*Formal Expression:\*\*\s*(?P<formal>[^\n]+|\$\$[\s\S]*?\$\$)\n)?"
            r"(?:- \*\*Operational Rule:\*\*\s*(?P<rule>[^\n]+))?",
            re.MULTILINE,
        )

        for match in axiom_pattern.finditer(content):
            ax_id = match.group("id").strip()
            name = match.group("name").strip()
            raw_level = match.group("level") or "Level 0"
            raw_status = match.group("status") or "Active"
            raw_epoch = match.group("epoch") or "0"
            statement = match.group("statement") or ""
            formal = match.group("formal") or ""
            rule = match.group("rule") or ""

            # Normalize level
            level = (
                AxiomLevel.LEVEL_1_STRUCTURAL
                if "Level 1" in raw_level or "Structural" in raw_level
                else AxiomLevel.LEVEL_0_EPISTEMIC
            )

            # Normalize status
            status_map = {
                "active": AxiomStatus.ACTIVE,
                "candidate": AxiomStatus.CANDIDATE,
                "inactive": AxiomStatus.INACTIVE,
                "pruned": AxiomStatus.INACTIVE,
                "rejected": AxiomStatus.REJECTED,
                "vetoed": AxiomStatus.VETOED,
            }
            status = status_map.get(raw_status.strip().lower(), AxiomStatus.ACTIVE)

            # Extract epoch number
            epoch_digits = re.findall(r"\d+", raw_epoch)
            epoch_num = int(epoch_digits[0]) if epoch_digits else 0

            axioms.append(
                Axiom(
                    id=ax_id,
                    level=level,
                    name=name,
                    statement=statement.strip(),
                    formal_expression=formal.strip(),
                    operational_rule=rule.strip(),
                    status=status,
                    origin_epoch=epoch_num,
                )
            )

        # Parse Negative Axioms if any exist
        neg_section = re.search(
            r"## Negative Axiom Invariant Registry[\s\S]*?(?=## Axiom Lifecycle Log|$)",
            content,
        )
        if neg_section:
            neg_text = neg_section.group(0)
            neg_blocks = re.findall(
                r"- \*\*\[(?P<id>[\w\-]+)\]\s*(?P<name>[^\*]+)\*\*:\s*(?P<pattern>[^\(]+)\s*\(Rationale:\s*(?P<rationale>[^\)]+)\)",
                neg_text,
            )
            for n_id, n_name, n_pat, n_rat in neg_blocks:
                negative_axioms.append(
                    NegativeAxiom(
                        id=n_id.strip(),
                        name=n_name.strip(),
                        forbidden_pattern=n_pat.strip(),
                        rationale=n_rat.strip(),
                        injected_at_epoch=0,
                        is_active=True,
                    )
                )

        return axioms, negative_axioms

    def load_architecture_state(self) -> Tuple[int, PhaseState, float]:
        """Reads current epoch, phase state, and global efficacy from architecture markdown file."""
        target_path = self.architecture_path
        if not target_path.exists():
            for alt in [target_path.parent / "ARCHITECTURE.md", target_path.parent / "gen_01_architecture.md", target_path.parent / "generation_01_architecture.md"]:
                if alt.exists():
                    target_path = alt
                    break
        if not target_path.exists():
            return 0, PhaseState.PHASE_1_META_EXPLORATION, 1.0

        content = target_path.read_text(encoding="utf-8")

        # Epoch
        epoch_match = re.search(r"\*\*Current Epoch:\*\*\s*(\d+)", content)
        epoch = int(epoch_match.group(1)) if epoch_match else 0

        # Phase
        phase = PhaseState.PHASE_1_META_EXPLORATION
        phase_match = re.search(r"\*\*Phase:\*\*\s*`?([A-Za-z0-9_]+)`?", content)
        if phase_match:
            raw_phase = phase_match.group(1).strip()
            if "PHASE_2" in raw_phase:
                phase = PhaseState.PHASE_2_STRUCTURAL_EXECUTION
            else:
                phase = PhaseState.PHASE_1_META_EXPLORATION

        # Efficacy
        eff_match = re.search(r"\*\*Baseline Global Efficacy \(\$E\$\):\*\*\s*`?([0-9\.]+)`?", content)
        efficacy = float(eff_match.group(1)) if eff_match else 1.0

        return epoch, phase, efficacy

    def load_trajectory_history(self) -> List[float]:
        """Parses past aggregate delta_e values from architecture trajectory table."""
        target_path = self.architecture_path
        if not target_path.exists():
            for alt in [target_path.parent / "ARCHITECTURE.md", target_path.parent / "gen_01_architecture.md", target_path.parent / "generation_01_architecture.md"]:
                if alt.exists():
                    target_path = alt
                    break
        if not target_path.exists():
            return []
        content = target_path.read_text(encoding="utf-8")
        rows = re.findall(
            r"\|\s*`(\d+)`\s*\|\s*\d+\s*\|\s*[\d,]+\s*\|\s*([+\-\d\.]+)\s*\|\s*([+\-\d\.]+)\s*\|\s*([+\-\d\.]+)\s*\|\s*([+\-\d\.]+)\s*\|",
            content,
        )
        deltas: List[float] = []
        for r in rows:
            epoch_num = int(r[0])
            if epoch_num > 0:
                try:
                    deltas.append(float(r[4]))
                except ValueError:
                    pass
        return deltas

    def sync_axioms_file(
        self,
        axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
        phase: PhaseState = PhaseState.PHASE_1_META_EXPLORATION,
        lifecycle_logs: Optional[List[dict]] = None,
    ) -> None:
        """Serializes current axiom registry back into AXIOMS.md."""
        if lifecycle_logs is None:
            lifecycle_logs = []
        active_axioms = [a for a in axioms if a.status == AxiomStatus.ACTIVE]
        l0_active = [a for a in axioms if a.level == AxiomLevel.LEVEL_0_EPISTEMIC]
        l1_active = [a for a in axioms if a.level == AxiomLevel.LEVEL_1_STRUCTURAL]

        lines = [
            "# Active Axiom Registry",
            "",
            "This document serves as the persistent memory and rule engine registry for the Axiom Bootstrapper. It maintains the canonical state of all active, candidate, pruned, and vetoed axioms across execution epochs.",
            "",
            "---",
            "",
            "## Registry Metadata",
            f"- **Status:** Operational",
            f"- **Phase:** {phase.value}",
            f"- **Total Active Axioms:** {len(active_axioms)}",
            f"- **Active Level 0:** {len([a for a in l0_active if a.status == AxiomStatus.ACTIVE])}",
            f"- **Inactive Level 0 (Archived Scaffolding):** {len([a for a in l0_active if a.status == AxiomStatus.INACTIVE])}",
            f"- **Active Level 1:** {len([a for a in l1_active if a.status == AxiomStatus.ACTIVE])}",
            "",
            "---",
            "",
            "## Level 0: Meta / Epistemic Axioms (How to Research)",
            "*Epistemic axioms govern hypothesis generation, exploration heuristics, and evaluation discipline. Upon Phase Transition (The Jettison), these transition to INACTIVE scaffolding and are preserved in persistent memory and the UI for architectural provenance and lineage.*",
            "",
        ]

        if not l0_active:
            lines.append("*(No Level 0 axioms currently recorded.)*\n")
        else:
            for ax in l0_active:
                lines.extend(self._format_axiom_block(ax))

        lines.extend([
            "---",
            "",
            "## Level 1: Structural Axioms (System Design)",
            "*Structural axioms dictate physical, computational, and architectural invariants for compiling target systems. These persist post-jettison and form the final system specification.*",
            "",
        ])

        if not l1_active:
            lines.append("*(No Level 1 structural axioms active yet.)*\n")
        else:
            for ax in l1_active:
                lines.extend(self._format_axiom_block(ax))

        lines.extend([
            "---",
            "",
            "## Negative Axiom Invariant Registry (Human Vetoes)",
            "*Negative axioms define forbidden architectural states injected via Human-in-the-Loop (HITL) interrupts. These represent hard invariants that candidates must never violate.*",
            "",
        ])

        if not negative_axioms:
            lines.append("*(None injected yet.)*\n")
        else:
            for neg in negative_axioms:
                active_str = "ACTIVE" if neg.is_active else "INACTIVE"
                lines.append(
                    f"- **[{neg.id}] {neg.name}** [{active_str}]: {neg.forbidden_pattern} (Rationale: {neg.rationale})\n"
                )

        lines.extend([
            "---",
            "",
            "## Axiom Lifecycle Log",
            "",
            "| Axiom ID | Level | Name | Epoch | Action | $\\Delta E$ | Status |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ])

        for log in lifecycle_logs:
            lines.append(
                f"| `{log.get('id', '-')}` | {log.get('level', '-')} | {log.get('name', '-')} | "
                f"{log.get('epoch', 0)} | {log.get('action', '-')} | {log.get('delta_e', 0.0):+.4f} | {log.get('status', '-')} |"
            )

        lines.append("")
        self.axioms_path.write_text("\n".join(lines), encoding="utf-8")

    def _format_axiom_block(self, ax: Axiom) -> List[str]:
        return [
            f"### [{ax.id}] {ax.name}",
            f"- **Level:** {'Level 0 (Meta/Epistemic)' if ax.level == AxiomLevel.LEVEL_0_EPISTEMIC else 'Level 1 (Structural)'}",
            f"- **Status:** {ax.status.value}",
            f"- **Origin Epoch:** Epoch {ax.origin_epoch}",
            f"- **Statement:** {ax.statement}",
            f"- **Formal Expression:** {ax.formal_expression}",
            f"- **Operational Rule:** {ax.operational_rule}",
            "",
        ]

    def record_epoch_architecture(
        self,
        epoch: int,
        phase: PhaseState,
        global_efficacy: float,
        efficacy_derivative: float,
        active_count: int,
        compute_tokens: int,
        metrics: Optional[TriFoldMetrics],
        status_action: str,
    ) -> None:
        """Appends or updates ARCHITECTURE.md with latest telemetry and epoch log."""
        if not self.architecture_path.exists():
            return

        content = self.architecture_path.read_text(encoding="utf-8")

        # Update metadata section using lambda replacements to avoid regex escape errors
        content = re.sub(
            r"\*\*Current Epoch:\*\*\s*[^\n]+",
            lambda _: f"**Current Epoch:** {epoch}",
            content,
        )
        content = re.sub(
            r"\*\*Phase:\*\*\s*[^\n]+",
            lambda _: f"**Phase:** `{phase.value}`",
            content,
        )
        content = re.sub(
            r"\*\*Baseline Global Efficacy \(\$E\$\):\*\*\s*[^\n]+",
            lambda _: f"**Baseline Global Efficacy ($E$):** `{global_efficacy:.4f}`",
            content,
        )
        content = re.sub(
            r"\*\*Efficacy Derivative[^\n:]*:\*\*\s*[^\n]+",
            lambda _: f"**Efficacy Derivative ($\\frac{{dE}}{{dt}}$):** `{efficacy_derivative:+.4f}`",
            content,
        )

        # Append row to Epoch Trajectory Log if table exists
        table_pattern = re.compile(
            r"(\| Epoch \| Active \$n\$ \| Compute Budget \$T\(n\)\$ \| \$\\Delta E_1\$ \| \$\\Delta E_2\$ \| \$\\Delta E_3\$ \| Aggregate \$\\Delta E\$ \| Phase \| Action / Status \|\n\| :--- [^\n]+\n)((?:\|[^\n]+\n*)+)"
        )
        match = table_pattern.search(content)
        if match:
            table_header = match.group(1)
            existing_rows = match.group(2).strip()

            e1_str = f"{metrics.delta_e1:+.4f}" if metrics else "0.0000"
            e2_str = f"{metrics.delta_e2:+.4f}" if metrics else "0.0000"
            e3_str = f"{metrics.delta_e3:+.4f}" if metrics else "0.0000"
            agg_str = f"{metrics.aggregate_delta_e:+.4f}" if metrics else "0.0000"
            phase_short = "Phase 2" if phase == PhaseState.PHASE_2_STRUCTURAL_EXECUTION else "Phase 1"

            new_row = f"| `{epoch}` | {active_count} | {compute_tokens:,} | {e1_str} | {e2_str} | {e3_str} | {agg_str} | {phase_short} | {status_action} |"
            
            # Avoid duplicate rows for the same epoch
            row_lines = [r for r in existing_rows.splitlines() if r.startswith("|") and not r.startswith(f"| `{epoch}` |")]
            row_lines.append(new_row)
            updated_rows = "\n".join(row_lines) + "\n"

            content = content[:match.start(2)] + updated_rows + content[match.end(2):]

        self.architecture_path.write_text(content, encoding="utf-8")
