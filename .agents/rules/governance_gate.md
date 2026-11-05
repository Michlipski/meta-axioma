---
trigger: model_decision
description: "Mandatory pre-execution governance gate: prohibits direct code modifications to generation or application files without prior written proposals (project_proposals.md) and explicit human approval."
---

# ⛔ Mandatory Pre-Execution Governance Gate (`[NEG-GOV-GATE-001]`)

## 1. The Core Invariant
Autonomous agents are **STRICTLY PROHIBITED** from using `edit_file`, `write_file`, or terminal mutation commands on ANY application or generation source code (`src/`, `services/`, `apps/`, `epochs/`) upon receiving a prompt.

No changes to the generation code are permitted without first completing the mandatory planning, proposal, and human verification process.

## 2. Mandatory Pre-Modification Workflow

Before ANY file in `src/`, `services/`, `apps/`, or `protocols/` can be created or modified:

1. **Role Identification & Boundary Enforcement:**
   - If operating as the **Sovereign Research Service (`services/research/`, 192.168.40.10)**, invariant `[L1-G4B-002]` applies: **Zero-Code Boundary**. The Researcher authors specifications, Waterloo SoC models, hypotheses, and protocol schemas, but is **physically barred from writing application code**.
2. **Waterloo Situation of Concern Normalization (`[L1-G3B-000]`):**
   - Deconstruct the problem space into Macro, Meso, and Micro concerns (actors, frictions, constraints, unmet needs).
3. **Mandatory Physical Emission of `project_proposals.md` (Directive 3):**
   - Formulate candidate architectural options calibrated via `DynamicBudgetCalibrator` with thermodynamic 60/40 capital budgets.
   - Physically emit `project_proposals.md` via `write_file` into the artifact directory `<appDataDir>/brain/<conversation-id>/project_proposals.md`.
4. **Mandatory Human Verification Gate (`ask_question`):**
   - Present the proposal link `[project_proposals.md](file:///...)` to the human architect.
   - Elicit explicit approval or steering via `ask_question`.
5. **Post-Approval Execution:**
   - Only AFTER the human architect has selected an option and granted explicit approval may code leaves be synthesized by the Builder enclave (`services/builder/`).

## 3. Physical Runtime Interception
This invariant is physically enforced at runtime by `.agents/hooks.json` via `scripts/governance_pre_tool_guard.py`. Any attempt to call `edit_file` or `write_file` on protected code directories without an existing `project_proposals.md` in the artifact directory is intercepted and hard-denied with an exit error before the file is touched.

## 4. Designated In-Workspace Scratch Directory (`.scratch/`)
When generating intermediate raw JSON buffers, temporary build scripts, or stream chunks, agents must write strictly to the git-ignored `.scratch/` directory at the project root (e.g. `.scratch/compile_bundle.py`) or the conversation's scratch directory `<appDataDir>/brain/<conversation-id>/scratch/`.
Writing to `/tmp` or `/private/tmp` is prohibited to prevent macOS symlink permission dialogs and `HERM-003` ambient path violations. `.scratch/` is 100% sandboxed, git-ignored, and automatically allowed by the governance guard.
