"""Quality-Diversity MAP-Elites Behavioral Archive for System G_1 Compiler.

Implements multi-dimensional behavioral preservation across:
1. Consistency Rate (0.0 to 1.0)
2. Partition Survival Rate (0.0 to 1.0)
3. Landauer Thermodynamic Efficiency (Erased Bits / Dissipated Heat)

Ensures stepping-stone architectures are preserved across evolutionary cycles,
preventing premature greedy collapse into suboptimal local minima.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from g1_compiler.types import BehavioralNiche, CandidateArchitecture, CrucibleReport


class MapElitesArchive:
    """Multidimensional Quality-Diversity archive indexing elites by behavioral niche."""

    def __init__(self, brackets_per_dim: int = 5):
        self.brackets = brackets_per_dim
        self.grid: Dict[BehavioralNiche, Tuple[CandidateArchitecture, CrucibleReport]] = {}
        self.total_evaluations = 0

    def compute_niche(self, report: CrucibleReport) -> BehavioralNiche:
        """Maps a crucible report to behavioral niche coordinates."""
        # 1. Consistency Bracket: [0, 4]
        if report.consistency_rate < 0.70:
            c_bracket = 0
        elif report.consistency_rate < 0.80:
            c_bracket = 1
        elif report.consistency_rate < 0.88:
            c_bracket = 2
        elif report.consistency_rate < 0.94:
            c_bracket = 3
        else:
            c_bracket = 4

        # 2. Partition Survival Bracket: [0, 4]
        if report.partition_survival_rate < 0.70:
            p_bracket = 0
        elif report.partition_survival_rate < 0.80:
            p_bracket = 1
        elif report.partition_survival_rate < 0.88:
            p_bracket = 2
        elif report.partition_survival_rate < 0.94:
            p_bracket = 3
        else:
            p_bracket = 4

        # 3. Thermal Efficiency Bracket: [0, 4] (Fewer erased bits = higher bracket)
        if report.erased_bits > 160.0:
            t_bracket = 0
        elif report.erased_bits > 120.0:
            t_bracket = 1
        elif report.erased_bits > 80.0:
            t_bracket = 2
        elif report.erased_bits > 40.0:
            t_bracket = 3
        else:
            t_bracket = 4

        return BehavioralNiche(
            consistency_bracket=c_bracket,
            partition_bracket=p_bracket,
            thermal_bracket=t_bracket,
        )

    def calculate_fitness(self, report: CrucibleReport) -> float:
        """Calculates scalar fitness across consistency, partition survival, and thermodynamic efficiency."""
        # Penalize falsified / dead-end architectures
        if report.is_falsified:
            return 0.1 * report.consistency_rate

        thermal_score = max(0.0, 1.0 - (report.erased_bits / 256.0))
        latency_score = max(0.0, 1.0 - (report.p99_latency_ms / 200.0))

        return (
            (0.45 * report.consistency_rate)
            + (0.30 * report.partition_survival_rate)
            + (0.15 * thermal_score)
            + (0.10 * latency_score)
        )

    def add_candidate(
        self,
        candidate: CandidateArchitecture,
        report: CrucibleReport,
    ) -> bool:
        """Inserts candidate into the archive if niche is empty or if it outperforms existing occupant."""
        self.total_evaluations += 1
        niche = self.compute_niche(report)
        fitness = self.calculate_fitness(report)

        if niche not in self.grid:
            self.grid[niche] = (candidate, report)
            return True

        _, current_report = self.grid[niche]
        current_fitness = self.calculate_fitness(current_report)

        if fitness > current_fitness:
            self.grid[niche] = (candidate, report)
            return True

        return False

    def get_elite(self, niche: BehavioralNiche) -> Optional[Tuple[CandidateArchitecture, CrucibleReport]]:
        """Returns the elite occupying a specific behavioral niche."""
        return self.grid.get(niche)

    def get_all_elites(self) -> List[Tuple[CandidateArchitecture, CrucibleReport]]:
        """Returns all current elites across occupied niches."""
        return list(self.grid.values())

    def get_coverage(self) -> float:
        """Returns grid coverage ratio (occupied cells / total available niche cells)."""
        total_cells = self.brackets ** 3
        return len(self.grid) / float(total_cells)

    def select_pareto_winner(self) -> Tuple[CandidateArchitecture, CrucibleReport]:
        """Selects the highest fitness elite among surviving (non-falsified) candidates."""
        surviving = [
            (c, r) for c, r in self.grid.values()
            if not r.is_falsified and r.passed
        ]
        if not surviving:
            # Fallback to absolute highest fitness
            all_entries = list(self.grid.values())
            if not all_entries:
                raise ValueError("Cannot select winner from an empty MAP-Elites archive.")
            return max(all_entries, key=lambda pair: self.calculate_fitness(pair[1]))

        return max(surviving, key=lambda pair: self.calculate_fitness(pair[1]))
