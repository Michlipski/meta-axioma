# Generation 4b Telemetry & Evaluation Service (`services/telemetry`)

## Overview
The **Telemetry & Evaluation Service** (`services/telemetry`) tracks thermodynamic capital decay, Landauer bit-erasure dissipation, and cryptographic Merkle-DAG witness chaining across the G4b sovereign mesh.

## Key Responsibilities
1. **Thermodynamic Capital Accounting:** Enforces the 60% Exploratory Capital ceiling and 40% Protected Capital floor.
2. **Landauer Dissipation Tracking:** Measures information erasure and calculates thermodynamic heat generation:
   $$Q = k_B T \ln 2 \cdot \text{bits}$$
3. **Hierarchical Merkle-DAG Chaining (`[L1-G4B-003]`):** Maintains the tamper-evident hash chain from genesis anchor to live runtime milestones.
4. **Development Process Telemetry Dashboard (`[L1-G3B-018]`):** Emits and updates real-time operational HUDs with zero external CDN dependencies.
5. **Boundary Isolation:** Bound to dedicated non-loopback IP `192.168.40.40`.
