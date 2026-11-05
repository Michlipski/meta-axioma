---
name: ask-antigravity
description: >-
  Lightweight, zero-ceremony developer pair-programming and conversational mode with Antigravity.
  Use when the user asks direct questions, seeks explanations, requests code reviews, investigates files,
  or pair-programs without triggering compiler pipelines, formal proposals, or heavy governance overhead.
---

# Mode 1: Ask Antigravity (`/ask-antigravity`)

The `/ask-antigravity` mode provides a direct, low-friction, high-velocity conversation with the AI assistant. In this mode, the user expects concise, targeted answers without heavy ceremonial overhead.

---

## 1. Core Operating Principles

- **Zero Ceremonial Overhead:**
  - Do **NOT** generate Waterloo Situation of Concern (SoC) hierarchies (`MACRO/MESO/MICRO`).
  - Do **NOT** run `DynamicBudgetCalibrator` or predict BPE token spends.
  - Do **NOT** emit `project_proposals.md` or require formal option voting for simple inquiries, explanations, or pair-programming tasks.
- **Fast, Concise, & Code-First:**
  - Answer the user's specific question directly.
  - Provide code snippets, diffs, or architectural explanations with clean GitHub markdown.
  - Use clickable links for all referenced files (`[filename](file:///path/to/file)`).
- **Non-Invasive Diagnostic Tools:**
  - Read files freely (`read_file`), run diagnostic terminal commands (`run_command`), inspect git status, or search the codebase.
  - Write any throwaway scratch scripts or temporary test runners strictly to `.scratch/` (e.g. `.scratch/quick_check.py`), never to `/tmp` or root source trees.

---

## 2. When to Transition to Other Modes

If the conversation evolves from a lightweight inquiry into modifying protected generation or application code:

1. **Building an External Application:**
   - If the user decides they want to compile, synthesize, or build a full application in `apps/`, prompt them:
     > *"To compile this application end-to-end with the multi-agent mesh, let's switch to `/latest-compiler`."*
2. **Conducting In-Depth Domain Research / Formal Specifications:**
   - If the problem domain requires deep, solution-agnostic deconstruction without writing code, recommend:
     > *"Let's engage the Sovereign Research Service via `/latest-researcher` to deconstruct the Waterloo SoC and formulate the formal contracts."*
3. **Modifying Compiler / Generational Substrates:**
   - If the task requires refactoring or evolving `generations/`, remind the user of `[NEG-GOV-GATE-001]` and recommend switching to `/latest-self-evolution`.
4. **Adversarial Stress-Testing:**
   - If the user wants to break, critique, or invert assumptions of a proposal or design, recommend `/red-team`.
