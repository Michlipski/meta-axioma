# Generation 2 Active Axiom Registry (`generation_02_axioms.md`)

> **Persistent Invariant Registry for Generation 2 ($G_2$)**  
> Formulated autonomously by **System $G_1$** via Target $S_2$ and the `G2BasisSynthesizer`.  
> Status: **OPERATIONAL (Epoch 2)**

---

## Registry Metadata

- **Generation:** $G_2$ (Autonomous Domain Compiler)
- **Status:** Operational
- **Epoch:** 2
- **Phase:** `PHASE_1_DOMAIN_EXECUTION`
- **Total Active Structural Axioms:** 7
- **Active Level 1:** 7
- **Inherited Negative Invariants:** 3
- **Inherited Scaffolding:** 10 Level 0 Axioms + 7 $G_1$ Structural Axioms (Accessible as generative priors)

---

## Active Level 1 Structural Basis Axioms

### [L1-G2-001] Adjoint Galois Substrate Connection & Multi-Target Preservation
- **Level:** Level 1 (Structural)
- **Status:** **ACTIVE**
- **Origin Epoch:** Epoch 1
- **Domain:** Applied Category Theory & Topos Theory
- **Statement:** Transformations between declarative user intent representations and multi-substrate compiled runtimes must form an adjoint Galois connection $\mathcal{F} \dashv \mathcal{G}$, ensuring bidirectional round-trip preservation and fidelity across heterogeneous execution targets without semantic drift.
- **Formal Expression:**
  $$\text{Hom}_{\mathcal{C}}(\mathcal{F}(A), B) \cong \text{Hom}_{\mathcal{D}}(A, \mathcal{G}(B)) \quad \text{with Unit } \eta: \text{Id}_{\mathcal{C}} \to \mathcal{G} \circ \mathcal{F} \quad \text{and Counit } \epsilon: \mathcal{F} \circ \mathcal{G} \to \text{Id}_{\mathcal{D}}$$
- **Operational Rule:** Any cross-substrate compiler transformation whose round-trip closure fails Galois adjoint bounds is rejected prior to code emission.
- **Teleological Purpose:** Enables humans to author concise, high-level intent models that compile into robust client and server code without leaky translations.

---

### [L1-G2-002] Ephemeral Self-Healing Invariant Restoration Loop
- **Level:** Level 1 (Structural)
- **Status:** **ACTIVE**
- **Origin Epoch:** Epoch 1
- **Domain:** Biological Homeorhesis & Cellular Repair
- **Statement:** Compiler and runtime execution pipelines encountering invariant infractions must trigger isolated, bounded self-healing loops within ephemeral exception enclaves before failing or emitting fatal termination.
- **Formal Expression:**
  $$\text{Infraction}(s) \implies \text{Loop}_{k \le 3}(\text{Heal}(s)) \land \text{BlastContainment}(s) \quad \text{where } \text{BlastContainment} \implies \text{Leakage} = \emptyset$$
- **Operational Rule:** Direct hard failure is forbidden for recoverable invariant infractions; up to 3 automated remediation cycles within sandbox isolation are strictly required.
- **Teleological Purpose:** Delivers resilient production software that self-repairs from transient failures and network partitions without interrupting the human user.

---

### [L1-G2-003] Cognitive Ergonomics & Persona Alignment Invariance
- **Level:** Level 1 (Structural)
- **Status:** **ACTIVE**
- **Origin Epoch:** Epoch 1
- **Domain:** Phenomenological Cognitive Science & Human-Computer Interaction
- **Statement:** Every user-facing boundary synthesized by Generation 2 must minimize Kullback-Leibler divergence between the human persona's mental model and the system state, maximizing persona goal velocity and eliminating cognitive friction.
- **Formal Expression:**
  $$D_{\text{KL}}(\text{Model}_{\text{User}} \parallel \text{Model}_{\text{System}}) \le \varepsilon_{\text{ergonomics}} \quad \text{and} \quad \text{Utility}(A_{\text{app}}) = \frac{\text{PersonaGoalVelocity}}{1 + \text{CognitiveFriction}} > U_{\min}$$
- **Operational Rule:** Compiler artifacts that introduce cryptic error codes, excessive interaction steps, or cognitive friction fail verification regardless of algorithmic correctness.
- **Teleological Purpose:** Prevents recursive compiler insularity; guarantees that non-generator production applications are intuitive, trustworthy, and joyful for humans.

---

### [L1-G2-004] Introspectable Zero-Trust Capability Scoping
- **Level:** Level 1 (Structural)
- **Status:** **ACTIVE**
- **Origin Epoch:** Epoch 1
- **Domain:** Object-Capability Operating Systems (KeyKOS / seL4)
- **Statement:** All external agent actions, tools, and side-effects must be demarked by granular, introspectable capability tokens equipped with cryptographic SHA-256 audit witnesses. Ambient or unscoped execution authority is strictly prohibited.
- **Formal Expression:**
  $$\text{Action}(t) \implies \text{Token}(t) \in \text{Scope}(\text{Persona}) \land \text{Witness}(t) \ne \bot$$
- **Operational Rule:** Any subsystem attempting to invoke an external tool or execute un-scoped system mutations without an explicit capability token fails with an immediate security boundary fault.
- **Teleological Purpose:** Guarantees that the human architect maintains absolute control and visibility over AI agent actions and external APIs.

---

### [L1-G2-005] Mandatory Human Intent Elicitation & Grounding Boundary
- **Level:** Level 1 (Structural)
- **Status:** **ACTIVE**
- **Origin Epoch:** Epoch 1
- **Domain:** User-Centered Design & Empirical Epistemology (Inherited from `LES-G1-001`)
- **Statement:** No non-generator application may compile without an explicit, verifiable `HumanIntentWitness` establishing the real-world human persona, JTBD (Jobs-To-Be-Done), daily workflow, and utility function.
- **Formal Expression:**
  $$\text{Compile}(\text{App}) \implies \text{Witness}(\text{HumanIntent}) \in \text{trace/} \land \text{Status}(\text{Witness}) = \text{SIGNED\_OFF}$$
- **Operational Rule:** The application compiler must abort with `GenerationalRegressionFault` if application compilation is attempted without prior human elicitation.
- **Teleological Purpose:** Directly eradicates the Verification Illusion: guarantees code generation never occurs in a vacuum detached from actual human needs.

---

### [L1-G2-006] Phenomenological Tool-Being & Zuhandenheit Attunement Invariant
- **Level:** Level 1 (Structural)
- **Status:** **ACTIVE**
- **Origin Epoch:** Epoch 2
- **Domain:** Heideggerian Phenomenological Ontology & Tool-Being (Injected via `L0-003` Exogenous Orthogonality)
- **Statement:** User-facing boundaries must measure the ontological transition from transparent *Zuhandenheit* (ready-to-hand) to conspicuous *Vorhandenheit* (present-at-hand) as a continuous intentional gradient. The telemetry circuit must mathematically detect cognitive rupture events—measuring intentional dwell, hesitation, compensatory undo frequency, and cognitive focus shift away from task objectives onto interface controls—scoring the exact disruption index $R_{\text{rupture}}$ rather than merely logging technical stack traces.
- **Formal Expression:**
  $$\Psi_{\text{tool}}(t) = 1 - R_{\text{rupture}} \quad \text{where} \quad R_{\text{rupture}} = \min\left(1.0, \, \frac{\tau_{\text{dwell}} - \tau_{\text{flow}}}{\tau_{\text{flow}}} \cdot w_{\text{dwell}} + C_{\text{undo}} \cdot w_{\text{undo}} + E_{\text{error}} \cdot w_{\text{error}}\right)$$
- **Operational Rule:** When $R_{\text{rupture}} \ge \varepsilon_{\text{flow}}$ (default: $0.45$), the system identifies an ontological breakdown, triggers ambient self-healing before conscious alienation, and appends the cognitive disruption directly into transgenerational compiler feedback (`feedback.json`).
- **Teleological Purpose:** Prevents software alienation; guarantees tools act as an invisible, transparent extension of human thought rather than cumbersome obstacles.

---

### [L1-G2-007] Kinetic Chaining & Semantic Momentum Propagation
- **Level:** Level 1 (Structural)
- **Status:** **ACTIVE**
- **Origin Epoch:** Epoch 2
- **Domain:** Movement Biomechanics & Kinesiology (Injected via `L0-003` Exogenous Orthogonality)
- **Statement:** Cross-substrate compilation from the core AST into edge runtimes (Terminal CLI, Headless Daemon, Web PWA) must operate as an articulated kinetic chain with compliant impedance matching. Rather than forcing rigid syntactic locking at translation boundaries (which leaks energy and fractures under variance), translation joints must preserve the *semantic momentum* $\mathbf{p}_{\text{semantic}}$ of the core AST across articulated adapters.
- **Formal Expression:**
  $$\mathbf{p}_{\text{semantic}} = \mathcal{M}_{\text{core}} \cdot \mathbf{v}_{\text{intent}} \quad \text{such that} \quad \oint_{\partial \text{Substrate}} (\mathbf{p}_{\text{semantic}} - \mathbf{J}_{\text{joint}} \cdot \dot{\mathbf{q}}) \, dt = 0 \quad \text{with } \frac{\Delta E_{\text{impedance}}}{\|\mathbf{p}_{\text{semantic}}\|} \le 0.05$$
- **Operational Rule:** Articulated substrate adapters must achieve $\ge 95\%$ semantic momentum retention and $\le 0.05$ joint impedance loss. Rigid syntactical coupling that leaks momentum across translation boundaries is rejected.
- **Teleological Purpose:** Enables fluid, organic multi-platform operation: commands and invariants flow smoothly from core AST to terminal, daemon, and browser without friction or translation distortion.

---

## Inherited Negative Invariants (Human Oracle Vetoes)

1. **`NEG-G2-001` (Mandatory Elicitation Gate):**  
   *Forbidden Pattern:* Direct compilation of non-generator applications without an existing, signed `HumanIntentWitness` in `trace/`.
2. **`NEG-G2-002` (Verification Illusion Veto):**  
   *Forbidden Pattern:* Marking an application or ergonomic target as "Verified" solely through automated unit tests without a human interaction verification record.
3. **`NEG-G2-003` (Full-Flow & Domain Invariant Test Gate):**  
   *Forbidden Pattern:* Declaring an application deployed without automated tests covering all user-exposed configurations and domain-specific semantic invariants.
