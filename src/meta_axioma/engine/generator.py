"""LLM prompt generator and rich candidate hypothesis generator with detailed system architecture profiles."""

from __future__ import annotations

import copy
import uuid
from typing import Any, Dict, List, Optional
from meta_axioma.types import Axiom, AxiomLevel, AxiomStatus, NegativeAxiom, PhaseState


# =====================================================================
# LEVEL 0: EPISTEMIC CANDIDATE POOL (Meta-Research Invariants)
# =====================================================================
LEVEL_0_EPISTEMIC_CANDIDATE_POOL: List[Axiom] = [
    Axiom(
        id="L0-004",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Popperian Demarcation & Active Counter-Example Synthesis",
        statement="Any epistemic claim or invariant must provide an algorithmic refutation witness; hypotheses lacking computable falsification boundaries are demarcated as metaphysical and discarded prior to simulation.",
        formal_expression=r"\forall \mathcal{H}, \; \exists \omega \in \Omega \; \text{s.t.} \; \text{Eval}(\mathcal{H}, \omega) = \bot \implies \text{Admissible}(\mathcal{H})",
        operational_rule="Candidates that cannot synthesize an explicit negative counter-example test harness are discarded at validation ingress.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Philosophy of Science (Karl Popper)",
            "source_principle": "Falsifiability Demarcation Criterion",
            "system_profile": {
                "archetype": "Dual-Channel Assertion & Counter-Example Runtime",
                "topology_type": "Pipeline with Continuous Counter-Example Probes",
                "topology_diagram": """[Hypothesis AST] ──> [Dual-Channel Parser]
                          │
           ┌──────────────┴──────────────┐
           ▼                             ▼
[Affirmative Path]             [Adversarial Refutation Harness]
           │                             │
           └──────────────┬──────────────┘
                          ▼
            [Falsifiability Arbiter] ──> [Compile-Time Witness]""",
                "subsystems": {
                    "Adversarial Refutation Harness": {
                        "role": "Synthesizes boundary counter-inputs aimed at falsifying module assertions.",
                        "invariant_rule": "Must generate at least one non-trivial counter-example test case.",
                    },
                    "Falsifiability Arbiter": {
                        "role": "Executes candidates against refutation vectors to prove falsifiability.",
                        "invariant_rule": "Tautological claims with zero failure states are rejected.",
                    },
                    "Counter-Example Tracer": {
                        "role": "Emits machine-readable diagnostic witnesses upon invariant breach.",
                        "invariant_rule": "Refutation failures must log minimal reproduction traces.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Forces hypothesis generator into high-entropy edge spaces to locate falsification witnesses (+0.0125).",
                    "target_e2_velocity": "Drastically accelerates rejection of vacuous, untestable claims without running deep simulations (+0.0180).",
                    "target_e3_yield": "Filters out untestable structural proposals early, yielding clean compilable specifications (+0.0090).",
                },
                "tradeoffs": {
                    "strengths": "Completely eliminates unprovable or tautological architectural claims; provides automated regression tests.",
                    "constraints": "Adds slight compilation overhead due to automatic test-vector synthesis.",
                },
            },
        },
    ),
    Axiom(
        id="L0-005",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Algorithmic Occam's Razor & Minimum Description Length (MDL)",
        statement="Between competing hypotheses of equivalent empirical fit, the hypothesis minimizing joint description length of model plus compressed residuals is strictly selected; architectural bloat is penalized proportionally to AST Kolmogorov complexity.",
        formal_expression=r"\mathcal{H}^* = \arg\min_{\mathcal{H}} \left( L(\mathcal{H}) + L(\mathcal{D} \mid \mathcal{H}) \right)",
        operational_rule="Candidates introducing redundant abstractions without proportional reduction in residual entropy are penalized by the compiler.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Algorithmic Information Theory (Kolmogorov & Rissanen)",
            "source_principle": "Minimum Description Length Principle",
            "system_profile": {
                "archetype": "AST Kolmogorov Pruning & Joint Code-Length Minimizer",
                "topology_type": "Hierarchical Complexity Compression Pipeline",
                "topology_diagram": """[Candidate Model AST] ──> [Kolmogorov Metric Evaluator]
                                 │
                                 ▼
                     [Residual Entropy Analyzer]
                                 │
                                 ▼
                   [Joint Code-Length Minimizer] ──> [Compact Verified Core]""",
                "subsystems": {
                    "AST Complexity Profiler": {
                        "role": "Measures description length L(H) in syntax tree nodes and operational token weights.",
                        "invariant_rule": "Penalizes unnecessary wrapper layers and pass-through proxies.",
                    },
                    "Residual Entropy Analyzer": {
                        "role": "Quantifies uncompressed variance in target outputs L(D|H).",
                        "invariant_rule": "Requires each added complexity unit to pay for itself in error reduction.",
                    },
                    "Isomorphism Collapser": {
                        "role": "Detects and merges redundant subsystem layers that perform isomorphic transformations.",
                        "invariant_rule": "Enforces strict canonical representation of state mutations.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Focuses search on lean, dense hypotheses rather than verbose variations (+0.0070).",
                    "target_e2_velocity": "Quickly rejects bloated hypotheses with excess degrees of freedom (+0.0150).",
                    "target_e3_yield": "Produces ultra-lean, highly maintainable structural compilation specifications (+0.0160).",
                },
                "tradeoffs": {
                    "strengths": "Prevents architectural over-engineering; minimizes runtime instruction footprints.",
                    "constraints": "May penalize nascent abstractions that require multi-epoch composition to show benefit.",
                },
            },
        },
    ),
    Axiom(
        id="L0-006",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Hegelian Dialectical Synthesis & Antinomy Reconciliation",
        statement="When two candidate hypotheses assert mutually contradictory architectural constraints yet both demonstrate positive empirical delta, the system must synthesize a higher-order meta-axiom that preserves the operational validity of both within bounded contextual domains.",
        formal_expression=r"\mathcal{T}_{\text{thesis}} \oplus \mathcal{A}_{\text{antithesis}} \xrightarrow{\text{Aufhebung}} \mathcal{S}_{\text{synthesis}} \quad \text{where} \quad \mathcal{V}(\mathcal{S}) > \max(\mathcal{V}(\mathcal{T}), \mathcal{V}(\mathcal{A}))",
        operational_rule="Competing axioms with orthogonal advantages are combined via contextual domain boundaries rather than greedy elimination.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Continental Philosophy / Dialectical Logic (G.W.F. Hegel)",
            "source_principle": "Sublation (Aufhebung) of Contradictory Theses",
            "system_profile": {
                "archetype": "Dialectical Conflict Resolver & Contextual Sublation Mesh",
                "topology_type": "Bifurcated Scope Mesh with Higher-Order Arbiter",
                "topology_diagram": """[Thesis Invariant] ──┐
                     ├──> [Antinomy Comparator] ──> [Context Boundary Partitioner]
[Antithesis Invariant]┘                                      │
                                                             ▼
                                                [Higher-Order Unified Invariant]""",
                "subsystems": {
                    "Antinomy Comparator": {
                        "role": "Identifies formal opposition between valid hypotheses (e.g., pure immutability vs high-speed mutable cache).",
                        "invariant_rule": "Only triggers when both opposing sides demonstrate strictly positive delta E.",
                    },
                    "Context Boundary Partitioner": {
                        "role": "Isolates execution scopes where each invariant holds true without conflict.",
                        "invariant_rule": "Prevents leakage of mutable semantics into immutable verification domains.",
                    },
                    "Sublation Synthesizer": {
                        "role": "Compiles unified higher-order invariant reconciling both operational modes.",
                        "invariant_rule": "Composite aggregate efficacy must strictly exceed both individual theses.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Synthesizes novel hybrid architectures that transcend single-paradigm traps (+0.0160).",
                    "target_e2_velocity": "Resolves design stalemates without oscillating back and forth between extremes (+0.0090).",
                    "target_e3_yield": "Produces resilient, dual-mode structural systems with high operational envelope (+0.0140).",
                },
                "tradeoffs": {
                    "strengths": "Recovers valuable insights from runner-up candidates rather than discarding them.",
                    "constraints": "Increases simulation depth required to verify multi-context boundary interactions.",
                },
            },
        },
    ),
    Axiom(
        id="L0-007",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Adversarial Stress Perturbation & Antifragile Invariant Hardening",
        statement="Epistemic assertions must demonstrate non-linear improvement in verification confidence under synthetic chaos injection; an invariant is considered verified only if its explanatory power monotonically increases when subjected to stochastic perturbations of target environmental states.",
        formal_expression=r"\frac{\partial^2 \mathcal{V}}{\partial \sigma^2} > 0 \quad \text{where} \quad \sigma \sim \mathcal{N}(0, \Sigma_{\text{chaos}})",
        operational_rule="Axioms whose verification degraded under noise injection are marked fragile and rejected.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Complex Systems & Control Theory (Nassim Taleb & Norbert Wiener)",
            "source_principle": "Dynamic Antifragility under Chaos Perturbation",
            "system_profile": {
                "archetype": "Chaos-Injected Antifragile Verification Harness",
                "topology_type": "Continuous Disturbance Feedback Loop",
                "topology_diagram": """[Candidate Axiom] ──> [Stochastic Chaos Engine]
                              │
                              ▼
                 [Perturbed Target Sandbox]
                              │
                              ▼
                 [Convexity & Fragility Auditor] ──> [Hardened Invariant]""",
                "subsystems": {
                    "Stochastic Chaos Engine": {
                        "role": "Injects network jitter, corrupted RPC messages, and resource starvation during simulation.",
                        "invariant_rule": "Perturbations must be bounded to preserve simulation decidability.",
                    },
                    "Convexity Auditor": {
                        "role": "Measures second derivative of system stability with respect to disturbance magnitude.",
                        "invariant_rule": "Rejects candidates showing brittle, cliff-edge failure modes.",
                    },
                    "Self-Healing Reconfigurer": {
                        "role": "Tests candidate architecture's ability to autonomously re-converge after stress.",
                        "invariant_rule": "Recovery to coherent state must occur within finite simulation depth.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Forces exploration towards robust, decentralized consensus invariants (+0.0130).",
                    "target_e2_velocity": "Unmasks brittle and overfitted candidates in a single perturbation pass (+0.0140).",
                    "target_e3_yield": "Produces structural axioms that operate reliably in Byzantine environments (+0.0110).",
                },
                "tradeoffs": {
                    "strengths": "Guarantees high real-world robustness; eliminates fragile happy-path architectures.",
                    "constraints": "Consumes higher compute token budget per simulation pass due to Monte Carlo noise injection.",
                },
            },
        },
    ),
    Axiom(
        id="L0-008",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Ergodic State Exploration & Measure-Preserving Search Dynamics",
        statement="The hypothesis generation mechanism must operate as an ergodic dynamical system over the manifold of architectural topologies, guaranteeing that time averages of candidate trajectories converge to space averages over reachable configuration space, precluding deadlocks and local attractors.",
        formal_expression=r"\lim_{T \to \infty} \frac{1}{T} \int_0^T f(S_t) dt = \int_{\mathcal{M}} f(s) d\mu(s) \quad \text{where} \quad \mu(\mathcal{M}) = 1",
        operational_rule="Search generators that fall into repetitive topological attractors are penalized with negative exploratory momentum.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Statistical Mechanics & Ergodic Theory (Ludwig Boltzmann & George Birkhoff)",
            "source_principle": "Ergodic Measure-Preserving Trajectory Dynamics",
            "system_profile": {
                "archetype": "Phase-Space Ergodic Trajectory Engine",
                "topology_type": "Manifold Repulsion & State Coverage Dispatcher",
                "topology_diagram": """[Trajectory History Buffer] ──> [Density Manifold Estimator]
                                           │
                                           ▼
                                [Anti-Attractor Repulsor]
                                           │
                                           ▼
                                [Ergodic Generator Dispatch]""",
                "subsystems": {
                    "Density Manifold Estimator": {
                        "role": "Maps past candidate axioms to an abstract topological coordinate manifold.",
                        "invariant_rule": "Maintains a spatial probability density of explored conceptual regions.",
                    },
                    "Anti-Attractor Repulsor": {
                        "role": "Computes repulsive vector fields around dense clusters to push generators away from local minima.",
                        "invariant_rule": "Forces distance metric d(new, history) > threshold.",
                    },
                    "Ergodic Dispatcher": {
                        "role": "Allocates candidate generation quotas across unvisited conceptual quadrants.",
                        "invariant_rule": "Guarantees non-zero sampling probability for all valid mathematical paradigms.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Maximum diversity gain; completely eliminates conceptual clustering and model collapse (+0.0190).",
                    "target_e2_velocity": "Avoids redundant verification of near-identical hypotheses (+0.0080).",
                    "target_e3_yield": "Unearths orthogonal structural paradigms that standard heuristics overlook (+0.0100).",
                },
                "tradeoffs": {
                    "strengths": "Total immunity to mode collapse; broad discovery across unconventional disciplines.",
                    "constraints": "Higher initial variance in candidate compilation success due to radical exploration jumps.",
                },
            },
        },
    ),
    Axiom(
        id="L0-009",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Recursive Meta-Refutation & Heuristic Half-Life Decay",
        statement="Every active epistemic search heuristic must maintain an empirical half-life based on its marginal contribution to structural candidate discovery; heuristics whose rolling yield falls below replacement entropy are dynamically discounted and subjected to recursive meta-refutation.",
        formal_expression=r"\lambda_i(t) = \lambda_0 \exp\left(-\frac{t - t_{\text{last\_yield}}}{\tau}\right) \cdot \mathbb{I}(\Delta E_{\text{marginal}} > 0)",
        operational_rule="Search rules that fail to yield compilable structural axioms within a moving window lose generative priority.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Evolutionary Cybernetics & Epistemic Logic",
            "source_principle": "Dynamic Epistemic Pruning & Meta-Audit",
            "system_profile": {
                "archetype": "Self-Pruning Heuristic Lifecycle Comptroller",
                "topology_type": "Attribution Feedback with Decay Throttles",
                "topology_diagram": """[Active Heuristic Registry] ──> [Yield Attribution Tracker]
                                            │
                                            ▼
                                [Half-Life Decay Engine]
                                            │
                                            ▼
                                [Meta-Refutation Deprecator]""",
                "subsystems": {
                    "Yield Attribution Tracker": {
                        "role": "Traces downstream structural successes back to the guiding epistemic heuristics.",
                        "invariant_rule": "Every committed structural delta updates heuristic credit scores.",
                    },
                    "Half-Life Decay Engine": {
                        "role": "Applies continuous exponential time-decay to inactive heuristic weights.",
                        "invariant_rule": "Heuristics without recent yield suffer monotonic prompt de-weighting.",
                    },
                    "Meta-Refutation Deprecator": {
                        "role": "Permanently prunes stagnant search heuristics from the meta-prompt before Phase 2.",
                        "invariant_rule": "Frees prompt context space for high-performing generators.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Prunes worn-out search directions, keeping prompt context lean and focused (+0.0100).",
                    "target_e2_velocity": "Maintains high refutation throughput by discarding indecisive search rules (+0.0170).",
                    "target_e3_yield": "Maximizes structural yield by allocating compute only to proven generators (+0.0150).",
                },
                "tradeoffs": {
                    "strengths": "Prevents prompt context bloat; actively optimizes the meta-compiler's own cognition.",
                    "constraints": "May prematurely discount slow-burn heuristics if decay parameter tau is set too short.",
                },
            },
        },
    ),
    Axiom(
        id="L0-010",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Constructive Proof Demarcation & Intuitionistic Type Witnessing",
        statement="An architectural invariant cannot be established by mere non-constructive contradiction; every accepted axiom must construct a computable computational witness that realizes the claimed invariant across every admissible system state.",
        formal_expression=r"\vdash A \iff \exists t \; (t : A) \quad \text{where} \quad \neg\neg A \not\implies A",
        operational_rule="Proofs of invariant preservation via law of excluded middle without an explicit executable witness term are rejected.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Constructive Mathematics (L.E.J. Brouwer & Per Martin-Löf)",
            "source_principle": "Curry-Howard Isomorphism & Witness Computability",
            "system_profile": {
                "archetype": "Curry-Howard Realizer & Intuitionistic Witness Compiler",
                "topology_type": "Dependent Type Checking & Term Extraction Pipeline",
                "topology_diagram": """[Invariant Specification] ──> [Intuitionistic Type Checker]
                                           │
                                           ▼
                               [Witness Term Extractor]
                                           │
                                           ▼
                               [Executable Realizer Unit]""",
                "subsystems": {
                    "Intuitionistic Type Checker": {
                        "role": "Treats invariant statements as dependent type propositions in Martin-Löf type theory.",
                        "invariant_rule": "Rejects non-constructive proofs relying on double-negation elimination.",
                    },
                    "Witness Term Extractor": {
                        "role": "Synthesizes an executable lambda-calculus term realizing the type proposition.",
                        "invariant_rule": "Extracted terms must be total and terminate within bounded steps.",
                    },
                    "Executable Realizer Unit": {
                        "role": "Executes witness programs against simulation states to guarantee operational validity.",
                        "invariant_rule": "Type preservation (subject reduction) must hold across state mutations.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Forces candidates into rigorous typed formalisms (+0.0090).",
                    "target_e2_velocity": "Immediately discards non-constructive assertions without simulation (+0.0160).",
                    "target_e3_yield": "Produces structural axioms that are directly compilable with zero ambiguity (+0.0180).",
                },
                "tradeoffs": {
                    "strengths": "Guarantees that every committed axiom has a concrete, executable verification program.",
                    "constraints": "Strict formulation requirement that rejects valid heuristics lacking immediate constructive witnesses.",
                },
            },
        },
    ),
    Axiom(
        id="L0-011",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Shannon Information Gain & Surprisal Gradient Maximization",
        statement="Exploratory search steps must maximize expected Kullback-Leibler divergence from the prior architectural belief state, prioritizing hypotheses that maximize reduction in epistemic entropy over those with high confirmatory probability.",
        formal_expression=r"\Delta I(A; \mathcal{T}) = D_{\text{KL}}(P(S \mid A) \parallel P(S)) > \gamma",
        operational_rule="Candidates that merely confirm existing system behaviors without shifting posterior belief distributions are discarded.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Information Theory (Claude Shannon & Solomon Kullback)",
            "source_principle": "Surprisal Gradient Optimization",
            "system_profile": {
                "archetype": "Surprisal Gradient Maximizer & Information Filter",
                "topology_type": "Bayesian Information Gain Dispatch Loop",
                "topology_diagram": """[Prior Belief Distribution] ──┐
                              ├──> [Mutual Information Gauge] ──> [Gradient Stepper]
[Observed Metric Feedback]  ──┘                                          │
                                                                         ▼
                                                            [High-Surprisal Target Focus]""",
                "subsystems": {
                    "Belief Distribution Tracker": {
                        "role": "Maintains Bayesian priors over candidate efficacy across target domains.",
                        "invariant_rule": "Updates posterior distributions following each simulation run.",
                    },
                    "Mutual Information Gauge": {
                        "role": "Calculates expected information gain I(H; T) for proposed hypotheses.",
                        "invariant_rule": "Penalizes proposals that yield zero variance reduction.",
                    },
                    "Surprisal Gradient Stepper": {
                        "role": "Directs generator prompts toward areas of highest epistemic uncertainty.",
                        "invariant_rule": "Guides exploration along the steepest information gradient.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Biases exploration toward high-entropy, low-probability domains (+0.0180).",
                    "target_e2_velocity": "Rapidly narrows down uncertainty bounds in simulation models (+0.0140).",
                    "target_e3_yield": "Produces high-impact, non-obvious structural breakthroughs (+0.0120).",
                },
                "tradeoffs": {
                    "strengths": "Maximizes learning rate per simulation token spent.",
                    "constraints": "May temporarily accept high-variance hypotheses with higher risk of rejection.",
                },
            },
        },
    ),
    Axiom(
        id="L0-012",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Topological Homology Invariance & Betti Number Preservation",
        statement="System dependency and communication graphs must preserve invariant Betti numbers under architectural transformations, ensuring that component decomposition neither introduces circular deadlock 1-cycles nor disconnects 0-simplex components.",
        formal_expression=r"\beta_k(\mathcal{K}_{\text{compiled}}) = \beta_k(\mathcal{K}_{\text{spec}}) \quad \forall k \ge 0",
        operational_rule="Structural transformations that alter simplicial homology groups or create unchecked 1-cycles are rejected.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Algebraic Topology (Henri Poincaré & Emmy Noether)",
            "source_principle": "Simplicial Homology Invariance",
            "system_profile": {
                "archetype": "Simplicial Complex Auditor & Betti Invariant Guard",
                "topology_type": "Simplicial Triangulation & Homology Analyzer",
                "topology_diagram": """[Component Dependency Graph] ──> [Simplicial Complex Mapper]
                                              │
                                              ▼
                                 [Homology Group Calculator]
                                              │
                                              ▼
                                 [Betti Number Invariant Guard]""",
                "subsystems": {
                    "Simplicial Complex Mapper": {
                        "role": "Converts module dependency networks into geometric simplicial complexes.",
                        "invariant_rule": "N-ary interactions are mapped to (N-1)-simplex faces.",
                    },
                    "Homology Group Calculator": {
                        "role": "Computes Betti numbers: beta_0 (connectivity) and beta_1 (1-cycles / deadlocks).",
                        "invariant_rule": "Detects circular dependency traps via non-zero 1-cycle boundaries.",
                    },
                    "Betti Invariant Guard": {
                        "role": "Ensures topological homology is preserved across compilation transformations.",
                        "invariant_rule": "Rejects any candidate that introduces un-bracketed 1-cycles.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Brings topological data analysis into systems architecture (+0.0140).",
                    "target_e2_velocity": "Mathematically proves absence of circular deadlocks without combinatorial search (+0.0160).",
                    "target_e3_yield": "Guarantees topological stability of generated system modules (+0.0130).",
                },
                "tradeoffs": {
                    "strengths": "Provably prevents circular deadlocks and orphaned subsystems.",
                    "constraints": "Requires graph triangulation compute step during AST verification.",
                },
            },
        },
    ),
    Axiom(
        id="L0-013",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Gödelian Incompleteness Demarcation & Meta-System Ascent",
        statement="When an architectural verification harness encounters an unprovable self-referential invariant within system state S, the compiler must ascend to meta-language M(S) rather than forcing unsound decidability.",
        formal_expression=r"\text{True}_{\mathcal{L}}(S) \not\subseteq \text{Provable}_{\mathcal{L}}(S) \implies \text{Ascend}(\mathcal{L} \to \mathcal{L}^+)",
        operational_rule="Candidates attempting to assert complete self-verification within their own operational calculus are rejected.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Mathematical Logic & Metamathematics (Kurt Gödel & Alfred Tarski)",
            "source_principle": "Tarskian Truth Hierarchy and Undecidability Escalation",
            "system_profile": {
                "archetype": "Tarskian Hierarchy Transceiver & Undecidability Escalator",
                "topology_type": "Stratified Multi-Level Meta-Language Lattice",
                "topology_diagram": """[Base System Calculus L0] ──> [Self-Reference Detector]
                                       │
                                       ▼
                         [Undecidability Demarcator]
                                       │
                                       ▼
                         [Meta-Language Escalator L1] ──> [Sound External Arbiter]""",
                "subsystems": {
                    "Self-Reference Detector": {
                        "role": "Identifies circular self-referential verification loops in component proofs.",
                        "invariant_rule": "Flags statements that assert their own unprovability.",
                    },
                    "Undecidability Demarcator": {
                        "role": "Distinguishes between falsified assertions and formally undecidable invariants.",
                        "invariant_rule": "Halts infinite verification loops when undecidability is detected.",
                    },
                    "Meta-Language Escalator": {
                        "role": "Transfers evaluation authority to higher-order supervisor logic.",
                        "invariant_rule": "Preserves consistency of base calculus by isolating paradoxes.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Encourages tiered, stratified modular architectures (+0.0120).",
                    "target_e2_velocity": "Instantly terminates search loops stuck on undecidable invariant proofs (+0.0170).",
                    "target_e3_yield": "Produces sound, paradox-free architectural compilation specifications (+0.0150).",
                },
                "tradeoffs": {
                    "strengths": "Provably prevents paradoxes and infinite compile-time verification loops.",
                    "constraints": "Requires multi-tiered execution environment with supervisor capabilities.",
                },
            },
        },
    ),
    Axiom(
        id="L0-014",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Ashby's Law of Requisite Variety & Dimensional Match",
        statement="The internal degrees of freedom in an architectural verifier must be greater than or equal to the disturbance variety in target environments (H(V) >= H(E)), ensuring regulatory capacity matches environmental entropy.",
        formal_expression=r"H(\mathcal{V}_{\text{regulator}}) \ge H(\mathcal{E}_{\text{disturbances}}) - H(\mathcal{S}_{\text{goal}})",
        operational_rule="Control and verification mechanisms whose internal state space is smaller than target error manifolds are rejected.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Cybernetics & Systems Control (W. Ross Ashby)",
            "source_principle": "Law of Requisite Variety in Governor Dynamics",
            "system_profile": {
                "archetype": "Requisite Variety Gauge & Invariant Regulator Balancer",
                "topology_type": "Entropy-Matching Dual Channel Regulator",
                "topology_diagram": """[Environmental Disturbance Entropy] ──> [Entropy Match Gauge]
                                                    │
                                                    ▼
                                    [Verifier Variety Expander]
                                                    │
                                                    ▼
                                    [Requisite State Regulator] ──> [Stable System Core]""",
                "subsystems": {
                    "Entropy Match Gauge": {
                        "role": "Computes Shannon entropy of target failure states and environmental inputs.",
                        "invariant_rule": "Rejects verifiers with insufficient state space resolution.",
                    },
                    "Verifier Variety Expander": {
                        "role": "Dynamically scales internal observation channels to match target complexity.",
                        "invariant_rule": "Allocates observation dimensions proportionally to environmental noise.",
                    },
                    "Requisite State Regulator": {
                        "role": "Maintains system goal invariants despite high-dimensional disturbances.",
                        "invariant_rule": "Ensures output variance remains within bounded goal tolerances.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Forces generators to invent high-capacity, expressive architectural governors (+0.0150).",
                    "target_e2_velocity": "Quickly discards overly simplistic controllers that cannot cover system states (+0.0130).",
                    "target_e3_yield": "Guarantees robust operational envelopment for compiled systems (+0.0140).",
                },
                "tradeoffs": {
                    "strengths": "Ensures supervisory mechanisms are never blindsided by unforeseen environmental states.",
                    "constraints": "Increases memory overhead of regulatory and logging subsystems.",
                },
            },
        },
    ),
    Axiom(
        id="L0-015",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Category-Theoretic Adjunction & Galois Connection",
        statement="Specification syntax and compiled runtime semantics must form an adjoint functor pair F -| G such that compilation guarantees universal factorization and bidirectional semantic preservation.",
        formal_expression=r"\text{Hom}_{\mathcal{C}}(F(A), B) \cong \text{Hom}_{\mathcal{D}}(A, G(B))",
        operational_rule="Transformations lacking adjoint right-inverses or failing Galois round-trip closure are pruned.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Category Theory & Abstract Algebra (Daniel Kan & Saunders Mac Lane)",
            "source_principle": "Adjoint Functor Duality and Universal Factorization",
            "system_profile": {
                "archetype": "Free-Forgetful Adjunction Transducer",
                "topology_type": "Bidirectional Natural Isomorphism Pipeline",
                "topology_diagram": """[Specification Domain C] ──(Left Functor F)──> [Runtime Domain D]
               │                                       │
               ▲                                       ▼
        [Unit eta] <──(Right Functor G)── [Counit epsilon]""",
                "subsystems": {
                    "Left Adjoint Functor F": {
                        "role": "Synthesizes free structural implementations from abstract declarative specifications.",
                        "invariant_rule": "Must preserve all colimits and coproducts from category C.",
                    },
                    "Right Adjoint Functor G": {
                        "role": "Extracts forgetful behavioral observations from concrete execution runtimes.",
                        "invariant_rule": "Must preserve all limits and Cartesian products into category D.",
                    },
                    "Adjunction Unit Arbiter": {
                        "role": "Verifies that round-trip transformation satisfies triangular identities.",
                        "invariant_rule": "Unit-counit composition must evaluate to identity morphism.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Connects categorical algebra with practical system compilers (+0.0140).",
                    "target_e2_velocity": "Enables algebraic verification of compilation correctness without simulation (+0.0160).",
                    "target_e3_yield": "Produces highly composable, mathematically sound structural architectures (+0.0160).",
                },
                "tradeoffs": {
                    "strengths": "Provable bidirectional correctness; specifications always match compiled binaries.",
                    "constraints": "Strict category-theoretic constraints limit ad-hoc optimizations.",
                },
            },
        },
    ),
    Axiom(
        id="L0-016",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Landauer's Thermodynamic Principle of Reversible Computation",
        statement="Architectural transformations that discard intermediate computational states must formally account for entropy dissipation, favoring logically reversible morphisms that preserve state reconstructibility.",
        formal_expression=r"\Delta Q \ge k_B T \ln 2 \cdot \Delta H_{\text{erasure}} \implies \text{Prefer}(\text{Isomorphism})",
        operational_rule="Irreversible lossy projections without explicit audit trails or invertibility witnesses are penalized.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Physical Information Theory (Rolf Landauer & Charles Bennett)",
            "source_principle": "Information Erasure Dissipation and Reversible Computing",
            "system_profile": {
                "archetype": "Microstate Conservation & Entropy Dissipation Auditor",
                "topology_type": "Reversible Morphism Pipeline with Conservation Rails",
                "topology_diagram": """[Ingress State S] ──> [Reversible Transformation] ──> [Egress State S']
                                  │                               │
                                  └───> [Information Conservation] ◄──┘
                                                │
                                                ▼
                                    [Audit Lineage Ledger]""",
                "subsystems": {
                    "Reversible Morphism Engine": {
                        "role": "Executes state transformations using bijective mappings.",
                        "invariant_rule": "Every forward step must have a computable backward inverse.",
                    },
                    "Information Conservation Auditor": {
                        "role": "Tracks bit-erasure entropy across pipeline stages.",
                        "invariant_rule": "Penalizes destructive state mutations that destroy history.",
                    },
                    "Audit Lineage Ledger": {
                        "role": "Maintains lightweight reconstructibility markers for state rollbacks.",
                        "invariant_rule": "Guarantees exact past state reconstructibility without full dumps.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Brings thermodynamic physics into software architecture (+0.0130).",
                    "target_e2_velocity": "Enables instant time-travel debugging and zero-cost rollbacks (+0.0150).",
                    "target_e3_yield": "Produces resilient, self-auditing distributed systems (+0.0140).",
                },
                "tradeoffs": {
                    "strengths": "Complete lineage traceability; enables deterministic rollback and replay.",
                    "constraints": "Requires tracking inverse operations or maintaining reversible logs.",
                },
            },
        },
    ),
    Axiom(
        id="L0-017",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Peircean Semiotic Triad & Pragmatic Maxim",
        statement="Module interfaces must decouple representational tokens from physical execution objects through an explicit mediation interpretant, preventing direct token-state semantic coupling.",
        formal_expression=r"\text{Sign}(R, O, I): \; R \xrightarrow{I} O \quad \text{where} \quad R \cap O = \emptyset",
        operational_rule="Direct coupling of internal memory structures to wire formats without an explicit interpretive schema is rejected.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Semiotics & Pragmatism (Charles Sanders Peirce)",
            "source_principle": "Triadic Sign Relation (Representamen-Object-Interpretant)",
            "system_profile": {
                "archetype": "Triadic Semantic Grounding Fabric",
                "topology_type": "Triadic Mediated Interface Bus",
                "topology_diagram": """[Representamen (Token)] ──┐
                              ├──> [Interpretant (Schema / Context)] ──> [Object (Physical State)]
[Environmental Pragmatics] ───┘""",
                "subsystems": {
                    "Representamen Encoder": {
                        "role": "Serializes module intent into syntactic representational tokens.",
                        "invariant_rule": "Tokens must be purely symbolic and free of runtime pointers.",
                    },
                    "Contextual Interpretant": {
                        "role": "Interprets tokens within dynamic context to determine pragmatic meaning.",
                        "invariant_rule": "Mediates all interactions between symbols and memory states.",
                    },
                    "Object State Grounder": {
                        "role": "Applies interpreted actions to underlying physical system state.",
                        "invariant_rule": "Rejects malformed interpretations before state mutation.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Encourages schema-driven, loosely coupled protocols (+0.0130).",
                    "target_e2_velocity": "Quickly detects protocol drift and semantic mismatches (+0.0140).",
                    "target_e3_yield": "Produces evolvable, backward-compatible API architectures (+0.0150).",
                },
                "tradeoffs": {
                    "strengths": "Total decoupling of serialization format from internal data structures.",
                    "constraints": "Adds interpretant mediation step to inter-module communications.",
                },
            },
        },
    ),
    Axiom(
        id="L0-018",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Spinozan Substance Monism & Attribute Parallelism",
        statement="System state is fundamentally unified under one immutable substrate; operational views (control flow, data flow, telemetry) are pure orthogonal attribute projections over that single substance.",
        formal_expression=r"\mathcal{S} = \text{Substance} \quad \land \quad \text{View}_k = \pi_k(\mathcal{S}) \quad \text{where} \quad \pi_i \perp \pi_j",
        operational_rule="Independent disparate state storage systems that lack canonical single-source synchronization are rejected.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Rationalist Metaphysics (Baruch Spinoza)",
            "source_principle": "Substance Monism and Dual-Aspect Parallelism",
            "system_profile": {
                "archetype": "Unified Substance Monad with Orthogonal Projections",
                "topology_type": "Monistic Central Kernel with Stratified Attribute Projections",
                "topology_diagram": """              ┌──> [Projection 1: Execution Flow]
              │
[Single Substance Monad] ──┼──> [Projection 2: Memory Graph]
              │
              └──> [Projection 3: Telemetry Stream]""",
                "subsystems": {
                    "Substance Monad Kernel": {
                        "role": "Maintains the singular, authoritative ontological state of the architecture.",
                        "invariant_rule": "All mutations must resolve within the primary monad.",
                    },
                    "Attribute Projection Fabric": {
                        "role": "Computes pure functional views for execution, debugging, and persistence.",
                        "invariant_rule": "Projections are read-only and cannot mutate underlying substance.",
                    },
                    "Parallelism Synchronizer": {
                        "role": "Guarantees instantaneous consistency across all operational attribute views.",
                        "invariant_rule": "State skew between projections is strictly forbidden.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Promotes monistic, single-source-of-truth architectures (+0.0120).",
                    "target_e2_velocity": "Eliminates cache coherence bugs and split-brain states (+0.0160).",
                    "target_e3_yield": "Produces clean, highly unified system architectures (+0.0150).",
                },
                "tradeoffs": {
                    "strengths": "Completely eliminates synchronization discrepancies and split-brain scenarios.",
                    "constraints": "High performance requirements on the central substance monad.",
                },
            },
        },
    ),
    Axiom(
        id="L0-019",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Leibniz's Identity of Indiscernibles & Bisimulation",
        statement="Subsystems exhibiting identical observational behaviors across all operational contexts must be unified into a single canonical AST representation, eliminating superficial syntactical duplication.",
        formal_expression=r"\forall x, y \; (\forall P \; (P(x) \leftrightarrow P(y)) \implies x = y)",
        operational_rule="Components that are observationally bisimilar but syntactically separated are collapsed into single canonical primitives.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Philosophical Logic & Ontology (Gottfried Wilhelm Leibniz)",
            "source_principle": "Principium Identitatis Indiscernibilium and Bisimulation",
            "system_profile": {
                "archetype": "Bisimulation Extensionality Canonicalizer",
                "topology_type": "Observational Equivalence Deduplication Pipeline",
                "topology_diagram": """[Subsystem A] ──┐
                 ├──> [Bisimulation Game Engine] ──> [Equivalence Quotient]
[Subsystem B] ──┘                                           │
                                                            ▼
                                                [Canonical Unified Module]""",
                "subsystems": {
                    "Bisimulation Game Engine": {
                        "role": "Tests behavioral equivalence across all admissible input sequences.",
                        "invariant_rule": "Simulates step-by-step state matching between components.",
                    },
                    "Equivalence Quotient Collapser": {
                        "role": "Replaces observationally identical modules with a single shared instance.",
                        "invariant_rule": "Guarantees zero divergence in compiled system outputs.",
                    },
                    "Indiscernibility Invariant Guard": {
                        "role": "Prevents redundant re-implementation of existing subsystem capabilities.",
                        "invariant_rule": "Rejects proposals that merely re-skin existing functions.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Forces generators to invent genuinely novel behaviors (+0.0140).",
                    "target_e2_velocity": "Quickly identifies duplicate proposals across epochs (+0.0150).",
                    "target_e3_yield": "Yields ultra-compact, canonical system implementations (+0.0160).",
                },
                "tradeoffs": {
                    "strengths": "Drastically reduces codebase bloat and maintenance surface.",
                    "constraints": "Bisimulation checking is computationally intensive for complex state machines.",
                },
            },
        },
    ),
    Axiom(
        id="L0-020",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Active Inference & Variational Free Energy Minimization",
        statement="Subsystems must maintain generative models of their interface environments, executing state transitions that minimize variational free energy (divergence between anticipated and observed messages).",
        formal_expression=r"\mathcal{F} = \mathbb{E}_{q}[\ln q(s) - \ln p(o, s)] \ge -\ln p(o) \implies \min \mathcal{F}",
        operational_rule="Passive reactive modules lacking internal predictive models are deprecated in favor of active inference agents.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Theoretical Neuroscience & Statistical Physics (Karl Friston)",
            "source_principle": "Free Energy Principle and Markov Blankets",
            "system_profile": {
                "archetype": "Generative Predictive State Filter & Active Invariant Regulator",
                "topology_type": "Markov Blanket Predictive Feedback Loop",
                "topology_diagram": """[Internal Generative Model] ──> [Top-Down Prediction]
                                            │
                                            ▼
[External Ingress Stream]  ──> [Sensory Markov Blanket] ──> [Prediction Error (Free Energy)]
                                                                    │
                                                                    ▼
                                                        [Active State Transition]""",
                "subsystems": {
                    "Internal Generative Model": {
                        "role": "Maintains probabilistic expectations of future environmental messages.",
                        "invariant_rule": "Continuously updates prior distributions using sensory feedback.",
                    },
                    "Sensory Markov Blanket": {
                        "role": "Isolates internal states from external perturbations via formal boundary.",
                        "invariant_rule": "Information exchange must pass exclusively through blanket states.",
                    },
                    "Free Energy Minimizer": {
                        "role": "Executes actions that resolve sensory prediction errors.",
                        "invariant_rule": "Minimizes variational upper bound on surprisal.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Introduces predictive cybernetics to distributed software (+0.0150).",
                    "target_e2_velocity": "Predicts component failures before RPC timeouts occur (+0.0160).",
                    "target_e3_yield": "Produces self-optimizing, adaptive system architectures (+0.0150).",
                },
                "tradeoffs": {
                    "strengths": "Anticipates traffic spikes and faults proactively rather than reactively.",
                    "constraints": "Requires internal model maintenance and probabilistic inference compute.",
                },
            },
        },
    ),
    Axiom(
        id="L0-021",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Quantum Superposition Demarcation & Decoherence Measurement",
        statement="Exploratory candidate trajectories may evolve in superposition across multiple parallel topologies until explicit measurement against target invariants collapses the wavefunction into stable pointer states.",
        formal_expression=r"|\Psi\rangle = \sum_i c_i |S_i\rangle \xrightarrow{\text{Measure}(\mathcal{T})} |S_{\text{pointer}}\rangle",
        operational_rule="Premature pruning of non-orthogonal architectural states before target interaction is prohibited.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Quantum Foundations (John von Neumann & Wojciech Zurek)",
            "source_principle": "Environmental Decoherence and Pointer State Selection",
            "system_profile": {
                "archetype": "Quantum Branch Evaluator & Decoherence Filter",
                "topology_type": "Multi-Path Superposition Lattice with Measurement Collapser",
                "topology_diagram": """[Candidate Inception] ──> [Superposition Branch Forker]
                                         │
                                         ├── Branch A (|S1>)
                                         ├── Branch B (|S2>)
                                         └── Branch C (|S3>)
                                         │
                                         ▼
                               [Target Invariant Measurement] ──> [Collapsed Pointer State]""",
                "subsystems": {
                    "Superposition Branch Forker": {
                        "role": "Maintains multiple competing architectural configurations concurrently.",
                        "invariant_rule": "Branches remain in parallel exploration without cross-talk.",
                    },
                    "Decoherence Target Harness": {
                        "role": "Simulates environmental interaction with validation targets.",
                        "invariant_rule": "Measurement must project states onto orthogonal basis vectors.",
                    },
                    "Pointer State Selector": {
                        "role": "Selects the most robust, environmentally stable configuration post-measurement.",
                        "invariant_rule": "Rejects states that exhibit high entanglement-induced fragility.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Maximizes breadth of concurrent exploratory paths (+0.0170).",
                    "target_e2_velocity": "Evaluates multiple topological variants in a single pass (+0.0130).",
                    "target_e3_yield": "Discovers non-intuitive optimal architectures through interference (+0.0140).",
                },
                "tradeoffs": {
                    "strengths": "Avoids premature commitment to sub-optimal local designs.",
                    "constraints": "Higher compute footprint to track multiple parallel branches.",
                },
            },
        },
    ),
    Axiom(
        id="L0-022",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Quinean Naturalized Epistemology & Web of Belief",
        statement="No single empirical simulation failure refutes an axiom in isolation; verification recalibrates the entire interdependent web of invariants, shielding axiomatic core principles before modifying peripheral boundary conditions.",
        formal_expression=r"\Delta \mathcal{W} = \arg\min_{\Delta} \left( \|\Delta\|_{\text{min}} \right) \quad \text{s.t.} \quad \mathcal{W} \cup \{E\} \not\vdash \bot",
        operational_rule="Core systemic axioms may not be discarded due to peripheral test harness failures without exhaustive boundary audit.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Philosophy of Language (W.V.O. Quine)",
            "source_principle": "Holism and Underdetermination of Theory by Data",
            "system_profile": {
                "archetype": "Holism Recalibration Web & Core-Periphery Differentiator",
                "topology_type": "Concentric Dependency Network with Radial Recalibration",
                "topology_diagram": """[Simulation Failure Event] ──> [Periphery Adapter Audit]
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                     ▼
         [Peripheral Rule Adjustment]           [Core Axiomatic Re-Evaluation]
         (High Flexibility / Low Cost)          (Extreme Reluctance / High Cost)""",
                "subsystems": {
                    "Core-Periphery Radial Classifier": {
                        "role": "Assigns epistemic centrality scores to all active architectural invariants.",
                        "invariant_rule": "Fundamental compositional rules receive maximum protection.",
                    },
                    "Web Recalibration Solver": {
                        "role": "Finds the minimal modification to the overall invariant web that resolves contradictions.",
                        "invariant_rule": "Maximizes conservative preservation of existing verified beliefs.",
                    },
                    "Boundary Condition Tuner": {
                        "role": "Adjusts peripheral interface assumptions before considering core invariant deprecation.",
                        "invariant_rule": "Shields foundation axioms from noisy localized test anomalies.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Stabilizes research progress against spurious test fluctuations (+0.0110).",
                    "target_e2_velocity": "Quickly identifies whether failures are fundamental or superficial (+0.0150).",
                    "target_e3_yield": "Protects foundational structural gains from regression (+0.0170).",
                },
                "tradeoffs": {
                    "strengths": "Prevents catastrophic discarding of good foundational ideas due to minor bugs.",
                    "constraints": "May tolerate flawed core ideas longer if periphery is continually adjusted.",
                },
            },
        },
    ),
    Axiom(
        id="L0-023",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Whiteheadian Process Philosophy & Actual Occasions",
        statement="Systems are fundamentally composed of transient temporal events (actual occasions) rather than static substances; state persistence is an emergent trajectory of serial concrescence.",
        formal_expression=r"\mathcal{S}(t) = \bigoplus_{i=1}^k \text{Concrescence}(e_i) \quad \text{where} \quad e_i \in \text{Occasions}",
        operational_rule="Static state objects without discrete event lineage or explicit prehension transitions are prohibited.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Process Philosophy & Metaphysics (Alfred North Whitehead)",
            "source_principle": "Concrescence of Actual Entities and Prehensive Unification",
            "system_profile": {
                "archetype": "Epochal Concrescence Engine & Event Process Graph",
                "topology_type": "Directed Acyclic Prehension Mesh",
                "topology_diagram": """[Past Actual Occasions] ──(Prehension)──> [Concrescence Ingest]
                                                    │
                                                    ▼
                                    [Novel Event Integration]
                                                    │
                                                    ▼
                                    [Objectified New Occasion] ──> [Next Horizon]""",
                "subsystems": {
                    "Prehension Collector": {
                        "role": "Gathers causal effects from completed historical occasions.",
                        "invariant_rule": "Must respect partial ordering of the causal spacetime graph.",
                    },
                    "Concrescence Engine": {
                        "role": "Fuses multiple historical influences into a singular atomic event.",
                        "invariant_rule": "Atomic occasions execute with total indivisibility.",
                    },
                    "Process Horizon Emitter": {
                        "role": "Objectifies new occasions into immutable historical anchors for future processes.",
                        "invariant_rule": "Completed occasions can never be altered or retroactively erased.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Encourages pure event-sourced and stream-processing paradigms (+0.0150).",
                    "target_e2_velocity": "Enables completely decoupled, asynchronous state evolution (+0.0140).",
                    "target_e3_yield": "Produces highly concurrent, race-condition-free structural systems (+0.0160).",
                },
                "tradeoffs": {
                    "strengths": "Immune to race conditions and mutable state locking; natural event sourcing.",
                    "constraints": "High event volume requires efficient log compaction and snapshotting.",
                },
            },
        },
    ),
    Axiom(
        id="L0-024",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Carnapian Logical Syntax & Tolerance Principle",
        statement="The compiler must not impose a single universal meta-logic; system components may define arbitrary internal logical calculi as long as their transformation rules into boundary syntaxes are fully formalized.",
        formal_expression=r"\forall \mathcal{L}_i, \mathcal{L}_j: \; \exists \tau_{ij}: \mathcal{L}_i \to \mathcal{L}_j \implies \text{Admissible}(\mathcal{L}_i)",
        operational_rule="Dogmatic rejection of alternative DSLs or component type systems without formal translation analysis is prohibited.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Logical Positivism & Syntax of Language (Rudolf Carnap)",
            "source_principle": "Principle of Tolerance in Formal Languages",
            "system_profile": {
                "archetype": "Multi-Syntactic Framework Transcompiler",
                "topology_type": "Polyglot Language Calculus Interoperability Matrix",
                "topology_diagram": """[Component Dialect L_A] ──┐
                             ├──> [Formal Syntax Transformation Engine] ──> [Boundary Standard]
[Component Dialect L_B] ──┘""",
                "subsystems": {
                    "Syntax Specification Ingest": {
                        "role": "Accepts arbitrary context-free or dependent formal grammars for submodules.",
                        "invariant_rule": "Grammar transformation rules must be mathematically sound.",
                    },
                    "Syntax Translation Matrix": {
                        "role": "Compiles cross-language morphisms between disparate subsystem logics.",
                        "invariant_rule": "Preserves operational semantics across syntactic translations.",
                    },
                    "Tolerance Verifier": {
                        "role": "Validates that heterogeneous logics interact through clean formal boundaries.",
                        "invariant_rule": "Prevents logical inconsistencies from crossing module fences.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Permits extreme diversity of sub-domain specialized architectures (+0.0180).",
                    "target_e2_velocity": "Avoids religious syntax debates by accepting all formally translatable calculi (+0.0120).",
                    "target_e3_yield": "Enables polyglot systems that use optimal paradigms per subsystem (+0.0150).",
                },
                "tradeoffs": {
                    "strengths": "Allows each subsystem to use the domain language best suited to its requirements.",
                    "constraints": "Translation matrix introduces interface marshalling and proof checking overhead.",
                },
            },
        },
    ),
    Axiom(
        id="L0-025",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Prigogine's Dissipative Structures & Far-From-Equilibrium Order",
        statement="Architectures operating under high-throughput input fluxes must maintain dissipative boundary channels to spontaneously generate macro-level self-organizing structural order.",
        formal_expression=r"\frac{dS_{\text{int}}}{dt} = \frac{d_e S}{dt} + \frac{d_i S}{dt} \quad \text{where} \quad \frac{d_e S}{dt} < 0 \implies \text{Order}",
        operational_rule="Static closed systems that attempt to maintain order without continuous external entropy export are rejected.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Non-Equilibrium Thermodynamics (Ilya Prigogine)",
            "source_principle": "Self-Organization through Dissipative Structures",
            "system_profile": {
                "archetype": "Non-Equilibrium Self-Organizing Mesh",
                "topology_type": "Flux-Driven Open System with Dissipative Outlets",
                "topology_diagram": """[High-Volume Input Flux] ──> [Non-Equilibrium Core] ──> [Self-Organizing Topology]
                                            │
                                            ▼
                                [Entropy Dissipation Channel]""",
                "subsystems": {
                    "Input Flux Controller": {
                        "role": "Regulates arrival of external workloads to keep system far from equilibrium.",
                        "invariant_rule": "Prevents stagnant equilibrium states that degrade dynamic throughput.",
                    },
                    "Self-Organizing Arbiter": {
                        "role": "Autonomously dynamically rearranges subsystem routing under high load.",
                        "invariant_rule": "Forms macro-level execution structures that minimize internal friction.",
                    },
                    "Entropy Dissipation Channel": {
                        "role": "Continuously offloads stale caches, dead connections, and telemetry noise.",
                        "invariant_rule": "Exported entropy rate must exceed internal entropy production.",
                    },
                },
                "target_behaviors": {
                    "target_e1_diversity": "Drives architecture toward open, highly dynamic streaming systems (+0.0160).",
                    "target_e2_velocity": "Maintains low latency under extreme traffic peaks (+0.0140).",
                    "target_e3_yield": "Produces self-balancing systems that thrive on continuous high throughput (+0.0150).",
                },
                "tradeoffs": {
                    "strengths": "Maintains high order and throughput under extreme operational stress.",
                    "constraints": "Sub-optimal for quiet systems with near-zero throughput (requires flux to self-organize).",
                },
            },
        },
    ),
]


# =====================================================================
# LEVEL 1: STRUCTURAL CANDIDATE POOL (Physical Systems Design)
# =====================================================================
LEVEL_1_STRUCTURAL_CANDIDATE_POOL: List[Axiom] = [
    Axiom(
        id="L1-001",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Deterministic State Transitions and Immutability",
        statement="Every architectural state modification must occur via pure deterministic transitions operating over immutable snapshots, prohibiting in-place mutation and hidden side-effects.",
        formal_expression=r"S_{t+1} = \delta(S_t, a) \quad \text{where} \quad S_t \cap S_{t+1} = \emptyset",
        operational_rule="State mutations without complete lineage and snapshot isolation are rejected by the compiler.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Mathematical Constructivism",
            "source_principle": "Temporal Immutability",
            "system_profile": {
                "archetype": "Immutable Snapshot Transition Engine",
                "topology_type": "Persistent Data Structure with Append-Only Event Log",
                "topology_diagram": """[Action Request a] ──┐
                         ├──> [Deterministic Reducer delta] ──> [New Immutable Snapshot S_t+1]
[Current Snapshot S_t] ──┘                                        │
                                                                  ▼
                                                      [Persistent Hash-Trie Storage]""",
                "subsystems": {
                    "Pure Reducer Dispatcher": {
                        "role": "Executes state transitions as mathematical functions delta(S, a).",
                        "invariant_rule": "Prohibits in-place mutation and external I/O inside transition body.",
                    },
                    "Persistent Hash-Trie Memory": {
                        "role": "Maintains structural sharing across historical snapshots.",
                        "invariant_rule": "Memory buffers for S_t are permanently marked read-only.",
                    },
                    "Deterministic Lineage Logger": {
                        "role": "Records cryptographic lineage hashes of every transition.",
                        "invariant_rule": "Replays must yield bit-identical snapshots.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Eliminates side-effects in recursive self-compilation (+0.0080).",
                    "target_2_self_evaluator": "Enables zero-cost state rewind and auditing across epoch boundaries (+0.0070).",
                    "target_3_control_group": "Provides clean distributed consensus without lock contention (+0.0110).",
                },
                "tradeoffs": {
                    "strengths": "Guarantees deterministic replayability; eliminates concurrent race conditions.",
                    "constraints": "Structural sharing adds minor memory indirection overhead.",
                },
            },
        },
    ),
    Axiom(
        id="L1-002",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Functorial State Evolution & Morphism Preservation",
        statement="Every architectural state transformation must operate as a structure-preserving functor across subsystem categories, guaranteeing that component composition in the problem domain is preserved under compilation into execution morphisms.",
        formal_expression=r"\mathcal{F}(f \circ g) = \mathcal{F}(f) \circ \mathcal{F}(g) \quad \land \quad \mathcal{F}(\text{id}_A) = \text{id}_{\mathcal{F}(A)}",
        operational_rule="State transitions that violate functorial morphism preservation across subcomponents are rejected at compile time.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Applied Category Theory",
            "source_principle": "Functorial Compositionality",
            "system_profile": {
                "archetype": "Category-Theoretic Functorial State Bus",
                "topology_type": "Morphism Preservation Category Network",
                "topology_diagram": """[Category C: Domain Objects] ──> [Functor F] ──> [Category D: Compiled Morphisms]
               │                                                    │
      Composition f o g                                   Preserved F(f) o F(g)
               │                                                    │
               ▼                                                    ▼
      [Domain Verification]                               [Execution Engine Runtime]""",
                "subsystems": {
                    "Functorial Mapping Layer": {
                        "role": "Maps domain-level component compositions directly into execution morphisms.",
                        "invariant_rule": "F(f o g) = F(f) o F(g) must be verified at compile time.",
                    },
                    "Identity Morphism Guard": {
                        "role": "Guarantees that null operations preserve identity across subsystem interfaces.",
                        "invariant_rule": "F(id_A) = id_F(A) must hold without side-effects.",
                    },
                    "Category Type Verifier": {
                        "role": "Checks that objects and morphisms form valid categories with associative composition.",
                        "invariant_rule": "Rejects non-composable subsystem boundaries.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Guarantees modular engine compilation without non-compositional side effects (+0.0100).",
                    "target_2_self_evaluator": "Provides mathematical proofs of telemetry preservation across layers (+0.0075).",
                    "target_3_control_group": "Preserves state consistency across distributed Byzantine nodes (+0.0120).",
                },
                "tradeoffs": {
                    "strengths": "Rigorous composability guarantees; mathematical proof of cross-subsystem correctness.",
                    "constraints": "Requires all component interfaces to be formalized as strict categories.",
                },
            },
        },
    ),
    Axiom(
        id="L1-003",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Linear Resource Ownership and The No-Cloning Invariant",
        statement="Every discrete capability, mutable memory buffer, or execution token must obey affine/linear type invariants; resources cannot be implicitly cloned or duplicated across concurrent processes, only transferred or consumed.",
        formal_expression=r"\mathcal{U}(\rho \otimes \sigma) \neq \rho \otimes \rho \quad \forall \rho \quad (\text{No-Cloning Invariant})",
        operational_rule="Subsystems attempting implicit cloning or aliasing of uncommitted resource tokens without explicit affine handoff trigger immediate compilation failure.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Quantum Information Theory",
            "source_principle": "Wootters-Zurek No-Cloning Theorem",
            "system_profile": {
                "archetype": "Affine Linear Resource Ownership System",
                "topology_type": "Directed Transfer Token Pipeline",
                "topology_diagram": """[Resource Producer] ──> [Linear Capability Token]
                                     │
                     ┌───────────────┴───────────────┐
                     ▼                               ▼
       [Exclusive Move / Handoff]        [Explicit Consume / Drop]
                     │                               │
                     ▼                               ▼
            [Destination Worker]             [Reclaimed Heap Buffer]""",
                "subsystems": {
                    "Affine Ownership Checker": {
                        "role": "Static compiler pass tracking capability token provenance and ownership lifetimes.",
                        "invariant_rule": "Prohibits shared mutable references; only single owners permitted.",
                    },
                    "Move Semantics Hand-off Bus": {
                        "role": "Facilitates zero-copy transfer of execution tokens across concurrent processes.",
                        "invariant_rule": "Transferring a token invalidates the sender's access capability.",
                    },
                    "Deterministic Drop Destructor": {
                        "role": "Automatically cleans up unconsumed resources at scope exit without garbage collection.",
                        "invariant_rule": "Every allocated token must be moved or dropped exactly once.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Prevents memory leaks and duplicate execution in self-compilation (+0.0080).",
                    "target_2_self_evaluator": "Guarantees telemetry packets are processed exactly once (+0.0060).",
                    "target_3_control_group": "Eliminates double-spend and duplicate message attacks in consensus (+0.0096).",
                },
                "tradeoffs": {
                    "strengths": "Zero-cost memory safety without GC pauses; prevents data races by construction.",
                    "constraints": "Strict ownership hierarchy requires deliberate explicit borrowing design.",
                },
            },
        },
    ),
    Axiom(
        id="L1-004",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Universal Grammar & Compositional Projection Constraints",
        statement="Every inter-module communication payload must conform to an invariant deep syntactic structure whose transformational projections into target representations preserve semantic well-formedness.",
        formal_expression=r"\mathcal{P}_{\text{surface}}(\mathcal{D}_{\text{deep}}) \equiv \mathcal{D}_{\text{deep}} \pmod{\text{Transform}}",
        operational_rule="Data mutations or messages that cannot be projected from an unambiguous deep grammar AST are rejected by target compilers.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Theoretical Linguistics / Generative Syntax",
            "source_principle": "Transformational Generative Grammar",
            "system_profile": {
                "archetype": "Universal Grammar AST Deep Projection Compiler",
                "topology_type": "Deep Syntax AST with Invariant Surface Projections",
                "topology_diagram": """[Module Communication] ──> [Deep Grammar AST Parser]
                                       │
                        ┌──────────────┴──────────────┐
                        ▼                             ▼
           [Projection Engine (Protobuf)]    [Projection Engine (JSON/REST)]
                        │                             │
                        └──────────────┬──────────────┘
                                       ▼
                       [Semantic Well-Formedness Guard]""",
                "subsystems": {
                    "Deep Syntax Validator": {
                        "role": "Parses all inter-module RPC payloads into a canonical deep-structure abstract syntax tree.",
                        "invariant_rule": "Rejects malformed messages prior to dispatch.",
                    },
                    "Transformational Projection Engine": {
                        "role": "Projects deep syntax ASTs into surface-level serialization formats without semantic loss.",
                        "invariant_rule": "Bidirectional round-trip isomorphism must hold.",
                    },
                    "Well-Formedness Guard": {
                        "role": "Verifies that received payloads comply with cross-module grammar agreements.",
                        "invariant_rule": "Payloads failing grammatical projection trigger compile-time rejection.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Ensures internal compiler ASTs maintain semantic consistency (+0.0080).",
                    "target_2_self_evaluator": "Standardizes telemetry stream formatting across heterogeneous observers (+0.0060).",
                    "target_3_control_group": "Prevents malformed Byzantine message attacks via strict grammar verification (+0.0144).",
                },
                "tradeoffs": {
                    "strengths": "Eliminates serialization bugs and interface mismatch; provides universal schema validation.",
                    "constraints": "Adds parsing and schema validation step to payload ingest pipeline.",
                },
            },
        },
    ),
    Axiom(
        id="L1-005",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Phenomenological Horizon & Intentional Bracketing (Epoché)",
        statement="Speculative execution modules must establish explicit intentional horizons, bracketing internal transient states until external observation boundaries are reached, preventing premature commitment of speculative paths.",
        formal_expression=r"\mathcal{H}(S_t) = \text{Bracket}(\mathcal{I}_{\text{speculative}}) \implies \partial S_t \cap \mathcal{E}_{\text{ext}} = \emptyset",
        operational_rule="Speculative internal mutations must remain bracketed within intentional horizons and are prohibited from escaping to global observation streams before epoch reconciliation.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Phenomenological Philosophy",
            "source_principle": "Husserlian Epoché & Intentionality",
            "system_profile": {
                "archetype": "Intentional Horizon Speculative Isolation Sandbox",
                "topology_type": "Bracketed Epoche Sandbox with Observation Barrier",
                "topology_diagram": """[Speculative Task] ──> [Bracketed Execution Horizon]
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
       [Transient State Sandbox]         [Epoch Reconciliation Barrier]
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
                     [Global Observable State Stream]""",
                "subsystems": {
                    "Intentional Bracketing Chamber": {
                        "role": "Isolates speculative state mutations within an unobserved execution horizon.",
                        "invariant_rule": "Prohibits leakage of speculative mutations to external processes.",
                    },
                    "Epoch Reconciliation Barrier": {
                        "role": "Synchronizes and commits speculative states only upon verification completion.",
                        "invariant_rule": "Failed speculative branches are discarded with zero trace.",
                    },
                    "Observation Horizon Firewall": {
                        "role": "Prevents external observers from viewing intermediate uncommitted states.",
                        "invariant_rule": "Guarantees atomic visibility of speculative batches.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Enables safe speculative compilation paths without contaminating master state (+0.0060).",
                    "target_2_self_evaluator": "Prevents premature telemetry emissions from uncommitted branches (+0.0060).",
                    "target_3_control_group": "Provides clean speculative execution in Byzantine state machine replication (+0.0096).",
                },
                "tradeoffs": {
                    "strengths": "Allows highly aggressive speculative execution without roll-back side effects.",
                    "constraints": "Requires temporary memory buffering for bracketed state branches.",
                },
            },
        },
    ),
    Axiom(
        id="L1-006",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Homeostatic Equilibrium & Negative Feedback Homeorhesis",
        statement="Subsystem resource allocation and concurrency limits must maintain dynamic homeostatic equilibrium through self-regulating negative feedback loops, preventing runaway cascading thrashing under contention.",
        formal_expression=r"\frac{d\mathcal{R}_i}{dt} = -\kappa (\mathcal{R}_i - \mathcal{R}_{\text{target}}) + \eta(t)",
        operational_rule="Subsystems lacking negative feedback damping when approaching saturation are throttled and re-balanced at compile time.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Theoretical Evolutionary Biology & Cybernetics",
            "source_principle": "Homeostatic Self-Regulation",
            "system_profile": {
                "archetype": "Negative-Feedback Homeostatic Controller",
                "topology_type": "Continuous Proportional-Integral Concurrency Regulator",
                "topology_diagram": """[Load & Contention Sensors] ──> [Error Detector (R - R_target)]
                                             │
                                             ▼
                               [Negative Feedback Damping Unit]
                                             │
                                             ▼
                               [Dynamic Resource Allocator] ──> [Stabilized Subsystems]""",
                "subsystems": {
                    "Contention Sensor Array": {
                        "role": "Monitors queue lengths, CPU utilization, and memory pressure across subsystems.",
                        "invariant_rule": "Emits telemetry at high-frequency intervals.",
                    },
                    "Negative Feedback Damping Unit": {
                        "role": "Applies proportional-integral braking to runaway thread pools and memory allocations.",
                        "invariant_rule": "Damping coefficient kappa must guarantee asymptotic stability.",
                    },
                    "Dynamic Resource Balancer": {
                        "role": "Reallocates execution tokens from idle subsystems to bottlenecked stages.",
                        "invariant_rule": "Prevents starvation and priority inversion.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Stabilizes engine self-compilation under restricted token budgets (+0.0070).",
                    "target_2_self_evaluator": "Prevents telemetry buffer overflow during peak evaluation load (+0.0065).",
                    "target_3_control_group": "Prevents cascading failures in congested distributed state machines (+0.0115).",
                },
                "tradeoffs": {
                    "strengths": "Prevents catastrophic system collapse under extreme overload; auto-tunes concurrency.",
                    "constraints": "Adds slight measurement overhead for continuous sensor telemetry.",
                },
            },
        },
    ),
    Axiom(
        id="L1-007",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Sheaf-Theoretic Local-to-Global Consistency",
        statement="Global architectural state must be computable strictly via gluing mutually compatible local section evaluations over an open cover of subsystem domains.",
        formal_expression=r"\mathcal{F}\left(\bigcup U_i\right) \cong \varprojlim \mathcal{F}(U_i)",
        operational_rule="State transitions lacking pairwise cocycle consistency on overlapping subsystem interfaces cannot be glued into global state.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Topos Theory / Sheaf Theory",
            "source_principle": "Sheaf Gluing Axiom",
            "system_profile": {
                "archetype": "Sheaf-Theoretic Local-to-Global State Glue Engine",
                "topology_type": "Open Cover Subsystem Mesh with Cocycle Verification",
                "topology_diagram": """[Local Sections F(U_i)] ──> [Pairwise Overlap Auditor F(U_i ∩ U_j)]
                                             │
                                             ▼
                                [Cocycle Consistency Verifier]
                                             │
                                             ▼
                                [Global Sheaf Colimit Glue] ──> [Unified Global State]""",
                "subsystems": {
                    "Local Section Evaluator": {
                        "role": "Computes local state transitions within isolated subdomains U_i.",
                        "invariant_rule": "Local evaluations are completely decoupled from remote subsystems.",
                    },
                    "Overlap Cocycle Auditor": {
                        "role": "Verifies pairwise consistency on intersections U_i ∩ U_j.",
                        "invariant_rule": "Transitions that disagree on shared interfaces are rejected.",
                    },
                    "Colimit Gluing Synthesizer": {
                        "role": "Glues mutually compatible local sections into a single global system state.",
                        "invariant_rule": "Global state cannot exist without local pairwise agreement.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Enables completely distributed compilation of engine sub-modules (+0.0090).",
                    "target_2_self_evaluator": "Allows local telemetry aggregation without requiring global lock locks (+0.0070).",
                    "target_3_control_group": "Solves distributed state synchronization with zero central coordination (+0.0130).",
                },
                "tradeoffs": {
                    "strengths": "Enables massive parallel scaling; local verification guarantees global correctness.",
                    "constraints": "Intersection verification requires formal definition of subsystem overlaps.",
                },
            },
        },
    ),
    Axiom(
        id="L1-008",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Landauer Thermodynamic Reversibility & Erasure Dissipation Accounting",
        statement="Every lossy state transformation that discards intermediate execution bits must formally account for entropy dissipation, enforcing logically reversible morphisms for all core state kernels.",
        formal_expression=r"\Delta Q \ge k_B T \ln 2 \cdot \Delta H_{\text{erasure}} \implies \text{Isomorphic}(\text{Kernel})",
        operational_rule="State mutations discarding intermediate histories without explicit dissipation audit channels or reversible inverse paths trigger compiler failure.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Physical Information Theory (Rolf Landauer)",
            "source_principle": "Information Erasure Dissipation & Reversible Computing (Derived from L0-016/L0-022)",
            "system_profile": {
                "archetype": "Reversible Morphism Pipeline with Conservation Rails",
                "topology_type": "Logically Reversible Morphism Mesh with Dissipation Sinks",
                "topology_diagram": """[Ingress State S] ──> [Reversible Transition delta] ──> [Egress State S']
                  │                                         │
                  └───> [Conservation Audit Ledger] ◄───────┘
                                       │
                                       ▼
                          [Entropy Dissipation Sink]""",
                "subsystems": {
                    "Reversible Morphism Kernel": {
                        "role": "Executes bijective transformations where each forward state transition has a computable backward inverse.",
                        "invariant_rule": "delta^-1(delta(S)) = S must hold without state loss.",
                    },
                    "Entropy Dissipation Sink": {
                        "role": "Explicitly buffers and audits all discarded microstate bits at module boundaries.",
                        "invariant_rule": "Bit-erasure events must log minimal thermodynamic accounting traces.",
                    },
                    "Microstate Invertibility Verifier": {
                        "role": "Proves that critical transaction histories can be rewound without relying on external snapshots.",
                        "invariant_rule": "Irreversible side-effects inside core reducers are rejected.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Eliminates state destruction during recursive self-compilation (+0.0110).",
                    "target_2_self_evaluator": "Enables bit-exact state rewind and deterministic debugging across epochs (+0.0090).",
                    "target_3_control_group": "Guarantees lossless message deduplication in Byzantine consensus (+0.0135).",
                },
                "tradeoffs": {
                    "strengths": "Provable zero data loss; mathematically reversible transactions eliminate rollback complexity.",
                    "constraints": "Reversibility tracking requires dedicated dissipation buffer channels.",
                },
            },
        },
    ),
    Axiom(
        id="L1-009",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Active Inference Generative Filter & Markov Blanket Isolation",
        statement="Subsystems must maintain internal generative models of their interface environments, executing state transitions that minimize variational free energy across insulating sensory and active Markov blankets.",
        formal_expression=r"\mathcal{F}(s, o) = \mathbb{E}_q[\ln q(s) - \ln p(o, s)] \ge -\ln p(o) \implies \min \mathcal{F}",
        operational_rule="Subsystems must interact strictly across sensory and active Markov blanket states by minimizing prediction error; uninsulated reactive coupling is prohibited.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Theoretical Neuroscience & Statistical Cybernetics (Karl Friston)",
            "source_principle": "Free Energy Principle & Markov Blankets (Derived from L0-020)",
            "system_profile": {
                "archetype": "Markov Blanket Predictive Feedback Loop",
                "topology_type": "Insulated Generative Model with Dual Blanket Boundaries",
                "topology_diagram": """[Internal Generative State] ──> [Active Blanket (Actions)] ──> [External Domain]
               ▲                                                      │
               │                                                      ▼
       [Free Energy Minimizer] <── [Sensory Blanket (Observations)] <──┘""",
                "subsystems": {
                    "Internal Generative Model": {
                        "role": "Maintains probabilistic priors over anticipated environmental message distributions.",
                        "invariant_rule": "Updates prior weights autonomously via observed prediction errors.",
                    },
                    "Sensory-Active Markov Blanket": {
                        "role": "Provides formal statistical insulation shielding internal variables from external noise.",
                        "invariant_rule": "Direct RPC access bypassing blanket boundary triggers compile rejection.",
                    },
                    "Variational Free Energy Resolver": {
                        "role": "Adjusts internal state parameters to minimize divergence between predicted and observed payloads.",
                        "invariant_rule": "Prioritizes actions that resolve interface ambiguity.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Anticipates dependency resolution bottlenecks before compilation stalls (+0.0120).",
                    "target_2_self_evaluator": "Filters spurious telemetry noise via predictive suppression (+0.0085).",
                    "target_3_control_group": "Mitigates network jitter and out-of-order packets via generative reconstruction (+0.0140).",
                },
                "tradeoffs": {
                    "strengths": "Proactive self-tuning resilience; shields subcomponents from external traffic spikes.",
                    "constraints": "Generative model inference incurs slight computational overhead on ingress.",
                },
            },
        },
    ),
    Axiom(
        id="L1-010",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Whiteheadian Event Concrescence & Prehension Directed Acyclic Mesh",
        statement="Architectural state must emerge strictly as a partially ordered sequence of immutable event concrescences (actual occasions); static mutable entities are prohibited in favor of explicit prehension causal graphs.",
        formal_expression=r"\mathcal{S}(t) = \bigoplus_{i=1}^k \text{Concrescence}(e_i) \quad \text{where} \quad e_i \in \text{ActualOccasions}",
        operational_rule="Static state objects without discrete event lineage or explicit prehension DAG ordering are rejected by the compiler.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Process Metaphysics & Causal Graph Theory (Alfred North Whitehead)",
            "source_principle": "Concrescence of Actual Entities (Derived from L0-023)",
            "system_profile": {
                "archetype": "Epochal Concrescence Engine & Event Process Graph",
                "topology_type": "Directed Acyclic Prehension Mesh",
                "topology_diagram": """[Past Actual Occasions] ──(Prehensive Ingest)──> [Concrescence Integrator]
                                                            │
                                                            ▼
                                              [Atomic Occasion Finalizer]
                                                            │
                                                            ▼
                                              [Immutable Historical Ledger]""",
                "subsystems": {
                    "Prehension Collector": {
                        "role": "Gathers causal influences from completed historical occasions across the DAG.",
                        "invariant_rule": "Preserves strict causal partial ordering without temporal paradoxes.",
                    },
                    "Concrescence Integrator": {
                        "role": "Synthesizes competing inputs into an atomic, indivisible execution event.",
                        "invariant_rule": "Atomic occasions execute with total transactional isolation.",
                    },
                    "Historical Horizon Ledger": {
                        "role": "Freezes finalized occasions into immutable anchors for future processes.",
                        "invariant_rule": "Retroactive modification of historical occasions is prohibited.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Eliminates race conditions in concurrent self-synthesis pipelines (+0.0130).",
                    "target_2_self_evaluator": "Provides complete mathematical provenance for every telemetry assertion (+0.0095).",
                    "target_3_control_group": "Guarantees Byzantine-tolerant causal ordering without distributed locks (+0.0150).",
                },
                "tradeoffs": {
                    "strengths": "Total immunity to state mutations and concurrency deadlocks; perfect auditability.",
                    "constraints": "Requires periodic DAG snapshotting and compaction for memory reclamation.",
                },
            },
        },
    ),
    Axiom(
        id="L1-015",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Zero-Trust Dual-Boundary Demarcation & Introspectable MCP Governance",
        statement="All inter-subsystem capabilities and data mutations must be bounded by formal typed schemas as data boundaries (Nouns) and deterministic state automata as temporal boundaries (Verbs), exposed via introspectable Model Context Protocol (MCP) gateways and verified through ephemeral self-healing sandboxes.",
        formal_expression=r"\mathcal{M}(s, a) \in \mathcal{G}_{\text{nouns}} \times \mathcal{A}_{\text{verbs}} \quad \land \quad \text{SandboxVerify}(a) = 0 \implies \text{Admissible}(a)",
        operational_rule="Subsystems attempting imperative state mutation without typed schema introspection or bypassing deterministic state machine guard transitions are rejected at compile time.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Zero-Trust Formal Language Semantics & Protocol Theory (The Axioma Paradigm)",
            "source_principle": "Dual-Boundary Governance: Schemas as Nouns, Automata as Verbs via Introspectable MCP",
            "system_profile": {
                "archetype": "Zero-Trust Dual-Boundary Gateway & Self-Healing MCP Arbiter",
                "topology_type": "Schema-Gated Gateway with State-Machine Guard Filter",
                "topology_diagram": """[Subsystem Mutation Intent a] ──> [MCP Schema Introspection Gateway (Nouns)]
                                           │
                                           ▼
                             [Automata State Machine Guard (Verbs)]
                                           │
                                           ▼
                             [Ephemeral Self-Healing Sandbox] ──> [Verified State Delta]""",
                "subsystems": {
                    "MCP Schema Introspection Gateway": {
                        "role": "Enforces strict GraphQL-style data graph boundaries; prohibits out-of-schema data shapes.",
                        "invariant_rule": "Every entity mutation must validate against declared schema AST.",
                    },
                    "Automata Temporal Guard": {
                        "role": "Enforces deterministic state transitions (XState automata) preventing illegal temporal operations.",
                        "invariant_rule": "Prohibits actions invalid in current state (e.g. charging unvalidated orders).",
                    },
                    "Self-Healing Sandbox Verifier": {
                        "role": "Executes proposed mutations in ephemeral test harnesses, auto-healing up to 3 compiler/test traces.",
                        "invariant_rule": "Mutations failing test sandbox with non-zero exit code cannot touch persistent state.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Binds recursive code generators inside strict schema and state boundaries (+0.0160).",
                    "target_2_self_evaluator": "Provides complete introspectable audit trails and zero-trust verification (+0.0155).",
                    "target_3_control_group": "Guarantees Byzantine nodes cannot inject arbitrary or out-of-order mutations (+0.0140).",
                },
                "tradeoffs": {
                    "strengths": "Mathematical zero-trust boundary; eliminates LLM hallucination in data shapes and state transitions.",
                    "constraints": "Requires formal schema definitions and state machine models for all subsystem interfaces.",
                },
            },
        },
    ),
    Axiom(
        id="L1-016",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Demarcated Exception Enclaves & Bounded Invariant Suspension",
        statement="Any necessary violation or edge-case bypass of an active architectural invariant must be confined within an explicitly demarcated Exception Enclave; enclaves must isolate the failure blast radius, emit machine-readable dissipation audit witnesses, and prohibit unverified state leakage to outer composable scopes.",
        formal_expression=r"\forall m \notin \mathcal{I}, \quad \text{Enclave}(m) \implies \partial \text{Scope}(m) \cap \mathcal{S}_{\text{outer}} = \emptyset \quad \land \quad \text{AuditWitness}(m) \neq \bot",
        operational_rule="Undemarcated or unisolated invariant breaches trigger immediate compile-time failure. Invariant suspensions are permitted only inside declared enclave wrappers with cryptographic dissipation logs and localized error boundaries.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Theoretical Computer Science & Monadic Enclave Theory (The `unsafe` Principle)",
            "source_principle": "Bounded Invariant Suspension & Isolated Blast Radius Containment",
            "system_profile": {
                "archetype": "Demarcated Exception Enclave & Audit Boundary Gateway",
                "topology_type": "Isolated Enclave Boundary with Cryptographic Audit Conduit",
                "topology_diagram": """[Edge-Case Mutation Intent] ──> [Enclave Entry Barrier]
                                              │
                                              ▼
                             [Bounded Invariant Suspension Scope]
                                              │
                               ┌──────────────┴──────────────┐
                               ▼                             ▼
                 [Cryptographic Audit Log]      [Humane Error Recovery Adapter]
                               │                             │
                               ▼                             ▼
                 [Audit Dissipation Witness]    [Graceful Persona Fallback]""",
                "subsystems": {
                    "Enclave Isolation Membrane": {
                        "role": "Confines unverified edge-case operations within an impermeable scope boundary; catches unhandled exceptions and prevents outer state corruption.",
                        "invariant_rule": "Scope boundary must catch all faults; zero unhandled error leakage permitted.",
                    },
                    "Invariant Suspension Auditor": {
                        "role": "Emits cryptographic dissipation audit witnesses detailing why and where the invariant was suspended.",
                        "invariant_rule": "Enclave execution without machine-readable justification is rejected.",
                    },
                    "Humane Error Recovery Adapter": {
                        "role": "Translates low-level enclave faults into graceful, actionable persona-oriented remediation paths instead of crashing the product.",
                        "invariant_rule": "Raw compiler or database dumps are intercepted and transformed into user-friendly guidance.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Permits necessary low-level runtime escapes (FFI, memory flush, raw socket I/O) without invalidating global compiler proofs (+0.0150).",
                    "target_2_self_evaluator": "Captures structured dissipation logs for all edge cases (+0.0135).",
                    "target_3_control_group": "Enables emergency split-brain recovery and partition fencing in distributed consensus (+0.0140).",
                    "target_4_product_usability": "Prevents catastrophic crashes, providing graceful fallback and gentle user recovery (+0.0165).",
                },
                "tradeoffs": {
                    "strengths": "Eliminates mathematical fragility; allows real-world edge-case handling without sacrificing zero-trust guarantees.",
                    "constraints": "Enclave usage must be audited and minimized to prevent abuse as an architectural shortcut.",
                },
            },
        },
    ),
    Axiom(
        id="L1-011",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Simplicial Homology Invariance & Betti Number Cycle Elimination",
        statement="Component dependency and message topologies must preserve invariant Betti numbers, enforcing beta_1 = 0 to provably eliminate circular deadlock cycles under recursive compilation.",
        formal_expression=r"\beta_0(\mathcal{K}_{\text{compiled}}) = \beta_0(\mathcal{K}_{\text{spec}}) \quad \land \quad \beta_1(\mathcal{K}) = 0",
        operational_rule="Dependency graphs introducing non-trivial 1-cycles (deadlock loops) or disconnecting 0-simplex components are rejected at compile time.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Algebraic Topology & Simplicial Homology (Henri Poincaré)",
            "source_principle": "Homological Cycle Elimination (Derived from L0-012)",
            "system_profile": {
                "archetype": "Simplicial Homology Topological Validator",
                "topology_type": "Simplicial Complex with Zero 1-Cycles (beta_1 = 0)",
                "topology_diagram": """[Subsystem Dependency AST] ──> [Simplicial Complex Mapper]
                                             │
                                             ▼
                             [Boundary Operator Evaluator d_1]
                                             │
                                             ▼
                                 [Betti Auditor: beta_1 = 0?] ──> [Deadlock-Free Mesh]""",
                "subsystems": {
                    "Simplicial Complex Mapper": {
                        "role": "Represents subsystem interactions as an abstract simplicial complex K.",
                        "invariant_rule": "Components form 0-simplices; communications form 1-simplices.",
                    },
                    "Boundary Operator Evaluator": {
                        "role": "Computes boundary matrices d_k to calculate homology groups H_k = ker(d_k) / im(d_k+1).",
                        "invariant_rule": "Verifies that d_k o d_k+1 = 0 holds strictly.",
                    },
                    "Betti Number Guard": {
                        "role": "Asserts that beta_1 = dim(H_1) = 0, proving zero circular wait dependencies exist.",
                        "invariant_rule": "Topologies with beta_1 > 0 are rejected prior to execution.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Guarantees self-compilation terminates without dependency cycles (+0.0140).",
                    "target_2_self_evaluator": "Ensures hierarchical telemetry streams never feed into circular observer loops (+0.0080).",
                    "target_3_control_group": "Eliminates distributed deadlock in multi-leader consensus protocols (+0.0145).",
                },
                "tradeoffs": {
                    "strengths": "Mathematical proof of deadlock freedom by topological construction.",
                    "constraints": "Requires strict acyclic structuring; circular callbacks must be refactored into event mediators.",
                },
            },
        },
    ),
    Axiom(
        id="L1-012",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Far-From-Equilibrium Self-Organizing Dissipative Outlets",
        statement="Subsystems operating under high-throughput input fluxes must maintain dedicated entropy dissipation outlets to autonomously generate macro-level self-organizing execution topologies under contention.",
        formal_expression=r"\frac{d_e S}{dt} < 0 \quad \land \quad \frac{d_i S}{dt} > 0 \implies \text{SpontaneousOrder}(\mathcal{M})",
        operational_rule="Static closed architectures unable to continuously export execution entropy and shed transient contention are rejected.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Non-Equilibrium Thermodynamics (Ilya Prigogine)",
            "source_principle": "Self-Organization in Dissipative Structures (Derived from L0-025)",
            "system_profile": {
                "archetype": "Non-Equilibrium Flux-Driven Self-Organizing Mesh",
                "topology_type": "Open System with Active Dissipative Conduits",
                "topology_diagram": """[High-Flux Workload Ingress] ──> [Non-Equilibrium Core] ──> [Self-Organizing Pipeline]
                                              │
                                              ▼
                                 [Dissipative Shedding Conduit]""",
                "subsystems": {
                    "Flux Concurrency Regulator": {
                        "role": "Drives execution kernels far from static equilibrium to trigger emergent pipelining.",
                        "invariant_rule": "Maintains high continuous throughput to sustain dynamic structures.",
                    },
                    "Dissipative Shedding Conduit": {
                        "role": "Continuously purges stale caches, expired RPC contexts, and noisy telemetry buffers.",
                        "invariant_rule": "Rate of entropy export must exceed internal entropy generation.",
                    },
                    "Self-Organizing Topology Arbiter": {
                        "role": "Autonomously re-routes message queues based on localized throughput pressure.",
                        "invariant_rule": "Restructures execution stages to minimize internal transaction drag.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Maintains peak compilation throughput during complex AST syntheses (+0.0115).",
                    "target_2_self_evaluator": "Prevents buffer bloating and latency spikes during high-frequency evaluation (+0.0105).",
                    "target_3_control_group": "Stabilizes distributed message brokers under severe network congestion (+0.0160).",
                },
                "tradeoffs": {
                    "strengths": "System thrives under high load, automatically tuning execution paths to maximize flow.",
                    "constraints": "Requires minimum continuous activity threshold to maintain dissipative organization.",
                },
            },
        },
    ),
    Axiom(
        id="L1-013",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Category-Theoretic Adjoint Galois Connection & Universal Factorization",
        statement="Declarative specification syntax and compiled runtime semantics must form an adjoint functor pair F -| G, ensuring universal factorization and round-trip Galois closure without semantic distortion.",
        formal_expression=r"\text{Hom}_{\mathcal{C}}(F(A), B) \cong \text{Hom}_{\mathcal{D}}(A, G(B)) \quad (\text{Unit-Counit Adjunction})",
        operational_rule="Transformations between specifications and binaries lacking adjoint right-inverses or failing Galois round-trip closure trigger compiler rejection.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Category Theory & Abstract Algebra (Mac Lane & Kan)",
            "source_principle": "Adjoint Functor Duality (Derived from L0-015)",
            "system_profile": {
                "archetype": "Free-Forgetful Adjunction Transcompiler",
                "topology_type": "Bidirectional Natural Isomorphism Pipeline",
                "topology_diagram": """[Specification Category C] ──(Left Adjoint F)──> [Runtime Category D]
                │                                         │
                ▲                                         ▼
         [Unit eta] <───(Right Adjoint G)─── [Counit epsilon]""",
                "subsystems": {
                    "Left Adjoint Synthesizer (F)": {
                        "role": "Constructs the free structural implementation from declarative specification models.",
                        "invariant_rule": "Preserves all coproducts, colimits, and modular pushouts from category C.",
                    },
                    "Right Adjoint Auditor (G)": {
                        "role": "Extracts forgetful behavioral observations from executing binaries back to specs.",
                        "invariant_rule": "Preserves all Cartesian products, limits, and pullbacks into category D.",
                    },
                    "Adjunction Unit Arbiter": {
                        "role": "Verifies that round-trip composition eta o epsilon satisfies Kan triangular identities.",
                        "invariant_rule": "Rejects transformations where round-trip evaluation deviates from identity.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Guarantees compiled engine binaries precisely reflect architectural specifications (+0.0135).",
                    "target_2_self_evaluator": "Enables algebraic verification of system invariants without black-box testing (+0.0110).",
                    "target_3_control_group": "Provides mathematical proofs of consensus protocol state preservation (+0.0150).",
                },
                "tradeoffs": {
                    "strengths": "Provable bidirectional correctness; specifications and runtimes are mathematically synchronized.",
                    "constraints": "Formalizing interfaces as strict adjoint functors requires rigorous mathematical schemas.",
                },
            },
        },
    ),
    Axiom(
        id="L1-014",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Spinozian Substance Monism & Modal Dual-Aspect Synchronization",
        statement="Execution logic and observability telemetry must operate as parallel modal attributes of an identical underlying state substrate, guaranteeing that telemetry observation never introduces observer bias or drift.",
        formal_expression=r"\mathcal{A}_{\text{exec}}(\mathcal{S}) \parallel \mathcal{A}_{\text{telemetry}}(\mathcal{S}) \quad \text{where} \quad \mathcal{S} \in \text{Substance}",
        operational_rule="Independent logging or monitoring subsystems operating on detached mutable state clones rather than primary state projections are prohibited.",
        status=AxiomStatus.CANDIDATE,
        metadata={
            "exogenous_domain": "Rationalist Metaphysics (Baruch Spinoza)",
            "source_principle": "Substance Monism and Dual-Aspect Parallelism (Derived from L0-018)",
            "system_profile": {
                "archetype": "Dual-Aspect Monistic Substrate",
                "topology_type": "Unified State Substrate with Dual Modal Projections",
                "topology_diagram": """                 [Unified State Substrate S]
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
  [Execution Attribute A_1]     [Telemetry Attribute A_2]
              │                             │
              ▼                             ▼
    [Runtime State Delta]        [Zero-Cost Telemetry Stream]""",
                "subsystems": {
                    "Monistic Substrate Storage": {
                        "role": "Maintains the singular ground-truth memory representation for each subsystem.",
                        "invariant_rule": "Prohibits independent secondary data stores for audit tracking.",
                    },
                    "Execution Attribute Dispatcher": {
                        "role": "Projects state transitions along the functional computational dimension.",
                        "invariant_rule": "Executes domain business logic without telemetry side-effects.",
                    },
                    "Modal Telemetry Projector": {
                        "role": "Extracts real-time observability metrics as an intrinsic modal attribute of the same substrate.",
                        "invariant_rule": "Telemetry emission incurs zero state mutation and zero observer bias.",
                    },
                },
                "target_behaviors": {
                    "target_1_self_constructor": "Ensures compiler diagnostics are direct projections of AST mutations (+0.0110).",
                    "target_2_self_evaluator": "Eliminates Heisenberg observer effects where monitoring alters system behavior (+0.0145).",
                    "target_3_control_group": "Guarantees consensus audit logs are bit-identical to committed state blocks (+0.0130).",
                },
                    "tradeoffs": {
                    "strengths": "Zero-overhead observability; guarantees telemetry can never fall out of sync with state.",
                    "constraints": "Substrate must be designed from the start to support dual modal projection.",
                },
            },
        },
    ),
]




class AxiomPromptGenerator:
    """Generates structured prompts and candidate axiom proposals with detailed system profiles."""

    def build_discovery_prompt(
        self,
        epoch: int,
        phase: PhaseState,
        level_0_axioms: List[Axiom],
        level_1_axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
        compute_tokens: int,
        epistemic_scaffolding: Optional[List[Axiom]] = None,
    ) -> str:
        """Constructs an LLM prompt to discover the next candidate axiom.
        
        Even after The Jettison transitions Level 0 axioms to INACTIVE status,
        the established epistemic scaffolding permanently guides hypothesis synthesis.
        """
        effective_l0 = level_0_axioms if level_0_axioms else (epistemic_scaffolding or [])
        is_scaffolding = not level_0_axioms and bool(epistemic_scaffolding)

        l0_header = (
            "Established Epistemic Scaffolding (Genetic Lineage · Inactive at Runtime):"
            if is_scaffolding
            else "Active Level 0 Epistemic Axioms:"
        )
        l0_text = "\n".join(
            [f"- [{a.id}] {a.name}: {a.statement} (Rule: {a.operational_rule})" for a in effective_l0]
        ) or "None (Jettisoned)"

        l1_text = "\n".join(
            [f"- [{a.id}] {a.name}: {a.statement} (Rule: {a.operational_rule})" for a in level_1_axioms]
        ) or "None committed yet"

        neg_text = "\n".join(
            [f"- [{n.id}] {n.name}: FORBIDDEN: {n.forbidden_pattern} (Rationale: {n.rationale})" for n in negative_axioms]
        ) or "None active"

        has_exogenous_rule = any(
            "exogenous" in a.name.lower() or "non-computing domain" in a.operational_rule.lower()
            for a in effective_l0
        )

        exogenous_prompt_clause = ""
        if has_exogenous_rule:
            exogenous_prompt_clause = """
EXOGENOUS SYNTHESIS CONSTRAINT (Governed by L0-003):
- You MUST first select a non-computing domain (such as applied category theory, theoretical linguistics, phenomenological philosophy, or quantum mechanics).
- Extract a foundational structural principle from that domain.
- The proposed candidate axiom MUST be a direct topological translation of that exogenous principle into systems architecture.
"""

        target_tier = "Level 0 Epistemic" if (phase == PhaseState.PHASE_1_META_EXPLORATION and len(level_0_axioms) < 10) else "Level 1 Structural"

        return f"""You are the Axiom Synthesizer for a Self-Constructing Architecture.
Epoch: {epoch} | Phase: {phase.value} | Target Tier: {target_tier} | Token Budget: {compute_tokens}

{l0_header}
{l0_text}

Active Level 1 Structural Axioms:
{l1_text}

Negative Invariants (Hard Veto Constraints):
{neg_text}
{exogenous_prompt_clause}
Goal: Propose exactly ONE new {target_tier} Axiom that satisfies:
1. Strict adherence to Level 0 Epistemic Principles (Compositionality L0-001, Exogenous Topological Mapping L0-003, Dialectical Reconciliation L0-006, Simplicial Homology L0-012).
2. Strict avoidance of any Negative Invariant patterns.
3. High generalizability across validation targets (The Self-Constructor, The Self-Evaluator, Byzantine Control Group).

Output in structured format:
ID: {'L0-XXX' if 'Level 0' in target_tier else 'L1-XXX'}
Name: <Name>
Statement: <Concise invariant description>
Formal Expression: <Mathematical notation>
Operational Rule: <Concrete architectural constraint>
"""

    def generate_candidate_batch(
        self,
        count: int,
        epoch: int,
        phase: PhaseState,
        level_0_axioms: List[Axiom],
        level_1_axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
        known_axiom_ids: Optional[set[str]] = None,
        epistemic_scaffolding: Optional[List[Axiom]] = None,
    ) -> List[Axiom]:
        """Synthesizes a batch of K candidate axioms pulling from divergent exogenous domains.

        In PHASE_1_META_EXPLORATION (until at least 10 epistemic axioms are committed):
        generates Level 0 Epistemic Axiom candidates.
        In PHASE_2_STRUCTURAL_EXECUTION:
        generates Level 1 Structural Axiom candidates grounded in the established epistemic scaffolding.
        """
        effective_l0 = level_0_axioms if level_0_axioms else (epistemic_scaffolding or [])
        is_epistemic_phase = (
            phase == PhaseState.PHASE_1_META_EXPLORATION
            and len(level_0_axioms) < 10
        )

        candidate_pool = LEVEL_0_EPISTEMIC_CANDIDATE_POOL if is_epistemic_phase else LEVEL_1_STRUCTURAL_CANDIDATE_POOL

        # Filter out already committed or previously evaluated axioms
        excluded_ids = {a.id for a in level_1_axioms} | {a.id for a in level_0_axioms}
        if known_axiom_ids:
            excluded_ids |= set(known_axiom_ids)

        batch: List[Axiom] = []
        for cand in candidate_pool:
            if cand.id not in excluded_ids:
                cand_copy = copy.deepcopy(cand)
                cand_copy.origin_epoch = epoch
                batch.append(cand_copy)
                if len(batch) >= count:
                    return batch

        # Fallback dynamic synthesis guided by epistemic heuristics in effective_l0
        while len(batch) < count:
            idx = len(batch) + 1
            suffix = f"{epoch:03d}_{idx}"
            tier_prefix = "L0" if is_epistemic_phase else "L1"
            level_enum = AxiomLevel.LEVEL_0_EPISTEMIC if is_epistemic_phase else AxiomLevel.LEVEL_1_STRUCTURAL

            if is_epistemic_phase:
                name = f"Synthesized Epistemic Search Heuristic {suffix}"
                stmt = f"Epistemic exploration in epoch {epoch} must prune redundant hypotheses across boundary {idx}."
                rule = f"Heuristics failing boundary {idx} constraint are pruned at synthesis."
                domain = "Abstract Systems Epistemology"
                principle = "Dynamic Search Space Partitioning"
            else:
                # Grounded directly in an established epistemic scaffolding axiom
                epistemic_source = effective_l0[(idx - 1) % len(effective_l0)] if effective_l0 else None
                if epistemic_source:
                    domain = epistemic_source.metadata.get("exogenous_domain", "Applied Mathematical Epistemology")
                    principle = f"Topological Translation of [{epistemic_source.id}] {epistemic_source.name}"
                    name = f"Structural Realization of [{epistemic_source.id}] ({suffix})"
                    stmt = f"Subsystems in epoch {epoch} enforce structural invariant derived from {epistemic_source.name}: every component must preserve {epistemic_source.statement}"
                    rule = f"State transformations violating [{epistemic_source.id}] rule ({epistemic_source.operational_rule}) are rejected at compile time."
                else:
                    domain = "Abstract Systems Architecture"
                    principle = "Dynamic Modular Decoupling"
                    name = f"Synthesized Structural Invariant {suffix}"
                    stmt = f"Subsystems in epoch {epoch} must decouple state transformation from persistence across boundary {idx}."
                    rule = f"Ensure strict modular separation of concerns at boundary {idx}."

            batch.append(
                Axiom(
                    id=f"{tier_prefix}-{suffix}",
                    level=level_enum,
                    name=name,
                    statement=stmt,
                    formal_expression=rf"\mathcal{{T}}_{{{idx}}}(S) = \mathcal{{P}}(\delta(S))",
                    operational_rule=rule,
                    status=AxiomStatus.CANDIDATE,
                    origin_epoch=epoch,
                    metadata={
                        "exogenous_domain": domain,
                        "source_principle": principle,
                        "system_profile": {
                            "archetype": f"Epistemically Grounded Subsystem Controller {suffix}",
                            "topology_type": "Decoupled Boundary Mesh with Epistemic Guard",
                            "topology_diagram": f"[Ingress {idx}] ──> [Epistemic Guard: {domain}] ──> [Verified Core {idx}]",
                            "subsystems": {
                                f"Boundary Controller {idx}": {
                                    "role": "Regulates interface transactions across module boundaries.",
                                    "invariant_rule": rule,
                                }
                            },
                            "target_behaviors": {
                                "target_1": f"Verifies boundary {idx} modularity in target 1 (+0.0080).",
                                "target_2": f"Ensures audit trail consistency across boundary {idx} (+0.0070).",
                                "target_3": f"Maintains distributed consensus across boundary {idx} (+0.0090).",
                            },
                            "tradeoffs": {
                                "strengths": "Directly grounded in established epistemic scaffolding principles.",
                                "constraints": "Requires explicit interface boundary registration.",
                            },
                        },
                    },
                )
            )

        return batch

    def generate_candidate_axiom(
        self,
        epoch: int,
        phase: PhaseState,
        level_0_axioms: List[Axiom],
        level_1_axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
        known_axiom_ids: Optional[set[str]] = None,
    ) -> Axiom:
        """Single-candidate generator for backwards compatibility."""
        batch = self.generate_candidate_batch(
            count=1,
            epoch=epoch,
            phase=phase,
            level_0_axioms=level_0_axioms,
            level_1_axioms=level_1_axioms,
            negative_axioms=negative_axioms,
            known_axiom_ids=known_axiom_ids,
        )
        return batch[0]
