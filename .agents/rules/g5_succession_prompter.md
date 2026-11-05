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
