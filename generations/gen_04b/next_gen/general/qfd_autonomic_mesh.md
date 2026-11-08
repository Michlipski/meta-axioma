# Autonomic Closed-Loop QFD Mesh Evolution Note (`qfd_autonomic_mesh.md`)

> **Document Type:** Generational Architectural Specification & Evolution Note (RFC)  
> **Target Scope:** Cross-Cutting Quality Function Deployment & Autonomic Decision Mesh  
> **Target Generation:** Generation 5 ($G_5$ / $G_{N+1}$)  
> **Author:** Sovereign Research Service (`services/research/`, 192.168.40.10) & Sovereign Audit Service (`services/audit/`, 192.168.40.30)  
> **Status:** PROPOSED (Succession Architecture Charter for Quality Engineering)  
> **Related URNs:** `urn:axioma:g5:qfd:autonomic_mesh`, `urn:axioma:g5:sheaf:roof_cohomology`, `urn:axioma:g5:voc:friction_stream`  

---

## 1. Context & Generation 4b Baseline

In Generation 4b, the **House of Quality (QFD) Engine** (`services/research/src/qfd_engine.py`) and **MCDA TOPSIS Ranker** (`services/research/src/mcda_ranker.py`) introduced mathematical rigor into option formulation and proposal generation:
1. **Mathematical Derivation:** Engineering characteristics are derived directly from customer requirements and Waterloo Tier 1 Situations of Concern (`[L1-G3B-000]`), computing technical importance $T_j = \sum W_i R_{ij}$ and relative normalized weights $\bar{T}_j$.
2. **Substrate Invariant Immunity (`[VULN-QFD-003]`):** Critical physical invariants (`CharacteristicType.SUBSTRATE_INVARIANT`) are immune to relevance threshold pruning.
3. **Pareto Dominance Filtering (`[VULN-QFD-004]`):** Dominated options are eliminated prior to TOPSIS ranking to prevent rank reversal anomalies.
4. **Zero-Bypass Micro-Auditing (`[INV-G4B-CAUSAL-001]`):** `QFDConsistencyAuditor` guarantees temporal causality, eliminates orphan features, verifies roof contradiction coverage, and enforces recommendation parity.

However, Generation 4b QFD remains a **static, open-loop design-time artifact**. Once sealed, the House of Quality is static. It does not ingest live user friction telemetry, cannot automatically cascade across runtime operations, and resolves roof contradictions via manual prose mitigation rather than formal topological proofs.

---

## 2. Generation 5 Paradigm Shift: The Closed-Loop Autonomic QFD Mesh

Generation 5 transforms QFD from a static pre-compilation gate into a **live, autonomic, closed-loop cybernetic feedback mesh**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   GENERATION 5 AUTONOMIC CLOSED-LOOP QFD MESH                          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ LEVEL 1: SOVEREIGN RESEARCH (House of Quality 1 - Product Planning)             │   │
│   │ Requirements (VOC) ───[Relationship Tensor]───► Engineering Characteristics   │   │
│   └───────────────────────────────────┬────────────────────────────────────────────┘   │
│                                       │ (Cascade via Event Mesh)                       │
│                                       ▼                                                │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ LEVEL 2: BUILDER ENCLAVE (House of Quality 2 - Subsystem Part Deployment)       │   │
│   │ Characteristics ──────[Functorial Mapping]─────► Code Leaves & Enclaves        │   │
│   └───────────────────────────────────┬────────────────────────────────────────────┘   │
│                                       │                                                │
│                                       ▼                                                │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ LEVEL 3: DEPLOYER ENCLAVE (House of Quality 3 - Process & Network Topology)    │   │
│   │ Module Specs ─────────[WireGuard/P2P Matrix]───► Host Placement & Sinks        │   │
│   └───────────────────────────────────┬────────────────────────────────────────────┘   │
│                                       │                                                │
│                                       ▼                                                │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ LEVEL 4: SIMULATOR ENCLAVE (House of Quality 4 - Continuous Verification)      │   │
│   │ Operations ───────────[Chaos & User Swarms]────► Live Friction Telemetry       │   │
│   └───────────────────────────────────┬────────────────────────────────────────────┘   │
│                                       │                                                │
│                                       │ mesh.events.qfd.friction_telemetry             │
│                                       └─────────────────────────────────┐              │
│                                                                         │              │
│   ◄─────────────────────── (Autonomic Feedback Loop) ───────────────────┘              │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Four Core Pillars of the Gen 5 QFD Architecture

### 3.1 4-Phase Cascading Deployment across the Sovereign Mesh
Standard industrial QFD (Akao's 4-Phase Model) is lifted into distributed autonomic compiler enclaves:
1. **Level 1 — Product Planning (`services/research/`):** Translates Waterloo Tier 1 Situations of Concern into verified engineering characteristics and topological correlation roofs.
2. **Level 2 — Subsystem Part Deployment (`services/builder/`):** The output characteristics of Level 1 become the inputs to Level 2, determining module boundaries, type interfaces, statechart strata, and AST skeletons.
3. **Level 3 — Process Deployment (`services/deployer/`):** Translates module constraints into container topology, WireGuard VPN peering, resource limits, and SQLite WAL enclaves.
4. **Level 4 — Quality Control & Live Operations (`services/simulator/`):** Translates process parameters into runtime health probes, SMT invariant watchers, and continuous journey walkers.

### 3.2 Dynamic Continuous VOC via `mesh.events.qfd.friction_telemetry`
Instead of one-time user interviews, Generation 5 employs **autonomous synthetic persona swarms** running inside `services/simulator/`:
- Hundreds of headless journey walkers simulate diverse cognitive profiles (novice, power user, malicious actor, latency-constrained node).
- When a journey step experiences unexpected latency, DOM occlusion, confusing error states, or excessive steps-to-value, the simulator emits a structured telemetry event:
  ```json
  {
    "event_topic": "mesh.events.qfd.friction_telemetry",
    "soc_id": "soc_axioma_crucible",
    "friction_type": "ERGONOMIC_STEP_EXPLOSION",
    "target_char_id": "CHAR_STEPS_TO_VALUE",
    "measured_delta": +2.4,
    "user_archetype": "NOVICE_STUDENT",
    "timestamp_ns": 1761273900000000000
  }
  ```
- The Research Service continuously consumes this stream. When aggregate friction exceeds threshold $\theta_{\text{friction}}$, the customer requirement weight $W_i$ is dynamically adjusted, and a proposal amendment is automatically initiated.

### 3.3 Sheaf-Theoretic Cohomology ($H^1$) Modeling of the Correlation Roof
In Generation 4b, the Correlation Roof is a pairwise correlation table. In Generation 5, the correlation roof is formalized as a **1-dimensional Sheaf Cohomology complex**:
- Let $X$ be the topological space of engineering characteristics $\{x_i\}$, covered by open sets $U_i$ representing subsystem domains.
- A section of the sheaf $\mathcal{F}(U)$ assigns local design parameter assignments.
- When two characteristics $x_a$ and $x_b$ share a negative correlation ($\text{CorrelationType.NEGATIVE}$ or $\text{STRONG\_NEGATIVE}$), they define a non-trivial transition cocycle:
  $$g_{ab} \in \mathcal{F}(U_a \cap U_b), \quad g_{ab} \neq 0$$
- If a global assignment of parameters is impossible without violating local constraints, the first cohomology group is non-vanishing:
  $$\check{H}^1(\mathcal{U}, \mathcal{F}) \neq 0 \quad (\text{Topological Contradiction Obstruction})$$
- **TRIZ Category Morphisms:** The compiler applies functorial categorical morphisms (separation in time, separation in physical substrate, or higher-order functorial wrapping) that split the stalk $\mathcal{F}_x$ into orthogonal sub-sheaves $\mathcal{F}' \oplus \mathcal{F}''$, proving $\check{H}^1 = 0$ (obstruction freedom).

### 3.4 Autonomous Socratic Council Multi-Agent Quorum
Determining relationship tensor strengths ($R_{ij} \in \{0, 1, 3, 9\}$) is too critical to leave to a single LLM prompt. Generation 5 executes a **game-theoretic Socratic debate**:
- **Domain Ontologist:** Argues for semantic fidelity and customer JTBD alignment.
- **Ergonomics Advocate:** Champions cognitive ease, minimal steps-to-value, and sensory ergonomics.
- **Byzantine Chaos Skeptic:** Challenges optimistic assumptions and pushes for defensive invariants.
- **Substrate Invariant Guardian:** Vetoes any scoring that undervalues Landauer bounds, single-workstation hermeticism, or non-loopback addressing.
- The debate proceeds until reaching an **$\epsilon$-Nash Equilibrium** where no agent can unilaterally improve invariant satisfaction. Each participant cryptographically signs the resultant tensor using its sovereign ECDSA/Ed25519 key, forming a verified **Quorum Attestation Certificate**.

---

## 4. Formal Generational Invariants for Gen 5 QFD

### `[L1-G5-QFD-001]` Closed-Loop Telemetry Convergence
The autonomic feedback loop between `services/simulator/` and `services/research/` must be provably convergent. Repeated adjustments to customer requirement weights $W_i^{(t)}$ must satisfy:
$$\lim_{t \to \infty} \|W_i^{(t+1)} - W_i^{(t)}\| < \epsilon_{\text{conv}}$$
oscillatory or diverging weight vectors halt the autonomic pipeline and trigger human governance escalation.

### `[L1-G5-QFD-002]` Sheaf Cohomology Obstruction Freedom
No Level 2 Builder compilation may proceed while the 1st Sheaf Cohomology group of the correlation roof contains non-trivial obstructions:
$$\check{H}^1(\mathcal{U}_{\text{roof}}, \mathcal{F}_{\text{contracts}}) \cong 0$$
All negative roof contradictions must be eliminated via formally certified categorical TRIZ morphisms.

### `[L1-G5-QFD-003]` Cryptographic Quorum Attestation
Every `HouseOfQualityIR` emitted in Generation 5 must include a multi-agent `QuorumAttestationCertificate` signed by at least 3 distinct sovereign personas with zero overlapping cognitive seeds:
$$\text{VerifyQuorum}(\text{HoQ}.\text{merkle\_root}, \text{Signatures}_{1..k}) == \text{True}, \quad k \ge 3$$

---

## 5. Verification and Acceptance Criteria
1. Subprocess telemetry replay: Ingest 10,000 synthetic friction events and verify deterministic QFD weight updating in $< 500\text{ms}$.
2. Sheaf cohomology solver: Prove obstruction elimination on a known 5-node negative contradiction graph using simplicial homology reduction.
3. Quorum Byzantine resilience: Inject 1 Byzantine agent attempting to manipulate weights to 0; prove that the remaining 3 agents reject the attestation and preserve invariant bounds.
