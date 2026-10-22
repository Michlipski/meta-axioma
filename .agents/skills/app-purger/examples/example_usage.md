# App Purger Usage Examples

This guide provides concrete command invocations and expected workflows for purging an application from the Meta-Axioma repository.

---

## 1. Dry-Run Discovery (Default Safe Mode)

Always start with a dry run to inspect every trace that matches the target application without altering any files on disk:

```bash
python3 .agents/skills/app-purger/scripts/purge_app.py axioma_atelier
```

### Sample Output:
```text
===========================================================
 Trace Discovery Report for App: axioma_atelier (short: atelier)
===========================================================
Repository Root: /Users/michaellipski/dev/meta-axioma

📁 Target Directories & Files (4 items):
  - [DIR] generations/gen_02b/apps/axioma_atelier
  - [FILE] generations/gen_02b/src/g2b_compiler/atelier_spec.py
  - [FILE] generations/gen_02b/src/g2b_compiler/emission/atelier_emitter.py
  - [FILE] generations/gen_02b/tests/test_compile_atelier.py

🔗 Root apps/ Symlinks (0 items):
  (None found)

⚡ Compiled Bytecode Caches (3 items):
  - [PYC] generations/gen_02b/src/g2b_compiler/__pycache__/atelier_spec.cpython-314.pyc
  - [PYC] generations/gen_02b/src/g2b_compiler/emission/__pycache__/atelier_emitter.cpython-314.pyc
  - [PYC] generations/gen_02b/tests/__pycache__/test_compile_atelier.cpython-314.pyc

📊 Telemetry Event Logs (3 files):
  - trace/telemetry/orchestration_decisions.jsonl: 1386 matching event line(s)
  - trace/telemetry/project_proposals.jsonl: 84 matching event line(s)
  - trace/telemetry/recursion_depth_opinions.jsonl: 82 matching event line(s)

📖 Documentation & Catalogs (1 files):
  - SYSTEMS_PORTFOLIO.md: 4 matching reference(s)
      Line 180: ### System 12: Axioma Atelier (Category Theory in the Kitchen & Studio)...

Total traces discovered: 1563
===========================================================

💡 This was a DRY-RUN. No files were deleted or modified.
👉 To execute the purge, run:
   python3 .agents/skills/app-purger/scripts/purge_app.py axioma_atelier --execute
```

---

## 2. Interactive Execution (Prompt for Confirmation)

When you are ready to purge, specify `--execute`. The script will display the audit report and prompt for confirmation before proceeding:

```bash
python3 .agents/skills/app-purger/scripts/purge_app.py axioma_atelier --execute
```

```text
⚠️ Are you sure you want to permanently delete all traces of 'axioma_atelier'? (yes/no): yes

✅ Purge Completed Successfully:
  - Deleted files & directories: 4
  - Deleted symlinks: 0
  - Deleted bytecode cache (.pyc): 3
  - Scrubbed telemetry lines: 1552
  - Scrubbed heuristic overrides: 0
  - Cleaned documentation files: 1
```

---

## 3. Automated / Non-Interactive Purge with Git Verification

For automated workflows, pass `--execute --force --verify-git`:

```bash
python3 .agents/skills/app-purger/scripts/purge_app.py axioma_atelier --execute --force --verify-git
```

---

## 4. Preserving Historical Telemetry

If you wish to delete the application files, tests, and documentation but preserve the thermodynamic compute logs in `trace/telemetry/*.jsonl` for historical metrics:

```bash
python3 .agents/skills/app-purger/scripts/purge_app.py axioma_atelier --execute --force --keep-telemetry
```

---

## 5. Structured JSON Output

To integrate the discovery results into other tools or subagents:

```bash
python3 .agents/skills/app-purger/scripts/purge_app.py axioma_atelier --json
```
