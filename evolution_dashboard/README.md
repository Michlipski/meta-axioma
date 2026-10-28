# Meta-Axioma Generational Evolution Studio & G4b Zenith Workbench

> **System ID:** `14` (`axioma_evolution_dashboard` / `evolution_dashboard`)  
> **Generational Benchmark:** Generation 4b Sovereign Service Mesh Architecture  
> **Status:** **Deployed & Operational** (17/17 Unit Tests Passing)  
> **Port:** `8105`  
> **Primary Authors:** Meta-Axioma Systems Architecture & Autonomous Meta-Swarm  
> **Location:** Root Workspace (`/evolution_dashboard/`)

---

## 1. Overview & Teleological Purpose

The **Axioma Evolution Dashboard** is an enterprise-grade interactive visual studio, topology workbench, and simulation engine mapping the complete 8-stage evolutionary trajectory of the Meta-Axioma recursive self-compiler:

$$S_0 \longrightarrow G_1 \longrightarrow G_2 \longrightarrow G_3 \longrightarrow G_{1b} \longrightarrow G_{2b} \longrightarrow G_{3b} \longrightarrow G_{4b}$$

Designed specifically for **engineering leaders, technical recruiters, and systems researchers**, this platform presents:
- **Surface-Level Readability (Layman Mode):** Clear, relatable plain-English explanations, metaphors, and intuitive visual models that anyone can grasp within 30 to 60 seconds.
- **Deep Academic Rigor (Systems Theory Mode / Hover Cards):** Machine-checkable mathematical axioms, SMT Z3 solver proofs, category-theoretic state morphisms ($S_{t+1} = f(S_t, E)$), Landauer thermodynamic limits ($Q = k_B T \ln 2 \cdot \text{bits}$), and Waterloo Situation of Concern (SoC) hierarchies.
- **Root-Level Permanence:** Located directly at the root level of the repository (`/evolution_dashboard/`) for continuous version control, periodic generational updates, and seamless embedding into the public systems portfolio.

---

## 2. Core Functional Anatomy

1. **Top Hero: The Meta-Axioma Philosophy**
   - *Why Formal Math is the Secret to Reliable AI Software:* The narrative explaining why conventional AI coding collapses at scale and how mathematical bounding guarantees software correctness.
   - *The Three Core Pillars:* Bounding AI in Math (Not Prompts), Brain vs. Muscle Cognitive Partitioning, and The Three-Tiered Jettison.
   - *The Core Invariant Triad:* Reality grounding (Landauer limits, User Zero), Human control (negative vetoes `NEG-###`, 1-tap undo), and Mathematical non-contradiction (category theory).
2. **Current Zenith: Generation 4b Sovereign Multi-Service Mesh**
   - *5 Sovereign Services:* Research (`soc_g4b_researcher`), Builder (`soc_g4b_builder`), Audit (`soc_g4b_audit`), Telemetry (`soc_g4b_telemetry`), and Governance (`soc_g4b_governance`).
   - *Dedicated Private Subnet:* `192.168.40.0/24` with anti-loopback interface binding (`[L1-G3B-012]`).
   - *Asymmetric RFC Protocol Bus:* Mathematical mediation between Builder and Research via the Z3 SMT prover bridge with formal `CounterProof` extraction.
3. **Interactive Visual Walkthrough: How 4b Compiles a Real App (`axioma_go`)**
   - Step-by-step visual compilation of `axioma_go` (10x10 Tactical Go Dojo):
     - *Step 1:* Human Intent & Waterloo Problem Normalization (Zero-Code Research boundary)
     - *Step 2:* Asymmetric RFC Bus Mediation & Z3 SMT Math Proving
     - *Step 3:* Dual-Model Cognitive Subagent Sandboxed Synthesis (Brain vs. Muscle)
     - *Step 4:* Sheaf-Quorum Adversarial Chaos Auditing (Byzantine fuzzing)
     - *Step 5:* Thermodynamic Telemetry Sealing & Live Deployment (Port `8082`)
   - *Interactive Controls:* Auto-Play, Step Forward/Back, Reset, and "Inspect Generated Code & Specs" drawer.
4. **The 8-Stage Architectural Evolution Spine ($S_0 \to G_{4b}$)**
   - Scrubbable timeline with all 8 eras.
   - Plain-English executive summaries: The Problem We Solved, In Plain English, Key Breakthrough, and Everyday Analogy.
   - 4-Tier Beehive SVG Topology Canvas with interactive nodes and live node inspector drawer.
   - Clickable transformation delta links ($\Delta_1 \to \Delta_7$) detailing added/removed/refactored primitives and catalysts.
5. **Live Side-by-Side Generational Diff Workbench (Option 3 Feature)**
   - Compare any two generations (e.g. $G_1$ vs $G_{4b}$) with dynamic diff matrices, node count deltas, and invariant shifts.
6. **Architectural Governance Spotlight**
   - Dedicated spotlight for operator insights, exogenous seeds, and negative vetoes across every generation.
7. **Live Landauer Thermodynamic Dissipation Calculator**
   - Real-time bit-erasure dissipation slider ($0$ to $50,000$ bits) computing physical energy dissipation in Joules ($Q = k_B T \ln 2 \cdot \text{bits}$).
   - Grounded in Rolf Landauer's 1961 physical reversibility limit ($k_B T \ln 2 \approx 2.871 \times 10^{-21}\text{ J/bit}$) and Category-Theoretic state preservation (`[L1-008]`).

---

## 3. Running the Dashboard

```bash
# 1. Quick Verification
python3 run.py --verify-only

# 2. Launch HTTP Server (Port 8105)
python3 run.py --port 8105

# 3. Open in Browser
open http://localhost:8105/

# 4. Open Standalone Offline File Directly (Zero CDN Dependencies)
open dashboard.html
```

---

## 4. Test Suite Execution

```bash
python3 -m unittest discover -v -s tests
```
*Result: 17/17 tests passing in 0.022s.*

---

## 5. Periodic Generational Update Protocol (`[L1-G3B-019]`)

Under **Directive 7** of `AGENTS.md`, whenever a new generation (e.g., Generation 5) or sub-epoch is synthesized:
1. Append the new stage to `evolution_dashboard/data/evolution_data.json` with its 4-tier Beehive topology nodes and layman problem/summary fields.
2. Document operator epistemic interventions and negative vetoes.
3. Re-bundle the standalone deliverable:
   ```bash
   python3 scripts/bundle_dashboard.py
   ```
4. Verify tests and commit to source control:
   ```bash
   python3 -m unittest discover -v -s tests
   ```
