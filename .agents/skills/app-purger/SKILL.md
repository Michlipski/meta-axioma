---
name: app-purger
description: >-
  Completely removes an application and all its traces from the Meta-Axioma repository,
  including canonical apps/, generational apps/, compiler specs, emitters, test suites,
  TRACE domain/flow files, intent elicitation JSONs, telemetry logs, and catalog documentation.
  Use this skill whenever the user asks to delete, purge, wipe, clean up, or remove an application
  and any trace of it from the codebase.
---

# App Purger Skill

This skill provides a systematic and zero-residue procedure to search, audit, and permanently delete an application and all associated traces from the Meta-Axioma repository.

When applications are synthesized or tested across generations ($G_1, G_{1b}, G_2, G_{2b}, G_3$), they create artifacts across 8 distinct layers. The `app-purger` skill ensures that deleting an app removes every artifact cleanly without leaving orphan symlinks, phantom documentation, broken test imports, or stale bytecode.

---

## Architecture of Application Traces

An application's traces span across:
1. **Root & Generational Applications:** `apps/<app_id>` (symlinks or directories) and `generations/gen_{XX}/apps/<app_id>/`.
2. **Compiler Specifications & Emitters:** `generations/gen_{XX}/src/g{XX}_compiler/{shortname}_spec.py` and `atelier_emitter.py`.
3. **Test Suites & Verification Fixtures:** `generations/gen_{XX}/tests/test_compile_{shortname}.py` and `tests/test_{shortname}*.py`.
4. **TRACE Declarative Models:** `trace/intent_elicitation_{app_id}.json`, `trace/domains/{app_id}*.domain.md`, `trace/flows/{app_id}*.flow.md`.
5. **Thermodynamic Telemetry:** Event lines in `trace/telemetry/project_proposals.jsonl`, `orchestration_decisions.jsonl`, and `recursion_depth_opinions.jsonl`.
6. **Stateful Overrides:** Exemption records in `trace/overrides/heuristic_overrides.json`.
7. **Documentation & Registries:** Catalog entries in `apps/README.md` and `SYSTEMS_PORTFOLIO.md`.
8. **Bytecode Caches:** Associated `.pyc` files in `__pycache__/`.

For full layer descriptions, consult [`references/trace_inventory.md`](./references/trace_inventory.md).

---

## Operational Workflow

### Step 1: Dry-Run Discovery & Trace Audit (Mandatory First Step)
Always run a dry-run discovery first to locate and display all traces without modifying any files:

```bash
python3 .agents/skills/app-purger/scripts/purge_app.py <app_id_or_shortname>
```

*Example:*
```bash
python3 .agents/skills/app-purger/scripts/purge_app.py axioma_atelier
```

Review the output report:
- Verify the list of target directories and files.
- Verify symlinks and bytecode caches.
- Check the count of telemetry lines and documentation references found.

### Step 2: Human Confirmation Gate
In accordance with Directive 1 (Human-in-the-Loop Intercepts), present the discovery findings to the human architect before executing destructive actions. If calling as an autonomous agent in chat, use `ask_question` or prompt for confirmation if ambiguous.

### Step 3: Execute Atomic Purge
Run the helper script with `--execute` (and optionally `--verify-git`):

```bash
# Interactive mode (prompts for confirmation)
python3 .agents/skills/app-purger/scripts/purge_app.py <app_id> --execute

# Non-interactive / script-driven mode
python3 .agents/skills/app-purger/scripts/purge_app.py <app_id> --execute --force --verify-git
```

#### Preserving Telemetry (Optional)
If the human architect requests keeping historical telemetry records for compute analysis, add `--keep-telemetry`:
```bash
python3 .agents/skills/app-purger/scripts/purge_app.py <app_id> --execute --force --keep-telemetry
```

### Step 4: Verification & Sanity Checks
After execution, verify the health of the repository:
1. **Check Git Status:** Confirm only the intended files were removed or modified:
   ```bash
   git status --short
   ```
2. **Run Unit Tests:** Ensure no dangling imports or missing module errors exist in the test suites:
   ```bash
   python3 -m unittest discover -s generations/gen_02b/tests
   ```

---

## Safety Safeguards & Protected Paths

The purge script enforces strict protections:
- **Protected Framework Roots:** Never permits deletion of `.`, `apps/`, `generations/`, `src/`, `tests/`, `trace/`, `.agents/`, or top-level project folders.
- **Protected Core Files:** Core compiler files (`engine.py`, `compiler.py`, `models.py`, `test_all.py`, `overview.md`, etc.) are permanently exempt from deletion even if their names contain substrings matching an app alias.
- **Atomic Operations:** Telemetry files and markdown documentation are scrubbed in place with intact syntax preservation.

---

## References & Examples

- **Trace Inventory Reference:** [`references/trace_inventory.md`](./references/trace_inventory.md)
- **Usage Walkthroughs & Commands:** [`examples/example_usage.md`](./examples/example_usage.md)
