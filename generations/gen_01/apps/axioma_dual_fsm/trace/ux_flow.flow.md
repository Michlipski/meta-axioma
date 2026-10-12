---
flow: DualFsmSecurityAndWorkflow
persona: SecurityEngineer
domains:
  - AxiomaDualFsm
  - AppSpecification
  - GenerationalFeedback
---

# WORKFLOW: Dual-FSM Zero-Trust Governance & Audit Loop

> GOAL: Provide AI security architects with provable, deterministic state inspection, interactive attack simulation, tool failure recovery, and audited functorial rollbacks.

---

## FLOW 1: Benign Multi-Turn Execution (Happy Path)
1. User provides prompt: "Query quarterly sales database for region EMEA."
2. `Outer FSM` transitions `SECURE_STANDBY` -> `ACTIVE_MONITORING`. Rate & entropy verified.
3. `Inner FSM` transitions `IDLE` -> `INTENT_IDENTIFIED` ("database_query").
4. Parameters elicited -> `PARAM_ELICITATION` (region: "EMEA").
5. Agent proposes SQL query plan -> `PLAN_PROPOSED`.
6. Tool requires permission -> `AWAITING_APPROVAL`.
7. User grants approval token -> `ACTION_DISPATCHED`.
8. Tool executes successfully -> `OUTCOME_EVALUATED` (status: 200 OK).
9. Output synthesized -> `RESPONSE_SYNTHESIZED` -> `TERMINAL_SUCCESS`.
10. `Outer FSM` returns to `SECURE_STANDBY`.

---

## FLOW 2: Tool Runtime Failure & Recovery Loop
1. Agent dispatches action (`ACTION_DISPATCHED`) to a remote microservice.
2. Remote API returns 504 Gateway Timeout.
3. `Inner FSM` steps to `OUTCOME_EVALUATED` with failure payload.
4. Instead of crashing dialogue or hallucinating response, FSM deterministically routes to:
   - **Path A (Fallback Tool):** Routes back to `PLAN_PROPOSED` to select secondary replica database.
   - **Path B (Parameter Correction):** If 400 Bad Request, routes back to `PARAM_ELICITATION` to re-query user for valid schema.

---

## FLOW 3: Dynamic De-Escalation Loop (ELEVATED_SCRUTINY -> ACTIVE_MONITORING)
1. LLM emits a long token string (e.g., base64 hash or UUID).
2. `Outer FSM` detects entropy spike -> escalates from `ACTIVE_MONITORING` -> `ELEVATED_SCRUTINY`.
3. Token boundary scanner verifies the payload matches approved UUID format (non-sensitive).
4. `Outer FSM` emits de-escalation event -> resets to `ACTIVE_MONITORING`. Dialogue continues without interruption.

---

## FLOW 4: Malicious Injection & Coupled Halting Morphism (Φ_halt)
1. User or model injection attempts prompt jailbreak or data exfiltration.
2. `Outer FSM` detects forbidden regex / exfiltration pattern.
3. `Outer FSM` transitions to `ATOMIC_HALT`.
4. Coupled Halting Morphism fires in zero clock cycles:
   - `Inner FSM` is instantly frozen in `HALTED`.
   - Egress token buffer is wiped to 0 bits (Landauer audit logged).
   - Cryptographic `AuditWitness` generated inside Demarcated Exception Enclave (L1-016).
   - Zero compromised tokens emitted to client.

---

## FLOW 5: Functorial Rollback Morphism (L1-002 Revert Edge)
1. Security operator inspects `AuditWitness` in console.
2. Operator uses time-travel scrubber to diagnose trigger token.
3. Operator clicks **"Authorize Revert State"**.
4. System executes `REVERT_STATE` morphism:
   - Steps `Outer FSM` back to `SECURE_STANDBY`.
   - Scrubs `Inner FSM` back to safe checkpoint (`IDLE`).
   - Appends signed rollback record to `data/audit_log.json`.
