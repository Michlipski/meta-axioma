# Generation 2 Feedback Dossier (`FEEDBACK.md`)

> **Transgenerational Epistemic Inheritance & Real-Time Operational Feedback**  
> **Generation:** $G_2$ (Autonomous Domain Compiler)  
> **Predecessor Origin:** $G_1$ (The Axiom Bootstrapper)  
> **Mandate:** Preserve and actively enforce lessons learned from $G_1$, while capturing runtime feedback, ergonomic frictions, and post-mortems in Generation 2.

---

## 1. Inherited Lessons from Generation 1

Generation 2 formally ingests the hard lessons of Generation 1:

| Lesson ID | Origin | Category | Severity | Title | Human Oracle Ruling | Inherited Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`LES-G1-001`** | $G_1$ | `ELICITATION_FAILURE` | **HIGH** | The Verification Illusion & Premature Synthesis | *"wow. you managed to build that entire app without first asking me how i use it or what I get out of it"* | **`NEG-G2-001` & `NEG-G2-002`** |
| **`LES-G1-002`** | $G_1$ | `TEST_INTEGRITY_FAILURE` | **HIGH** | Main Flow Test Absence & Domain Invariant Blindness | *"1. synthesis consistently fails for a 9x9... 2. crossword clues typically require that the answer is not among explicitly among the words in the clue... 3. the dissection is also just wrong"* | **`NEG-G2-003`** |

---

## 2. Inherited Constraints Binding System $G_2$

1. **`NEG-G2-001` (Mandatory Human Intent Elicitation Gate):**  
   *Forbidden Pattern:* Direct compilation of non-generator applications without an approved, signed `trace/intent_elicitation.md` artifact.
2. **`NEG-G2-002` (Verification Illusion Veto):**  
   *Forbidden Pattern:* Marking an application or ergonomic target as "Verified" solely through automated unit tests without a human interaction verification record.
3. **`NEG-G2-003` (Full-Flow & Domain Invariant Test Gate):**  
   *Forbidden Pattern:* Releasing systems without automated regression tests covering all user-exposed configurations and domain-specific semantic invariants.
4. **`NEG-G2-004` (Substrate Pre-Flight Verification Gate):**  
   *Forbidden Pattern:* Releasing multi-substrate packages (e.g. Android APKs) without verifying platform manifest flags (`android.useAndroidX=true`), local asset bundle fallbacks, and launch render integrity.
5. **`NEG-G2-005` (Anti-Mock Hardware & State Reality Invariant):**  
   *Forbidden Pattern:* Employing simulated timers, fake notification banners, or hardcoded mock counters in place of real system/hardware APIs (`NotificationChannel`, `POST_NOTIFICATIONS`, Web Notifications API) and state-derived event calculations.
6. **`NEG-G2-006` (Clean-Slate Production State Invariant):**  
   *Forbidden Pattern:* Polluting production databases or new user installations with dummy, mock, or placeholder records. Production systems must initialize to a pristine state with only essential user-specified seeds.
7. **`NEG-G2-007` (External API Verification & Resilient Resolution Invariant):**  
   *Forbidden Pattern:* Relying on unverified third-party web APIs without live pre-flight validation of endpoint availability, CORS headers, latency, and automated multi-tier offline fallbacks.
8. **`NEG-G2-008` (Visual Dignity & Ergonomic Affordance Gate):**  
   *Forbidden Pattern:* Presenting unstyled, raw browser default elements (e.g. "ugly white rectangle buttons") or unpolished visual hierarchies to the user. Every interactive affordance must meet the cognitive ergonomics baseline.
9. **`NEG-G2-009` (Cruciverbalist Lexical Purity Invariant):**  
   *Forbidden Pattern:* Generating pseudo-words, scrambled letter fragments, or arbitrary phonetic nonsense (e.g. "ran tula", "cruel tu", "legal hen c", "nna otci") in crossword clues. Every single token in the clue surface reading must be a recognized, authentic English dictionary word. When anagram fodder cannot be formed from real English words, compilers must employ Double Definitions, Charades, or Telescopic Hidden Words.

---

## 3. Active Generation 2 Lessons Ledger (The "Usable App" Doctrine)

Recorded during the construction, refinement, and production hardening of **`axioma_lexis`** and **`axioma_crossword`**:

| Lesson ID | Subsystem | Category | Severity | Human Oracle Ruling | Architectural Prescriptions & Invariant Enforced |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`LES-G2-LEX-001`** | Android Gradle & Assets | `SUBSTRATE_BUILD_FAILURE` | **HIGH** | *"checkDebugAarMetadata FAILED... android.useAndroidX is not enabled"*; *"it opened to a black screne"* | **`NEG-G2-004`**: Enforce platform configuration pre-flight checks (AndroidX flags, asset resolution, offline asset bundles). |
| **`LES-G2-LEX-002`** | Spaced Repetition Engine | `MOCK_SUBSTITUTION_FAILURE` | **CRITICAL** | *"this is supposed to be the polished version but there is a simulated notification, and the session says 3 words reviewed even though there was just 1"* | **`NEG-G2-005`**: Zero mock substitution. All telemetry and alerts must reflect real event logs and real OS capabilities. |
| **`LES-G2-LEX-003`** | Lexicon Initial State | `DATA_POLLUTION` | **MEDIUM** | *"when I build I'd like there to be a blank slate apart from zuhandenheit"* | **`NEG-G2-006`**: Ban mock fixtures in production storage. Clean slate initialization with only user-demarcated seeds. |
| **`LES-G2-LEX-004`** | Dictionary Hydrator | `API_PRECONDITION_FAILURE` | **HIGH** | *"the api appears to be having problems. did you check that it exists?"* | **`NEG-G2-007`**: Verify API endpoints via live network requests before code synthesis; implement tiered offline-first resolution. |
| **`LES-G2-LEX-005`** | Visual Design & Theme | `ERGONOMIC_DIGNITY_FAILURE` | **HIGH** | *"Also, there are a lot of buttons that are just white rectangles that are remarkably ugly"* | **`NEG-G2-008`**: Ban unstyled browser default elements. Every affordance must have cohesive design tokens, haptics, and visual finish. |
| **`LES-G2-LEX-006`** | Semantic Hydration | `INCOMPLETE_SEMANTICS` | **MEDIUM** | *"Now I've noticed that the context and mnemonic are empty. I don't personally need those perse but it would be nice"* | Entity schemas must achieve full semantic coverage; populate context, mnemonics, and etymologies rather than leaving blank fields. |
| **`LES-G2-LEX-007`** | Release Packaging | `TEST_SCAFFOLDING_LEAK` | **MEDIUM** | *"they worked. please remove them for the final build. On that note, is there a more finalized build I should install now or is this one okay?"* | Decouple test harnesses from production builds; compile clean, signed release artifacts (`app-release.apk`) free of debugging UI. |
| **`LES-G2-CW-001`** | Crossword Lexicon & Clues | `CRUCIVERBALIST_AUTHENTICITY_FAILURE` | **CRITICAL** | *"ran tula are not words"* | **`NEG-G2-009`**: Ban pseudo-words and meaningless letter jumbles in cryptic crosswords. All clue surface tokens must be legitimate English dictionary words. |

