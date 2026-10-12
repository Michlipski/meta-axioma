---
domain: TelemetryAudit
related_domains:
  - AxiomRegistry
  - EvaluationTargets
---

CONSTRAINTS:
- TelemetryAudit records immutable event logs and serializes epoch snapshots without corrupting execution states.
- Epoch summaries are persisted to the active generation directory (`generations/gen_XX/epochs/`).
- Interactive HTML dashboards are updated dynamically after each epoch.

GLOSSARY:
- EpochTelemetry: Complete state snapshot of an executed epoch including tournament leaderboard, metrics, and decisions.
- TelemetryEvent: Low-latency event payload dispatched across internal routers.
- Dashboard Artifact: Self-contained HTML report with embedded styles and SVG charts.

# ENTITY: EpochTelemetry
MUST HAVE:
- epoch: Integer
- phase: Enum (PHASE_1_META_EXPLORATION, PHASE_2_STRUCTURAL_EXECUTION)
- active_l0_count: Integer
- active_l1_count: Integer
- total_active: Integer
- current_efficacy: Float
- efficacy_derivative: Float
- compute_budget: ComputeBudget
- candidate_axiom: Axiom
- tri_fold_metrics: TriFoldMetrics
- tournament_leaderboard: List of CandidateScore
- decision: String
- timestamp: ISO8601 String

RULES:
- R1: Telemetry must be recorded to JSON (`epoch_XXX.json`) and Markdown (`epoch_XXX.md`).
- R2: Dashboard (`dashboard.html`) must be regenerated after every committed epoch.

# LISTENS TO: EpochCompleted (from EpochEvolution flow)
- Writes JSON file to `generations/gen_XX/epochs/data/epoch_{epoch:03d}.json`.
- Writes Markdown summary to `generations/gen_XX/epochs/epoch_{epoch:03d}.md`.
- Compiles updated `dashboard.html` in generation root and conversation artifact directories.
