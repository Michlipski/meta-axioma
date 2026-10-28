# 📊 Live Cryptographic Telemetry Dashboard: `soc_test_dashboard_app`

- **Compiler Identity:** `SystemG3b_DashboardGate`
- **SHA-256 Chain Head Witness:** `869844b36eb8b577bb9686a03f36b6861730dac7ec24072735d2ff89488a4823`
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
| **Emitted Epoch Disk Tokens** | `9,631` | Measured across `10` compiler epoch files |
| **Emitted App Directory Tokens** | `12,486` | Measured across `3` application files |
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
| `telemetry_dashboard.html` | `6,240` |
| `tests/__init__.py` | `15` |
| `tests/test_emitted_system.py` | `490` |
| `topology_config.json` | `285` |
| `topology_verifier.py` | `345` |

### Full Application Directory (`apps/<app_id>/`) Physical Files

| App File Path | Physical BPE Tokens |
| :--- | :---: |
| `dashboard.html` | `6,240` |
| `server.py` | `6` |
| `telemetry_dashboard.html` | `6,240` |

---

## 5. SHA-256 Cryptographic Event Chain

| Index | Event Type | Previous Hash (Prefix) | Event Hash (SHA-256) |
| :---: | :--- | :--- | :--- |
| `0` | `COMPILATION_INITIATED` | `000000000000...` | `edc586085f0141fdfa1b0027df3ce6434270ec6941bad5a3c5e273fe331ffbe2` |
| `1` | `CRUCIBLE_SYNTHESIS_CERTIFIED` | `edc586085f01...` | `54eac88164061a6d18729b2e092abb8c078c7e5fbc4f79eadd107a6aa283dc9a` |
| `2` | `APP_SUBSTRATE_AUDITED_AND_VERIFIED` | `54eac8816406...` | `de6dc5bbec2e80b61db621dd23de08fa98c268a0dc47f8ca362938cf3568249b` |
| `3` | `STACK_TRACE_SEALED` | `de6dc5bbec2e...` | `72dc29a4cecc9626539d494ca3a97920f77eb018649f1eda78539f744ca5c6d3` |
| `4` | `DISK_SUBSTRATE_MEASURED` | `72dc29a4cecc...` | `5816627c0808b3d03a765ea07a5f05bad20c0f6192fcc80bd19ca4254613e8c9` |
| `5` | `SUBSTRATE_TEST_WITNESS` | `5816627c0808...` | `6692614e4b1de98d384f217a249a76b4aa024fa6bc3ecf03686b036ab409e2b2` |
| `6` | `THERMODYNAMIC_LEDGER_SEALED` | `6692614e4b1d...` | `869844b36eb8b577bb9686a03f36b6861730dac7ec24072735d2ff89488a4823` |
