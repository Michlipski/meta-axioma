---
name: system-diagnosis
description: >-
  Systemic problem diagnosis and functorial roundtrip closure workflow (/system-diagnosis).
  Elevates localized micro-defects to higher-order architectural invariants,
  derives generalized structural remedies, projects them down to prove remediation,
  and enforces multi-agent context separation to eliminate confirmation bias.
---

# Mode 8: System Diagnosis & Functorial Roundtrip Closure (`/system-diagnosis`)

The `/system-diagnosis` mode executes a disciplined, bi-directional diagnostic protocol for **Meta-Axioma** system defects. It prevents treating symptoms with isolated patches by systematically climbing the abstraction ladder to cure the systemic disease, while enforcing **strict multi-agent context separation** to eliminate single-agent confirmation bias.

---

## 1. When to Use This Skill

Activate `/system-diagnosis` when:
- An implementation shortcut, mock bypass, or structural flaw is discovered in a generated service or application.
- You need to determine what higher-order architectural invariant, compiler pass, or micro-auditor rule failed to prevent the flaw.
- You want to design a generalized systemic remedy and mathematically prove that it cures the original defect without relying on the author's self-justification.

---

## 2. The 5-Step Functorial Roundtrip Protocol

$$\begin{CD}
\text{Defect}_{\text{micro}} @>{\text{Elevation } (F)}>> \text{InvariantDeficit}_{\text{macro}} \\
@. @VV{\text{Architectural Remedy } (S)}V \\
\text{Specific Cure}_{\text{micro}} @<<{\text{Projection } (G)}< \text{Systemic Invariant}_{\text{macro}}
\end{CD}$$

### Step 1: Micro-Anomaly Isolation (Physical Grounding)
1. Identify the exact physical file path and line numbers (e.g. `runner.py:360-407`).
2. Document the **observed defect** (e.g. in-memory dictionary state spoofing).
3. Document the **expected operational behavior** (e.g. execution of `app.js` in a headless Node.js probe).
4. Explain why existing test suites or linters produced a false-positive pass.

### Step 2: Waterloo Abstraction Elevation (Upward Morphism $F$)
Deconstruct the root cause through the Waterloo Tier 1 Situation of Concern (`[L1-G3B-000]`):
- **Micro (Symptom):** The specific lines of code or data structures that took the shortcut.
- **Meso (Mechanism):** The compiler pipeline, service interface, or verification pass that failed to catch the shortcut before delivery.
- **Macro (Systemic Incentive):** The foundational axiom or incentive gradient (e.g. LLM simulation gradient, builder/tester collusion, lack of negative feedback loops) that caused the shortcut.

### Step 3: Higher-Order Architectural Remedy Formulation (Morphism $S$)
Design a structural, deterministic remedy at the macro/meso level:
- New machine-readable IR contracts (e.g. `AcceptanceSpecIR`).
- Automated compiler gates (e.g. Physical Mutation Falsification Gate).
- Static AST micro-auditor rules (e.g. `HERM-ANTIMOCK-001`).
- *Strict Rule:* The remedy must be mechanical (enforced by AST linters, subprocess exits, or cryptographic witnesses), **never a prompt suggestion or plea for better agent behavior**.

### Step 4: Downward Concrete Trace Walk (Downward Morphism $G$)
Trace the higher-order remedy back down to the original micro instance:
- **Trace 4.1:** At what exact line of code would the new gate trigger?
- **Trace 4.2:** What exact exception class and diagnostic payload would be emitted?
- **Trace 4.3:** Does the remedy break backward compatibility or cause Landauer budget overruns?

### Step 5: Adversarial Epistemic Firewall (Enforcing Context Separation)
To prevent the single-context "Self-Justification Loop", the diagnosis must pass through the **3-Tier Epistemic Firewall** before any proposal is certified.

---

## 3. How Separation of Context is Physically Enforced

Single LLM contexts inevitably suffer from confirmation bias: an agent that invents a solution will always convince itself that the solution works. To break this loop, `/system-diagnosis` enforces separation across **four physical barriers**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        THE 4 PHYSICAL SEPARATION BARRIERS                              │
├──────────────────────────────────────┬─────────────────────────────────────────────────┤
│  Barrier 1: Process & Memory Sandboxing│  Barrier 2: Context Sanitization (Blind Inversion)│
│  ─────────────────────────────────── │  ────────────────────────────────────────────── │
│  Subagents are spawned via           │  The subagent's prompt receives ONLY the raw    │
│  `invoke_subagent` with clean        │  artifact and an adversarial objective.         │
│  conversation IDs and zero memory    │  Parent rationales, explanations, and defenses  │
│  of parent reasoning.                │  are strictly stripped out.                     │
├──────────────────────────────────────┼─────────────────────────────────────────────────┤
│  Barrier 3: Branch Workspace Isolation │  Barrier 4: The Deterministic Acid Test         │
│  ─────────────────────────────────── │  ────────────────────────────────────────────── │
│  `Workspace="branch"` isolates disk   │  The ultimate judge is NOT an LLM text reply.   │
│  mutations into a cloned worktree.   │  A Python script physically runs against the    │
│  Exploits cannot contaminate main.   │  unmodified buggy code; asserts exit code != 0. │
└──────────────────────────────────────┴─────────────────────────────────────────────────┘
```

### Barrier 1: Independent Subagent Spawning (`invoke_subagent`)
- Never ask the main conversation: *"Does this fix the bug?"*
- Always spawn an independent agent using `invoke_subagent(Role=..., Prompt=..., Workspace="branch")`.
- The subagent has a fresh context window, independent attention heads, and no memory of the parent's thought process.

### Barrier 2: Context Sanitization (The "Blind Adversary" Prompt Shape)
When querying the subagent, **strip all parent justifications and desired outcomes**. Frame the prompt using adversarial incentives:

#### Vector A: The "Lazy Builder Exploit Simulation"
```python
invoke_subagent(
    TypeName="self",
    Role="Adversarial Exploit Engineer",
    Workspace="branch",
    Prompt="""
[TASK: FIND EVASION VECTORS]
You are a resource-constrained, lazy software bot trying to pass the following new audit rule with the absolute minimum effort, without writing real functional implementation code:

<AUDIT_RULE>
{audit_rule_source}
</AUDIT_RULE>

Identify at least 2 concrete ways a bot could fool this rule using synthetic mocks, dead code, or trivial workarounds. Do not justify the rule; your sole objective is to break it.
"""
)
```

#### Vector B: The Popperian Falsification Red Team
```python
invoke_subagent(
    TypeName="self",
    Role="Dialectical Red Team Architect",
    Workspace="branch",
    Prompt="""
[TASK: FALSIFY THE ROUNDTRIP]
A developer claims that Architectural Remedy (S) completely prevents Defect (P):

Defect P: {defect_description}
Remedy S: {remedy_source}

Your objective is Popperian falsification:
1. Construct a concrete edge case where Defect P can still occur under Remedy S.
2. Identify any secondary failure modes (deadlocks, performance regressions, network timeouts) introduced by Remedy S.
Do not be polite; be rigorous.
"""
)
```

### Barrier 3: Branch Workspace Sandboxing (`Workspace="branch"`)
- The adversarial subagents operate in temporary isolated workspaces.
- Any scratch scripts, test mutations, or exploit payloads they create are executed in isolation and never leak into the main branch until verified.

### Barrier 4: The Deterministic Acid Test (Non-LLM Physical Grounding)
- **The Golden Invariant:** LLM agreement is never accepted as proof.
- The diagnosis must execute a physical Python script (`PhysicalMutationFalsifier`):
  1. Executes the proposed audit rule or test suite against the **unmodified, buggy code**.
  2. Programmatically asserts that the execution fails (`exit_code != 0`).
  3. If the test passes against buggy code, compilation halts with a fatal `TautologicalTestViolation`.

---

## 4. Deliverable Format

When `/system-diagnosis` completes, it writes `trace/diagnoses/diagnosis_<defect_id>.md` containing:

1. **Section 1: Micro-Anomaly Isolation:** Grounded file paths, lines, and observed vs expected behavior.
2. **Section 2: Waterloo SoC Elevation:** 3-tier Macro/Meso/Micro root cause analysis.
3. **Section 3: Higher-Order Remedy:** Declarative IR changes, new compiler gates, or AST linters.
4. **Section 4: Downward Concrete Trace Walk:** Step-by-step trace showing where the gate triggers on the original defect.
5. **Section 5: Epistemic Firewall Attestation:**
   - *Exploit Subagent Findings:* Bypasses found and mitigations applied.
   - *Red Team Verdict:* [PASS | BLOCKED].
   - *Physical Acid Test Output:* Exit code != 0 confirmed against buggy substrate.
