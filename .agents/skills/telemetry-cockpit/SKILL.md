---
name: telemetry-cockpit
description: >-
  Launch, inspect, and interact with the Telemetry Cockpit, SQLite WAL Event Stream,
  Live Mesh Node Graph, and Timeline Scrubber. Use when auditing transaction logs,
  monitoring live tasks, scrubbing the state timeline, or verifying event replay.
---

# Mode 6: Telemetry Cockpit (`/telemetry-cockpit`)

The `/telemetry-cockpit` mode interfaces with the **Sovereign Telemetry Service** (Generation 4b: `generations/gen_04b/services/telemetry/`, binding to `192.168.40.40`).

Use this mode to inspect live service-task relationships, audit nanosecond transaction logs, scrub back and forth along the timeline, and verify event-sourced state replay or forking.

---

## 1. Core Telemetry Capabilities

1. **Live Service-to-Task Node Graph:**
   - Visual representation of which service (`research`, `builder`, `audit`, `governance`, `telemetry`) is handling each task at any given moment.
   - Dynamic Canvas/SVG display of nodes, operational states, and active channel messages.
2. **Nanosecond Micro-Transaction Log (`MeshTransactionRecord`):**
   - Micro-timestamped records logging transaction ID, source service, target service, event payload, and state snapshot digest.
   - Preserved in persistent SQLite WAL store (`event_store.py`).
3. **Interactive Timeline Scrubber:**
   - Scrub backward and forward across all recorded state transitions.
   - Visual inspection of historical states, queue depths, and token dissipation meters.
4. **Event-Sourced State Replay & Forking:**
   - Replay recorded event streams from any historical checkpoint.
   - Test retries and speculative execution forks without mutating the canonical state.

---

## 2. Cockpit Operations & Diagnostic Commands

- **Check Telemetry Service Health:**
  ```bash
  python3 -c "from generations.gen_04b.services.telemetry.src.telemetry_vault import TelemetryVault; print('Vault OK')"
  ```
- **Inspect SQLite Event Store:**
  - Verify SQLite WAL database existence and table schemas (`events`, `transactions`, `snapshots`).
- **Launch Decoupled Cockpit Server:**
  - Run `cockpit_server.py` (or view standalone `telemetry_dashboard.html`).
- **Audit Recent Transactions:**
  - Read `generations/gen_04b/services/telemetry/telemetry_ledger.json` to inspect the latest Merkle-DAG transaction anchors.
