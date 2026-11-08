# Generation 5 Idea Prompting Protocol (`g5_succession_prompter.md`)

> **Scope:** Workspace Behavioral Invariant for Audits & Self-Evolution  
> **Target:** Generation 4b (`generations/gen_04b/`) $\to$ Generation 5 (`next_gen/`)  
> **Status:** Active Human Invariant Directive  

---

## 1. Core Operating Directive

When inspecting, auditing, refactoring, or researching Generation 4b components (`generations/gen_04b/`):

1. **Active G5 Radar:**
   - Continuously evaluate whether an identified limitation, structural friction, Landauer dissipation bottleneck, or desired capability belongs in Generation 5 ($G_5$).
   - Specific triggers:
     - Single-machine subnet limitations (`192.168.40.0/24`) requiring true distributed P2P WireGuard mesh.
     - Cooperative agent collusion requiring container air-gaps and asymmetric token bounties.
     - Synchronous IPC bottlenecks requiring a decentralized Pub/Sub event bus (`mesh.events.*`).
     - In-memory mock testing requiring hardware/kernel-level eBPF probes.
     - Capabilities that cannot be cleanly supported in G4b without accumulating structural debt.

2. **Prohibition of Silent Automation:**
   - **Do NOT silently omit or ignore** the insight.
   - **Do NOT silently write or modify** documents in `generations/gen_04b/next_gen/` without human consent.

3. **Mandatory Human Consultation Prompt:**
   - Whenever a G5 candidate is identified during an audit:
     1. Surface the observation directly to the human architect.
     2. Provide a 1–2 sentence rationale for why it exceeds G4b's ceiling and belongs in G5.
     3. Identify the specific target document in `generations/gen_04b/next_gen/` (e.g. `general/candidate_services.md`, `services/audit.md`, `general/hostile_asymmetric_mesh.md`).
     4. Prompt the user: *"Would you like me to add this to the `next_gen/` documentation?"*

---

## 2. Mandatory `G5SuccessionNote` Schema in Project Proposals

When formulating `project_proposals.md` under Directive 3, every proposed option that cuts features for future generations, identifies Landauer thermal ceilings, or highlights architectural limitations of Gen 4b **must embed a machine-verifiable `G5SuccessionNote` JSON block** inside the option description:

````markdown
```json:g5_succession_note
{
  "note_id": "g5-<service_or_topic>-<kebab_slug>",
  "source_proposal_option": "Option 1: <Option Title>",
  "scope_type": "service | general",
  "target_relative_path": "services/<service>.md | general/<slug>.md",
  "target_service": "research | builder | audit | telemetry | governance | general",
  "title": "<Concise Engineering Title>",
  "friction_summary": [
    "<Friction 1: observed bottleneck or thermal overrun in Gen 4b>",
    "<Friction 2: architectural limit requiring generational succession>"
  ],
  "desired_capabilities": [
    "<Capability 1: structural or protocol specification for Gen 5>",
    "<Capability 2: cross-service interaction or mesh topology requirement>"
  ],
  "proposed_invariants": [
    "[L1-G5-###] <Formal category-theoretic or algebraic invariant>",
    "[NEG-G5-###] <Explicit negative constraint>"
  ],
  "research_spikes": [
    "<Spike 1: open technical unknown or prototype to benchmark>"
  ]
}
```
````

### Validation Invariants
- `note_id`: Deterministic kebab-case slug (`^[a-zA-Z0-9_-]+$`).
- `target_relative_path`: Path inside `generations/gen_04b/next_gen/` (path traversal `..` is strictly forbidden).
- `scope_type`: Either `"service"` (mapping to `services/<svc>.md`) or `"general"` (mapping to `general/<slug>.md`).
- Schema completeness: Validated via `python3 scripts/sync_next_gen_notes.py --proposals-file <path> --check`.

---

## 3. Post-Selection Synchronization Step

Once the human architect reviews `project_proposals.md` and selects an option via `ask_question`:

1. **Execute CLI Synchronization:**
   Run the dedicated synchronization utility targeting the chosen proposal option:
   ```bash
   python3 scripts/sync_next_gen_notes.py --proposals-file <path_to_project_proposals.md> --option <option_name_or_index> --yes
   ```

2. **Idempotent Comment Guards:**
   The sync tool wraps all injected content in `<!-- BEGIN G5_SYNC: <note_id> -->` and `<!-- END G5_SYNC: <note_id> -->`. Re-running with the same `note_id` updates the content in-place without duplication.

3. **Reversible Undo Guarantee:**
   Every sync operation saves an exact pre-sync snapshot in `.scratch/next_gen_undo_snapshots/`. If an option selection is reversed, execute:
   ```bash
   python3 scripts/sync_next_gen_notes.py --undo
   ```
