# Generation 4b Sovereign Builder Enclave (`services/builder`)

## Overview
The **Sovereign Builder Enclave** (`services/builder`) is the primary generative synthesis engine in Generation 4b. Under the Decoupled Research Sovereignty Invariant (`[L1-G4B-001]`), Builder is physically and logically separated from the Research Service (`services/research`).

## Key Responsibilities
1. **Deliverable Ingestion:** Ingests certified, immutable `ResearchDeliverableBundle` specifications from `services/research/` via standardized schemas in `protocols/deliverable_bundle.py`.
2. **Code Emission & Synthesis:** Emits physical, non-zero-byte source files, statecharts, topologies, and test suites for target applications.
3. **Asynchronous RFC Protocol Participation:**
   - When encountering physical friction (token decay, latency overruns, irreversibility), submits `SpecAdjustmentRequest` via `protocols/rfc_protocol.py`.
   - Halts synthesis of affected modules until Research adjudicates with a cryptographically signed `SpecAmendment` or refutes with a mathematical `CounterProof`.
   - Never alters specifications unilaterally.
4. **Boundary Isolation:** Bound to dedicated non-loopback IP `192.168.40.20`.
