# 📊 Live Cryptographic Telemetry Dashboard: `soc_test_dashboard_app`

- **Compiler Identity:** `SystemG3b_DashboardGate`
- **SHA-256 Chain Head Witness:** `447f4ca02e94450fb314e8bac26824e80ee3b0bab8ebe580af7eb5e008cadb4d`
- **Chained Cryptographic Events:** `7`
- **Live AGY Subagent Spawning (`invoke_subagent`):** ⚠️ `0` live `invoke_subagent` calls (Executed via in-process deterministic fallback)
- **Substrate Test Exit Code:** `0` (`4` tests passing)

---

## 1. Thermodynamic Capital & Dual-Model Token Ledger (`[L1-G3B-014]`)

| Metric | Token / Physical Value | Pool / Model Attribution |
| :--- | :---: | :--- |
| **Total Allocated Budget** | `7,800` | Calibrated 60/40 Thermodynamic Envelope |
| **Predicted Total Spend** | `4,800` | Pre-Execution `DynamicBudgetCalibrator` Estimate |
| **Prediction Accuracy** | `99.8%` | Predicted vs. Actual Physical BPE Spend (`4,812` tokens) |
| **Exploratory Pool Cap (60%)** | `4,680` | Generative & Deliberative Ceiling (`80.3%` utilized) |
| **Protected Pool Floor (40%)** | `3,120` | Immutable Verification Sink Floor |
| **Gemini 4 Argon Deliberation** | `1,563` | The Brain (SoC + Stack Decomposition) |
| **Gemini 3.8 Flash Leaf Emission** | `2,197` | The Muscle (Indivisible Leaf Synthesis) |
| **Gemini 4 Argon Verification Sinks** | `2,143` | The Brain (Protected Zero-Trust Audits) |
| **Total Exploratory Spent** | `3,760` | `920` remaining (`80.3%` pool utilization) |
| **Total Protected Spent** | `1,052` | `2,068` remaining |
| **Total Budget Spent** | `4,812` | `61.7%` overall budget utilization |
| **Emitted Epoch Disk Tokens** | `9,627` | Measured across `10` compiler epoch files |
| **Emitted App Directory Tokens** | `12,478` | Measured across `3` application files |
| **Landauer Bits Erased** | `0` bits | Discarded defective leaf attempts |
| **Landauer Heat Dissipated ($Q$)** | `0.000000e+00` J | $Q = k_B T \ln(2) \cdot \text{bits}$ at $T=300\text{K}$ |

---

## 2. Subagent Spawning & Dual-Model Routing Witness (`[L1-G3B-014]`)

- **Status:** ⚠️ `0` live `invoke_subagent` calls (Executed via in-process deterministic fallback)

---

## 3. Emitted Physical Files on Disk (`[NEG-G1B-001]`)

| Relative File Path | Physical BPE Tokens |
| :--- | :---: |
| `contract_service.py` | `897` |
| `domain_models.py` | `235` |
| `leaf_code.py` | `191` |
| `run.py` | `240` |
| `statechart_engine.py` | `693` |
| `telemetry_dashboard.html` | `6,236` |
| `tests/__init__.py` | `15` |
| `tests/test_emitted_system.py` | `490` |
| `topology_config.json` | `285` |
| `topology_verifier.py` | `345` |

### Full Application Directory (`apps/<app_id>/`) Physical Files

| App File Path | Physical BPE Tokens |
| :--- | :---: |
| `dashboard.html` | `6,236` |
| `server.py` | `6` |
| `telemetry_dashboard.html` | `6,236` |

---

## 5. SHA-256 Cryptographic Event Chain

| Index | Event Type | Previous Hash (Prefix) | Event Hash (SHA-256) |
| :---: | :--- | :--- | :--- |
| `0` | `COMPILATION_INITIATED` | `000000000000...` | `edc586085f0141fdfa1b0027df3ce6434270ec6941bad5a3c5e273fe331ffbe2` |
| `1` | `CRUCIBLE_SYNTHESIS_CERTIFIED` | `edc586085f01...` | `54eac88164061a6d18729b2e092abb8c078c7e5fbc4f79eadd107a6aa283dc9a` |
| `2` | `APP_SUBSTRATE_AUDITED_AND_VERIFIED` | `54eac8816406...` | `0cd89a46f5277fd791b9a1d036121781f3a6ef6344e2463e7f49c715745852cf` |
| `3` | `STACK_TRACE_SEALED` | `0cd89a46f527...` | `f557a0680ce912b7b8a53357483184a72bfe78d9601494a046011a9692b6377b` |
| `4` | `DISK_SUBSTRATE_MEASURED` | `f557a0680ce9...` | `425bd5ff6eb5c026b61d67014c985e4b9b7b0ff76517adf73e44e90b6aa228b9` |
| `5` | `SUBSTRATE_TEST_WITNESS` | `425bd5ff6eb5...` | `2e1b75f9056595a51629e1c905a68ea77af9c4d2037286886c67a9c2ac854fba` |
| `6` | `THERMODYNAMIC_LEDGER_SEALED` | `2e1b75f90565...` | `447f4ca02e94450fb314e8bac26824e80ee3b0bab8ebe580af7eb5e008cadb4d` |
