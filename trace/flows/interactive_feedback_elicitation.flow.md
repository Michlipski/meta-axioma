---
flow: InteractiveFeedbackElicitationFlow
persona: MetaOrchestrator
domains:
  - AppSpecification
  - GenerationalFeedback
  - EvaluationTargets
---

# WORKFLOW: Interactive Feedback Elicitation & Grounding Loop

> GOAL: Ensure that systems know to actively ask for human feedback before, during, and after application compilation, preventing the Verification Illusion and enabling continuous cross-generational learning.

---

## STEP 1: Pre-Compilation Intent Elicitation (Phase 0 Gate)
- When a new application idea or reference product is proposed:
  - The orchestrator pauses autonomous compilation.
  - Generates a targeted human interview covering:
    1. **Trigger & Context:** When and where does the user open this tool? (Desktop, mobile on couch, commute, etc.)
    2. **Job-to-be-Done (JTBD):** What specific functional or emotional transformation is desired?
    3. **Existing Friction:** What makes existing alternatives (or paper notes / spreadsheets) painful?
    4. **Domain Nuances:** What specific data types, languages, or workflows are involved?
  - Logs the dialogue into `trace/intent_elicitation.md` as an official `HumanIntentWitness`.

## STEP 2: Co-Designed High-Level Plan & Human Approval Gate
- Translates the elicited dialogue into a comprehensive high-level plan (persona, JTBD, workflow, architecture, UX ergonomics).
- Presents the plan to the human architect for review and feedback.
- **Low-level code execution is strictly optional.**
- The orchestrator MUST explicitly ask: *"Would you like to execute on this plan and compile the application code, or iterate on the plan first?"*
- Any code synthesis or file creation is physically blocked until explicit approval is granted.

## STEP 3: Optional Compilation with Embedded Feedback Affordances
- If and only if the human architect grants explicit approval:
  - The compiler synthesizes the application code with mandatory feedback affordances:
    - **Backend:** `POST /api/feedback` handler persisting to `data/user_feedback.json`.
    - **Frontend:** Standardized `💬 Feedback / Report Friction` UI modal allowing instant 1-tap rating and text submission.

## STEP 4: Post-Deployment Active Feedback Query
- Immediately after launching or delivering the interactive application preview:
  - The orchestrator actively queries the human architect:
    - *"How does the initial layout feel compared to your mental model?"*
    - *"Where do you feel cognitive friction or unexpected friction?"*
    - *"What edge cases or daily habits did we miss?"*

## STEP 5: Generational Feedback Ledger Compilation
- User responses (from both orchestrator queries and in-app `/api/feedback` events) are reviewed.
- If a misalignment or architectural failure is identified:
  - Formulates an atomic `GenerationalLesson` (`LES-G{N}-{###}`).
  - Appends to `generations/gen_{N}/FEEDBACK.md` and `feedback/feedback.json`.
  - If severity is High or Critical, synthesizes an inherited constraint (`NEG-G{N+1}-{###}`) for the successor generation compiler.
