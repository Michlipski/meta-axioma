---
stack: Meta-Axioma-Recursive-Bootstrapper-V1
---

# Meta-Axioma Infrastructure & System Defaults

## Execution Stack

### Core Runtime
- **Language / Runtime:** Python 3.14 (AsyncIO)
- **Agent Orchestrator:** Google Antigravity (AGY) Agentic Architecture (Subagent swarms, custom skills, tool sandboxes, persistent terminals)
- **Tooling Constraint:** Free & Open-Source Software (FOSS) and native AGY tools strictly. Zero dependency on closed, paid proprietary APIs.

### Persistence & Storage
- **Canonical Invariant Store:** Markdown registries (`AXIOMS.md`, `ARCHITECTURE.md`)
- **Generational Artifact Store:** Hierarchical directory tree (`generations/gen_XX/epochs/`)
- **Telemetry Snapshots:** JSON serialization per epoch (`epoch_XXX.json`)
- **Observability Stream:** Standalone interactive HTML Dashboards with self-contained visual graphs and SVG telemetry widgets

---

## System Defaults

1. **Axiom Nomenclature:**
   - Level 0 Epistemic Axioms: `L0-###` (e.g., `L0-001`, `L0-003`)
   - Level 1 Structural Axioms: `L1-###` (e.g., `L1-002`, `L1-008`)
   - Negative Invariants (Human Vetoes): `NEG-###`

2. **Compute Decay Mechanics:**
   - Budget formula: $$T(n) = \frac{T_0}{1 + \alpha (n - n_0)}$$
   - Default constants: $T_0 = 10,000$ tokens, $\alpha = 0.5$, base active count $n_0 = 2$.
   - Floor parameters: Minimum token budget = $1,000$, minimum simulation depth = $2$.

3. **Strict Improvement Invariant:**
   - A candidate axiom is committed if and only if aggregate $\Delta E > 0$.
   - Any candidate causing invariant violations or $\Delta E \le 0$ is rejected and logged.

4. **Phase Transition Gate (The Jettison):**
   - Minimum active epistemic axioms: $n_{\text{epistemic}} \ge 10$.
   - Minimum epoch count: Epoch $\ge 10$.
   - Plateau condition: Rolling derivative $\frac{dE}{dt} < 0.002$ with positive lookahead dividend $\Lambda(H) > 0$.
   - Transition semantics: Epistemic axioms become `INACTIVE` scaffolding rather than being deleted.

5. **HITL Intercept Non-Blocking Default:**
   - Human interaction queries occur asynchronously.
   - Simulation workers and background tasks do not block un-intercepted pipelines.
