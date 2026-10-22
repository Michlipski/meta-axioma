# Application Trace Inventory in Meta-Axioma

When an application is synthesized, compiled, or tested in Meta-Axioma, it establishes footprints across several distinct architectural layers. To completely remove an application without leaving orphan symlinks, broken imports, phantom documentation entries, or corrupted telemetry streams, the `app-purger` skill audits all 8 layers detailed below.

---

## 1. Physical Application Directories & Symlinks
- **Canonical Top-Level Symlinks:**
  - `apps/<app_id>` (e.g. `apps/axioma_atelier` $\to$ `../generations/gen_02b/apps/axioma_atelier`)
- **Generation-Specific Substrates:**
  - `generations/gen_{XX}/apps/<app_id>/`
  - Contains `run.py`, `server.py`, `app.json`, `static/`, `schema/`, `data/`, `tests/`, `recursion_tree.md`, `telemetry_dashboard.html`, and `project_proposals.md`.

---

## 2. Compiler Specifications & Emitter Modules
Depending on which compiler synthesized the app (`System G1`, `System G1b`, `System G2`, `System G2b`, `System G3`), dedicated specification builders or emitters may have been generated:
- `generations/gen_{XX}/src/g{XX}_compiler/{shortname}_spec.py`
  - Defines the Semantic IR, Statechart IR, and Contract IR.
- `generations/gen_{XX}/src/g{XX}_compiler/emission/{shortname}_emitter.py`
  - Application-specific template or code generation logic.

---

## 3. Test Suites & Verification Harnesses
Verification fixtures and end-to-end integration tests:
- `generations/gen_{XX}/tests/test_compile_{shortname}.py`
- `generations/gen_{XX}/tests/test_{shortname}*.py`
- Root test bindings in `tests/test_{shortname}*.py` or within `tests/test_all.py`.

---

## 4. TRACE Declarative Specifications & Elicitation Files
- **Intent Elicitation Artifacts:**
  - `trace/intent_elicitation_{app_id}.json`
  - Captures Phase 0 human intent interview, JTBD, user stories, and acceptance constraints.
- **Domain & Flow Declarations:**
  - `trace/domains/{app_id}*.domain.md`
  - `trace/flows/{app_id}*.flow.md`

---

## 5. Thermodynamic Telemetry & Decision Streams
Meta-Axioma records event telemetry for all compilation and synthesis runs in newline-delimited JSON (`.jsonl`):
- `trace/telemetry/project_proposals.jsonl`: Logs dynamic token proposals ($C_{\min} \dots C_{\max}$) and selected proposal tiers for `{app_id}`.
- `trace/telemetry/orchestration_decisions.jsonl`: Logs recursive sub-agent worker routing decisions under `{shortname}_compile_run`.
- `trace/telemetry/recursion_depth_opinions.jsonl`: Logs worker depth suggestions and confidence ratings under `{shortname}_compile_run`.

---

## 6. Stateful Human Override & Heuristic Governance
- `trace/overrides/heuristic_overrides.json`
  - Under `[L1-G2B-002]`, human usability exemptions or heuristic overrides granted to an application are registered here.

---

## 7. Registry Documentation & Portfolios
- `apps/README.md`: The canonical markdown table listing active deployed applications, port assignments, and embodied axioms.
- `SYSTEMS_PORTFOLIO.md`: The detailed non-generator systems portfolio ledger containing application descriptions, test metrics, and architectural retrospective sections.

---

## 8. Python Bytecode Caches
- `__pycache__/*{shortname}*.pyc`
  - Cached compiled bytecode files in compiler, test, or app folders that can cause phantom imports if left behind.
