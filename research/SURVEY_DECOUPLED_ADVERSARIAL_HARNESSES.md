# Literature Survey: Decoupled Adversarial Harnesses & Falsification Engines

- **Document ID:** `RES-LIT-002`
- **Topic:** Theory & Practice of Independent Falsification for Autonomous Software
- **Author:** Meta-Axioma Systems Research

---

## 1. The Epistemological Impasse: Generator–Judge Collusion

In standard agentic coding pipelines, when an AI model is asked to "test its code," it generates unit tests that assert the correctness of its own implementation:
$$\text{TestSuite} = f_{\text{LLM}}(\text{Code})$$
This results in **100% false positive verification**:
- The tests only exercise the paths the model anticipated.
- Invariants that were misunderstood in the implementation are equally misunderstood in the assertions.
- Unhandled edge cases, concurrency hazards, and network failure modes are completely omitted from the test suite.

To break this impasse, the evaluation engine must be **epistemically decoupled** from the generative compiler.

---

## 2. Karl Popper & Imre Lakatos: Falsification as a Software Gate

### A. The Demarcation Criterion (Popper 1934)
A system architecture cannot be classified as "verified" because it passed conforming examples. It is verified only if it has actively survived severe, independent attempts at refutation:
$$\text{Corroboration}(\mathcal{H}) \propto \text{Severity of Attempted Falsification}(\mathcal{E})$$
- A test suite with low severity (e.g. trivial input/output checks) provides approximately zero epistemic corroboration.
- High-severity tests deliberately target known structural vulnerabilities: partition boundaries, message reordering, clock drift, and memory exhaustion.

### B. Proofs and Refutations (Lakatos 1976)
Lakatos showed that mathematical and software models evolve through a dialectic of **conjectures and refutations**:
1. Initial conjecture is proposed.
2. A counter-example (monster) is produced by an adversary.
3. The conjecture is refined (concept-stretching or lemma-incorporation) to incorporate the counter-example, leading to a strictly more powerful theory.
- In software architecture, this means: **a system that never encounters a failing counter-example during compilation has not evolved; it has simply regurgitated an untested prior.**

---

## 3. Industrial Foundations of Adversarial Harnesses

### A. Jepsen Testing (Kyle Kingsbury / Aphyr)
Jepsen is the gold standard for distributed systems verification (tested on Cassandra, Raft, etcd, CockroachDB, Kafka):
- **Nemesis Injection:** An independent thread ("The Nemesis") executes unannounced network splits, IP tables drops, process pauses (`SIGSTOP`/`SIGCONT`), and clock jumps.
- **Client Concurrency Thrash:** Hundreds of concurrent clients issue randomized read/write/CAS operations.
- **Knossos / Elle Linearizability Checkers:** Evaluates the resulting execution trace against strict consistency models (Linearizability, Strict Serializability, Causal Consistency), mathematically detecting state loss, stale reads, or split-brain divergence.

### B. Chaos Engineering (Netflix / Basiri et al. 2016)
Principles of Chaos Engineering define:
1. Define 'steady state' as normal measurable system output.
2. Hypothesize that this steady state will continue in both the control group and experimental group.
3. Introduce variables that reflect real-world events like servers that crash, hard drives that malfunction, network connections that are severed.
4. Try to disprove the hypothesis by looking for a difference in steady state between the control group and the experimental group.

### C. Property-Based & Metamorphic Testing
- **QuickCheck (Claessen & Hughes 2000):** Formulates formal algebraic invariants (e.g. $f(f^{-1}(x)) = x$, associativity $(a \star b) \star c = a \star (b \star c)$) and generates thousands of randomized, adversarial inputs with automated shrinking to find the minimal failing counter-example.
- **Metamorphic Testing (Chen et al. 1998):** Solves the "Oracle Problem" by testing metamorphic relations between distinct executions (e.g. $f(x \cup y) = f(x) \sqcup f(y)$) without requiring manual knowledge of expected ground-truth values.

---

## 4. Mathematical Formulation for Meta-Axioma's Decoupled Crucible

In Meta-Axioma, any candidate compiler or subsystem $\mathcal{C}$ must be evaluated by a decoupled Crucible $\mathcal{K}$:
$$\mathcal{K} = \langle \mathcal{N}_{\text{nemesis}}, \mathcal{G}_{\text{generator}}, \mathcal{V}_{\text{verifier}}, \mathcal{M}_{\text{metrics}} \rangle$$
Where:
1. $\mathcal{N}_{\text{nemesis}}$ is an autonomous chaos injector (asymmetric partitions, packet drops, interleaving delays) with stochastic parameterization $\sigma \sim \mathcal{D}_{\text{chaos}}$.
2. $\mathcal{G}_{\text{generator}}$ generates high-entropy concurrent workloads independent of $\mathcal{C}$'s source code.
3. $\mathcal{V}_{\text{verifier}}$ checks algebraic invariant preservation (cohomology error $H^0 = 0$, linearizability, no split-brain divergence).
4. $\mathcal{M}_{\text{metrics}}$ measures physical Landauer dissipation:
   $$Q_{\text{dissipated}} = k_B T \ln 2 \cdot \sum \text{bits\_erased}$$

### The Hard Mechanical Gate:
$$\text{Admissible}(\mathcal{C}) \iff \text{Passed}(\mathcal{K}(\mathcal{C})) \quad \land \quad \text{Severity}(\mathcal{K}) \ge \Theta_{\text{adversarial}}$$
Any candidate evaluated solely by static unit tests is rejected at compile time.
