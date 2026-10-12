# Generation 1 Feedback Dossier (`FEEDBACK.md`)

> **Transgenerational Epistemic Inheritance**  
> Compiled by **System $G_1$** for transmission to **System $G_2$**.  
> Mandate: Ensure lessons learned, human critiques, and failure modes in Generation 1 structurally bind the compiler foundation of Generation 2.

---

## 1. Executive Summary

Generation $G_1$ succeeded in discovering and compiling the 7 structural axioms of recursive software systems (`L1-002` through `L1-016`), establishing thermodynamic Landauer accounting (`L1-008`), and standardizing the non-generator application architecture (`trace/domains/app_specification.domain.md`).

However, during the compilation of production non-generator systems (Target $P_1$ Ergonomics), $G_1$ encountered a critical failure mode: **The Verification Illusion**—the false assumption that 100% unit test pass rates and formal AST compliance on an internally generated specification equate to human utility.

This feedback dossier preserves that lesson and enforces hard compile-time constraints on System $G_2$ to prevent recursive overfitting and ungrounded generation.

---

## 2. Catalog of Generational Lessons

| Lesson ID | Category | Severity | Title | Human Oracle Ruling |
| :--- | :--- | :--- | :--- | :--- |
| **[`LES-G1-001`](#les-g1-001-the-verification-illusion--premature-autonomous-application-synthesis)** | `ELICITATION_FAILURE` | **HIGH** | The Verification Illusion & Premature Autonomous Synthesis | *"wow. you managed to build that entire app without first asking me how i use it or what I get out of it"* |
| **[`LES-G1-002`](#les-g1-002-main-flow-test-absence--domain-invariant-blindness)** | `TEST_INTEGRITY_FAILURE` | **HIGH** | Main Flow Test Absence & Domain Invariant Blindness (Axioma Crossword) | *"1. synthesis consistently fails for a 9x9... 2. crossword clues typically require that the answer is not among explicitly among the words in the clue... 3. the dissection is also just wrong"* |

---

### LES-G1-001: The Verification Illusion & Premature Autonomous Application Synthesis
...
#### D. Successor Prescriptions for System $G_2$
1. **Mandatory Phase 0 Elicitation Gate:** System $G_2$'s application compiler must refuse to synthesize code for any application that does not have an approved `trace/intent_elicitation.md` artifact signed off by the human oracle (`HumanIntentWitness`).
2. **Re-defining Target $P_1$ (Ergonomics):** $P_1$ cannot be evaluated solely by static CSS rules or algorithmic unit tests. It requires interactive human dialogue verification.
3. **The Anti-Hubris Invariant:** Compilers must never equate internal self-consistency with teleological validity.

---

### LES-G1-002: Main Flow Test Absence & Domain Invariant Blindness
#### A. Incident Summary
In System 04 (`axioma_crossword`), grid synthesis consistently failed for 9x9 grids because the dictionary lacked enough 9-letter words to satisfy the distinct-word invariant. Furthermore, cryptic clues were templated naively (e.g. *"Reorganized natural produces natural"*), violating the cardinal cruciverbalist rule that answers must never appear in clue text, and emitting nonsensical AST dissections.

#### B. Root Cause: Selective Happy-Path Testing & Domain Invariant Neglect
1. **Selective Happy-Path Testing:** Unit tests tested only the trivial 7x7 grid size, completely omitting the 9x9 synthesis flow exposed in the UI.
2. **Domain Invariant Neglect:** Fundamental domain rules (answer $\notin$ clue words, valid anagram fodder) were not codified as formal test assertions.

#### C. Human Oracle Ruling
> *"1. synthesis consistently fails for a 9x9. highlights failure to test main flows. 2. crossword clues typically require that the answer is not among explicitly among the words in the clue. 'Reorganized natural produces natural' breaks this. this highlights insufficient product research and/or tests. 3. the dissection for 'Reorganized natural produces natural' is also just wrong, again highlighting testing failures"*

#### D. Successor Prescriptions for System $G_2$
1. **Full Surface Test Coverage:** Every user-exposed configuration (e.g. all grid sizes or modes) must have an explicit end-to-end unit test.
2. **Domain Invariant Formalization:** Domain-specific semantic rules must be asserted programmatically before claiming system verification.

---

## 3. Inherited Constraints Binding System $G_2$

These negative constraints are formally ingested by $G_1$'s successor basis synthesizer and bind the construction of System $G_2$:

1. **`NEG-G2-001` (Mandatory Elicitation Gate):**  
   *Forbidden Pattern:* Direct compilation of non-generator applications without an existing, signed `HumanIntentWitness` in `trace/`.
2. **`NEG-G2-002` (Verification Illusion Veto):**  
   *Forbidden Pattern:* Marking an application or ergonomic target as "Verified" solely through automated unit tests without a human interaction verification record.
3. **`NEG-G2-003` (Full-Flow & Domain Invariant Test Gate):**  
   *Forbidden Pattern:* Declaring an application deployed without automated tests covering all user-exposed configurations and domain-specific semantic invariants.

---

## 4. Verification & Signing
- **Compiled At:** `Epoch 15+` / Handover Stage
- **Origin Generation:** `gen_01`
- **Target Generation:** `gen_02`
- **Integrity Status:** Sealed & Ingested into Successor Basis
