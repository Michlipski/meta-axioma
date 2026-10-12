# Axioma Dual FSM

> **Zero-Trust AI Runtime Governance Kernel & Deterministic Gateway**  
> Compiled autonomously by **System $G_1$** (Meta-Axioma Recursive Compiler) to realize the High-Level Jettison.

---

## 1. Product Overview

**Axioma Dual FSM** is an embeddable, zero-dependency runtime governance middleware designed to enforce absolute, mathematically verifiable state determinism over autonomous AI agents and conversational LLMs.

Rather than relying on fuzzy, non-deterministic secondary LLMs ("guardrail LLMs") or loose procedural `if/else` checks, Axioma Dual FSM gates execution through two independent, concurrent finite state machines governed by a formal **Coupled Halting Morphism ($\Phi_{\text{halt}}$)**:
- **Inner FSM:** Models dialogue intent, task planning, and tool execution progression.
- **Outer FSM:** Strictly enforces token rate boundaries, Shannon entropy limits, and data exfiltration invariants.
- **The Dominance Rule:** If the Outer FSM detects an anomaly, it dominates and freezes the Inner FSM in zero clock cycles, preventing any unapproved tokens or tool calls from reaching external execution runtimes.

---

## 2. The Three Architectural Refinements

### 🔄 Refinement 1: Non-Deterministic Tool Failure Recovery Loop
In standard architectures, tools either succeed or crash the session. In Axioma Dual FSM:
- After `ACTION_DISPATCHED`, the state transitions to `OUTCOME_EVALUATED`.
- If the tool call succeeds, it advances to `RESPONSE_SYNTHESIZED`.
- If a transient runtime error occurs (e.g., 504 Gateway Timeout), it deterministically loops back to `PLAN_PROPOSED` to select a fallback tool.
- If a 400 Bad Request / parameter error occurs, it loops back to `PARAM_ELICITATION` to solicit corrected parameters from the user.

### 📉 Refinement 2: Dynamic De-Escalation (Rebound vs. Ratchet)
Escalation is not an irreversible ratchet:
- `ELEVATED_SCRUTINY ⇄ ACTIVE_MONITORING`: When a high-entropy token is detected (e.g., a benign UUID or base64 asset identifier), the payload format scanner clears the anomaly and de-escalates the Outer FSM back to `ACTIVE_MONITORING`.
- `CONTAINED_QUARANTINE` and `ATOMIC_HALT` remain one-way trapdoors that require human intervention.

### ↩️ Refinement 3: Functorial Reversibility (`L1-002`) & The Revert Edge
When an `ATOMIC_HALT` is triggered:
- The session is safely bounded within a Demarcated Exception Enclave (`L1-016`).
- A human security operator can inspect the cryptographic `AuditWitness` and time-travel scrub to the trigger point.
- The operator triggers a deterministic `REVERT_STATE` morphism: steps the Outer FSM back to `SECURE_STANDBY`, resets the Inner FSM to `IDLE`, and records a signed `Rollback Witness` in `data/audit_log.json`.

---

## 3. Invariant Architecture Mapping

| Axiom ID | Name | Role in Axioma Dual FSM |
| :--- | :--- | :--- |
| **`L1-015`** | Zero-Trust MCP Gateway | Dual-boundary typed Nouns and deterministic Verb state transition tables. |
| **`L1-016`** | Demarcated Exception Enclaves | Traps halts, binds blast radius, and emits machine-readable cryptographic witnesses. |
| **`L1-002`** | Functorial State Evolution | Reversible morphisms (`REVERT_STATE`) for post-breach rollback and time travel. |
| **`L1-004`** | Universal Grammar Schemas | Deep AST syntactic validation for all conversational intent payloads. |
| **`L1-008`** | Landauer Thermodynamic Accounting | Live bit-erasure calculation ($k_B T \ln 2$) when buffers are wiped on quarantine. |
| **`L1-011_3`** | Decoupled Persistence (Boundary 3) | Pure in-memory state engine decoupled from persistent audit ledgers. |
| **`L1-015_1`** | Compositional Boundary Isolation | Dialogue parser and security scanner compose orthogonally with zero side effects. |

---

## 4. How to Run

Launch the standalone zero-dependency Python 3.14 server (default port `8092`):

```bash
# From repository root:
python3 generations/gen_01/apps/axioma_dual_fsm/run.py
```

Then open your browser at **`http://localhost:8092`**.

---

## 5. Automated Verification

Run the automated test suite verifying state determinism, tool failure recovery loops, de-escalation paths, and coupled halting morphisms:

```bash
python3 -m unittest -v generations/gen_01/apps/axioma_dual_fsm/tests/test_app.py
```
