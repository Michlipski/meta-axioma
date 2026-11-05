# Generation 5 Governance & Safety Service Dossier (`services/governance.md`)

> **Enclave Target:** `services/governance/` (192.168.40.50)  
> **Target Successor:** Generation 5 Sovereign Governance Enclave  
> **Source Directive:** [NEG-GOV-GATE-001] Pre-Execution Governance Gate, [L1-G2B-004..005] Dynamic Budget Calibration  
> **Status:** Active Evolution Notes & Desiderata  

---

## 1. Context & Generation 4b Baseline

In Generation 4b, the **Governance & Safety Service** (`services/governance/`) maintains the supreme constitutional authority of Meta-Axioma:
- **Mandatory Pre-Execution Governance Gate (`[NEG-GOV-GATE-001]`):** Strictly prohibits direct modification of generation or application source code without prior written proposals (`project_proposals.md`) and explicit human approval via `ask_question`.
- **Physical Pre-Tool Guard (`scripts/governance_pre_tool_guard.py`):** System-level hook intercepting tool calls before file mutation.
- **Dynamic Budget Calibrator (`DynamicBudgetCalibrator`):** Calculates unified BPE token allowances, enforcing the thermodynamic capital split (60% Exploratory, 40% Protected).
- **Succession Gatekeeper (`succession_gatekeeper.py`):** Enforces formal Z3 proofs, HDR $\le 0.15$ ceilings, and zero-loopback invariants before certifying generational handover.

---

## 2. Generation 4b Friction Points & Limitations

1. **Synchronous Single-Veto Gate:** Governance currently halts tool execution synchronously while waiting for a single human user. It lacks support for multi-party architectural quorums or async approval queues.
2. **Static Heuristic Budgeting:** While `DynamicBudgetCalibrator` dynamically sizes options based on structural graph counts, it cannot adapt dynamically mid-run if an application experiences unexpected algorithmic breakthroughs or dead-ends.
3. **Manual Invariant Addition:** Introducing a new negative constraint (`NEG-###`) requires manually editing markdown files rather than executing a signed governance transaction through a CLI or API.
4. **Local Process Interception:** The pre-tool guard runs as a local Python script attached to `.agents/hooks.json`. In a distributed multi-node mesh, governance must run as an authenticated policy proxy (e.g. OPA/Rego or eBPF filter).

---

## 3. Generation 5 Desired Capabilities & Aspirations

### 3.1 Distributed Cryptographic Quorum Voting
- Supports multi-human and multi-agent governance quorums:
  - Critical generational changes require $M$-of-$N$ cryptographic signatures (e.g., Human Architect + Principal Auditor + Telemetry Health Witness).
  - Routine low-risk tasks (e.g., updating docs or running lint checks) can be auto-approved based on formal policy rules.

### 3.2 Dynamic Token Elasticity & Landauer Throttling
- Integrates live token decay with compute throttling. If an agent enters a circular unproductive reasoning loop, governance automatically intervenes, dials down exploratory temperature, or forces an early Socratic Red Team review.

### 3.3 Zero-Trust Policy Proxy (eBPF / Network Boundary)
- Transitions from file-hook guards to network-layer enforcement. In Gen 5's distributed mesh, any attempt by an untrusted node to emit packets to protected ports or write to protected volumes without a valid authorization token is dropped at the kernel layer.

### 3.4 Automated Heuristic Debt Enforcement
- Continuously calculates the live Heuristic Debt Ratio (HDR). If HDR rises above $0.15$, the Governance Service immediately places the repository into **Read-Only / Refactor Mode**, rejecting all new feature requests until structural cleanup is completed.

---

## 4. Proposed Invariants for Gen 5 Governance

- **`[L1-G5-GOV-001]` The Inviolable Human Veto:** Total preservation of human negative invariants (`NEG-###`). No autonomous compiler, optimizer, or agent quorum may override an explicit human veto.
- **`[L1-G5-GOV-002]` Immutable Governance Audit Trail:** All approval, veto, and budget allocation events must be appended to the append-only governance hash chain.
- **`[L1-G5-GOV-003]` Hard Heuristic Debt Ceiling:** Absolute zero tolerance for HDR $> 0.15$ at any generational handover boundary.

---

## 5. Open Research Spikes & Inquiries

1. *Lightweight In-Process Policy Engines:* Can we embed an ultra-fast OPA (Open Policy Agent) WebAssembly evaluator into the governance enclave to evaluate policy rules in $< 1\text{ms}$?
2. *Asynchronous Approval Queues:* How can the governance gate queue and batch non-blocking tool calls while waiting for human architectural reviews without stalling independent background processes?
