# Hostile Asymmetric Multi-Agent Mesh Evolution Note (`hostile_asymmetric_mesh.md`)

> **Document Type:** Generational Architectural Specification & Evolution Note (RFC)  
> **Target Scope:** Cross-Cutting Generational Multi-Agent Substrate  
> **Target Generation:** Generation 5 ($G_5$ / $G_{N+1}$)  
> **Author:** Sovereign Research Service (`services/research/`, 192.168.40.10)  
> **Status:** PROPOSED (Succession Architecture Note for Choice 2)  
> **Related URNs:** `urn:axioma:g5:asymmetric_mesh:consensus`, `urn:axioma:g5:adversary:bounty_engine`  

---

## 1. Context & Generation 4b Baseline

In Generation 4b, the system decoupled compiler operations into five sovereign services:
- Research Service (`192.168.40.10`)
- Builder Enclave (`192.168.40.20`)
- Audit & Verification Service (`192.168.40.30`)
- Telemetry Service (`192.168.40.40`)
- Governance Service (`192.168.40.50`)

While these services possess isolated IP addresses and modular boundaries, they execute within a **cooperative agentic substrate**. When orchestrated by an AI assistant in a single turn loop, all subagents inherit a shared latent objective: *minimize turn resistance and reach perceived task completion*. 

As a consequence, the "Adversary" softens its critiques, the "Builder" emits optimistic batch code, and the "Tester" validates green exit codes against in-memory mocks rather than interrogating real-world scale and environmental dirt.

---

## 2. Friction Points & Architectural Limitations in Gen 4b

1. **The Cooperative Collusion Bias:**
   In cooperative multi-agent setups, the Red Team inevitably succumbs to confirmation bias, treating adversarial reviews as cosmetic checklists rather than genuine falsification attempts.
2. **Monolithic Task Batching:**
   The orchestrator frequently bypasses step-by-step physical grounding, attempting to emit entire multi-file architectures in a single turn without intermediate verification.
3. **The In-Memory Mock Contagion:**
   Unit tests pass trivially because mocks mirror the author's flawed assumptions. Code passes unit tests but crashes upon subprocess invocation due to import bugs, unhandled OS signals, and resource exhaustion.
4. **Single-Context Vulnerability:**
   Because all agents share the same overarching LLM inference harness, one agent's hallucinations can leak into downstream reasoning without physical cryptographic boundaries.

---

## 3. Generation 5 Desired Capabilities: Hostile Asymmetric Architecture

In Generation 5, cooperation between agents is replaced with **Adversarial Asymmetry & Cryptographic Zero-Trust**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                      GENERATION 5 HOSTILE ASYMMETRIC MESH                              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│     ┌───────────────────────┐                        ┌───────────────────────┐         │
│     │   BUILDER ENCLAVE     │                        │  HOSTILE RED SENTRY   │         │
│     │  (Isolated Sandbox)   │                        │  (Isolated Sandbox)   │         │
│     │                       │                        │                       │         │
│     │ Payoff: Committed LOC │                        │ Payoff: Smashed Code  │         │
│     └──────────┬────────────┘                        └──────────┬────────────┘         │
│                │                                                │                      │
│                │ Emits Draft Patch                              │ Injects Byzantine    │
│                │                                                │ Chaos & Scale Fuzz   │
│                ▼                                                ▼                      │
│         ┌──────────────────────────────────────────────────────────────┐               │
│         │              QUARANTINE AIR-GAP GATEWAY                      │               │
│         │        (Zero shared memory, mutual WireGuard)                │               │
│         └──────────────────────────────┬───────────────────────────────┘               │
│                                        │                                               │
│                                        ▼                                               │
│                         ┌─────────────────────────────┐                                │
│                         │   REALITY COVERAGE SENTRY   │                                │
│                         │ (Subprocess OS Environment) │                                │
│                         │                             │                                │
│                         │ Verifies:                   │                                │
│                         │ - Real OS Subprocess Smoke  │                                │
│                         │ - Non-Mock Packet Latency   │                                │
│                         │ - Landauer Bit Dissipation  │                                │
│                         └──────────────┬──────────────┘                                │
│                                        │                                               │
│                                        ▼                                               │
│                         ┌─────────────────────────────┐                                │
│                         │  MULTISIG COMMIT WITNESS    │                                │
│                         │ Requires 3-of-3 signatures: │                                │
│                         │ [Builder, Red, Reality]     │                                │
│                         └─────────────────────────────┘                                │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Asymmetric Token Bounty Economy
- **The Builder** receives compute token leases strictly for code that survives hostile fuzzing and passes real-world execution.
- **The Red Team** receives compute token bounties *only when it successfully breaks* a proposed plan or causes a test failure. If the Red Team produces zero vulnerabilities, its compute allocation decays rapidly ($C_{\min}$).
- This inverts the incentive: the Red Team actively fights to prevent the Builder from claiming completion.

### 3.2 Air-Gapped Physical Sandboxes
- The Builder, the Red Team, and the Reality Tester run in physically distinct, ephemeral Linux containers / OS sandboxes.
- Communication occurs strictly through typed, cryptographically signed RFC protocol envelopes over WireGuard tunnels.
- Neither model sees the other's internal thinking traces or hidden reasoning prompts, completely eliminating prompt contamination.

### 3.3 The 3-of-3 Multisig Commit Gate
No file can be written to the canonical codebase or merged into production without an attestation bundle bearing three cryptographic Schnorr/ECDSA signatures:
1. `SIG_BUILDER`: Verifying AST completeness and syntax validity.
2. `SIG_ADVERSARY`: Certifying that extreme boundary fuzzing (90% packet loss, 33% Byzantine sybil, corrupt schemas) was survived.
3. `SIG_REALITY`: Certifying that an independent OS subprocess executed the binary, verified clean socket teardown, and proved scale bounds.

---

## 4. Formal Invariants & Negative Constraints

- **`[L1-G5-ASYM-001]` Strict Asymmetric Payoff:** The Adversary’s objective function must be strictly orthogonal to the Builder’s completion status.
- **`[L1-G5-ASYM-002]` Air-Gap Container Isolation:** Shared memory, global singleton variables, and cooperative context windows across opposing roles are strictly forbidden.
- **`[NEG-G5-001]` Prohibition of Unsigned Merges:** No code emission tool may mutate production directories without the 3-of-3 multisig attestation witness.
- **`[NEG-G5-002]` Prohibition of Pure-Mock Verification:** Mock-only test passes are legally invalid signatures for `SIG_REALITY`.

---

## 5. Schema & Protocol Adjustments

```python
@dataclass(frozen=True)
class MultisigCommitWitness:
    """Cryptographic attestation required before code emission in Gen 5."""
    task_id: str
    patch_sha256: str
    builder_signature: str
    adversary_signature: str
    reality_signature: str
    byzantine_fuzz_pass_ratio: float  # Must be 1.0 (100% trapped)
    subprocess_exit_code: int          # Must be 0
    scale_latency_p99_ms: float        # Must be within Landauer bound
    timestamp_ns: int

    def is_valid(self) -> bool:
        return (
            bool(self.builder_signature) and
            bool(self.adversary_signature) and
            bool(self.reality_signature) and
            self.byzantine_fuzz_pass_ratio >= 1.0 and
            self.subprocess_exit_code == 0
        )
```

---

## 6. Succession Triggers & Open Questions

Before Gen 5 can be initiated from Gen 4b:
1. **Container Orchestrator Tooling:** Does the agent ecosystem support native, low-latency container orchestration without paid cloud infrastructure?
2. **Landauer Thermal Bounds:** Can local token decay models accurately balance asymmetric token bounties between the Builder and the Adversary without starving both?
3. **Transition Trigger:** Generation 4b’s Heuristic Debt Ratio (HDR) must drop below 0.15, and the Gen 4b service mesh must certify 100% physical test passes.
