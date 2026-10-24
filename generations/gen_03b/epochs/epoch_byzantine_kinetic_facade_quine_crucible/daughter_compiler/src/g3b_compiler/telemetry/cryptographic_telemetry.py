"""Generation 3b Live Cryptographic Telemetry & Thermodynamic Dashboard Engine.

Enforces Live Telemetry Cryptography:
- Physically measures emitted files on disk via PhysicalTokenMeter.
- Logs exact token counts separated by model tier (Gemini 4 Argon Brain vs. Gemini 3.8 Flash Muscle)
  and Landauer bit-erasure heat dissipation (Joules at T=300K).
- Chains every telemetry event with SHA-256 cryptographic hashes (H_i = SHA256(H_{i-1} || payload_i))
  so any post-hoc tampering or fiat fabrication is mathematically detectable.
- Emits both machine-verifiable `telemetry_ledger.json` and human-readable `telemetry_dashboard.md`.
"""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from ..thermodynamics import PhysicalTokenMeter, ThermodynamicLedger


GENESIS_HASH = "0" * 64


@dataclass
class ChainedTelemetryEvent:
    """A single cryptographically chained telemetry event."""
    index: int
    event_type: str
    payload: Dict[str, Any]
    prev_hash: str
    event_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "event_type": self.event_type,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "event_hash": self.event_hash,
        }


class CryptographicTelemetryEngine:
    """Constructs and verifies SHA-256 chained telemetry ledgers and dashboards."""

    def __init__(self, compiler_id: str = "SystemG3b"):
        self.compiler_id = compiler_id
        self.events: List[ChainedTelemetryEvent] = []
        self._last_hash = GENESIS_HASH

    @staticmethod
    def _compute_hash(prev_hash: str, event_type: str, payload: Dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        raw = f"{prev_hash}|{event_type}|{canonical}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def record_event(self, event_type: str, payload: Dict[str, Any]) -> ChainedTelemetryEvent:
        """Appends a new event to the SHA-256 hash chain."""
        idx = len(self.events)
        ev_hash = self._compute_hash(self._last_hash, event_type, payload)
        ev = ChainedTelemetryEvent(
            index=idx,
            event_type=event_type,
            payload=payload,
            prev_hash=self._last_hash,
            event_hash=ev_hash,
        )
        self.events.append(ev)
        self._last_hash = ev_hash
        return ev

    @property
    def chain_head_hash(self) -> str:
        return self._last_hash

    @classmethod
    def verify_ledger_integrity(cls, ledger_data: Dict[str, Any]) -> bool:
        """Independently re-computes the entire SHA-256 hash chain to verify zero tampering."""
        events = ledger_data.get("hash_chain_events", [])
        curr_hash = GENESIS_HASH
        for idx, ev in enumerate(events):
            if ev.get("index") != idx:
                return False
            if ev.get("prev_hash") != curr_hash:
                return False
            expected = cls._compute_hash(curr_hash, ev["event_type"], ev["payload"])
            if ev.get("event_hash") != expected:
                return False
            curr_hash = expected
        return ledger_data.get("chain_head_hash") == curr_hash

    def emit_telemetry_artifacts(
        self,
        output_dir: Union[str, Path],
        soc_id: str,
        ledger: ThermodynamicLedger,
        argon_deliberation_tokens: int,
        flash_emission_tokens: int,
        argon_verification_tokens: int,
        remediation_events: List[Dict[str, Any]],
        stack_trace: List[Dict[str, Any]],
        test_execution_witness: Dict[str, Any],
        daughter_witness: Optional[Dict[str, Any]] = None,
        subagent_witnesses: Optional[List[Dict[str, Any]]] = None,
        app_output_dir: Optional[Union[str, Path]] = None,
        app_test_witness: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Measures physical disk files, seals the cryptographic chain, and writes JSON + Markdown artifacts."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        # Measure physical tokens of emitted code files before writing telemetry files
        disk_measurement = PhysicalTokenMeter.measure_directory(out_path)
        app_measurement: Optional[Dict[str, Any]] = None
        if app_output_dir is not None:
            app_path = Path(app_output_dir).resolve()
            if app_path.exists():
                app_measurement = PhysicalTokenMeter.measure_directory(app_path)

        witness_list = list(subagent_witnesses or [])
        live_subagents_count = sum(1 for w in witness_list if w.get("is_live_agy_subagent", False))

        # Record stack trace & subagent spawning summary event
        self.record_event("STACK_TRACE_SEALED", {
            "total_stack_operations": len(stack_trace),
            "remediation_count": len(remediation_events),
            "live_subagents_spawned_count": live_subagents_count,
            "recorded_subagent_witnesses_count": len(witness_list),
        })

        # Record physical disk measurement event
        self.record_event("DISK_SUBSTRATE_MEASURED", {
            "emitted_file_count": disk_measurement["file_count"],
            "emitted_physical_tokens": disk_measurement["total_tokens"],
            "files": disk_measurement["files"],
            "app_file_count": app_measurement["file_count"] if app_measurement else 0,
            "app_physical_tokens": app_measurement["total_tokens"] if app_measurement else 0,
        })

        # Record live test execution witness event
        self.record_event("SUBSTRATE_TEST_WITNESS", test_execution_witness)

        if app_test_witness is not None:
            self.record_event("APP_SUBSTRATE_TEST_WITNESS", app_test_witness)

        if daughter_witness is not None:
            self.record_event("QUINE_DAUGHTER_WITNESS", daughter_witness)

        # Record final thermodynamic seal
        thermo_dict = ledger.to_dict()
        thermo_dict["argon_deliberation_tokens"] = argon_deliberation_tokens
        thermo_dict["flash_emission_tokens"] = flash_emission_tokens
        thermo_dict["argon_verification_tokens"] = argon_verification_tokens
        thermo_dict["emitted_disk_tokens"] = disk_measurement["total_tokens"]
        thermo_dict["app_disk_tokens"] = app_measurement["total_tokens"] if app_measurement else 0
        thermo_dict["total_combined_disk_tokens"] = (
            disk_measurement["total_tokens"] + (app_measurement["total_tokens"] if app_measurement else 0)
        )
        thermo_dict["live_subagents_spawned_count"] = live_subagents_count
        self.record_event("THERMODYNAMIC_LEDGER_SEALED", thermo_dict)

        ledger_payload: Dict[str, Any] = {
            "compiler_id": self.compiler_id,
            "soc_id": soc_id,
            "chain_head_hash": self.chain_head_hash,
            "total_chained_events": len(self.events),
            "thermodynamics": thermo_dict,
            "subagent_witnesses": witness_list,
            "live_subagents_spawned_count": live_subagents_count,
            "disk_substrate": disk_measurement,
            "app_substrate": app_measurement,
            "test_execution_witness": test_execution_witness,
            "app_test_execution_witness": app_test_witness,
            "remediation_events": remediation_events,
            "daughter_witness": daughter_witness,
            "hash_chain_events": [e.to_dict() for e in self.events],
        }

        ledger_file = out_path / "telemetry_ledger.json"
        ledger_file.write_text(json.dumps(ledger_payload, indent=2, sort_keys=True), encoding="utf-8")

        dashboard_md = self._render_markdown_dashboard(ledger_payload)
        dashboard_file = out_path / "telemetry_dashboard.md"
        dashboard_file.write_text(dashboard_md, encoding="utf-8")

        return ledger_payload

    def _render_markdown_dashboard(self, data: Dict[str, Any]) -> str:
        thermo = data["thermodynamics"]
        disk = data["disk_substrate"]
        app_disk = data.get("app_substrate")
        witness = data["test_execution_witness"]
        app_witness = data.get("app_test_execution_witness")
        daughter = data.get("daughter_witness")
        subagents = data.get("subagent_witnesses", [])
        live_sub_count = data.get("live_subagents_spawned_count", 0)

        predicted_spend = thermo.get("predicted_total_spend")
        pred_acc = thermo.get("prediction_accuracy_pct")
        pred_spend_str = f"`{predicted_spend:,}`" if predicted_spend is not None else "`N/A (Manual)`"
        pred_acc_str = f"`{pred_acc:.1f}%`" if pred_acc is not None else "`N/A`"
        exp_util_str = f"`{thermo.get('exploratory_utilization_pct', 0.0):.1f}%`"
        tot_util_str = f"`{thermo.get('utilization_pct', 0.0):.1f}%`"
        subagent_status_str = (
            f"✅ `{live_sub_count}` live AGY `invoke_subagent` worker(s) verified"
            if live_sub_count > 0
            else "⚠️ `0` live `invoke_subagent` calls (Executed via in-process deterministic fallback)"
        )

        lines = [
            f"# 📊 Live Cryptographic Telemetry Dashboard: `{data['soc_id']}`",
            "",
            f"- **Compiler Identity:** `{data['compiler_id']}`",
            f"- **SHA-256 Chain Head Witness:** `{data['chain_head_hash']}`",
            f"- **Chained Cryptographic Events:** `{data['total_chained_events']}`",
            f"- **Live AGY Subagent Spawning (`invoke_subagent`):** {subagent_status_str}",
            f"- **Substrate Test Exit Code:** `{witness.get('exit_code')}` (`{witness.get('tests_run', 0)}` tests passing)",
        ]
        if app_witness:
            lines.append(
                f"- **App Test Suite Exit Code:** `{app_witness.get('exit_code')}` (`{app_witness.get('tests_run', 0)}` tests passing)"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 1. Thermodynamic Capital & Dual-Model Token Ledger (`[L1-G3B-014]`)",
            "",
            "| Metric | Token / Physical Value | Pool / Model Attribution |",
            "| :--- | :---: | :--- |",
            f"| **Total Allocated Budget** | `{thermo['total_budget']:,}` | Calibrated 60/40 Thermodynamic Envelope |",
            f"| **Predicted Total Spend** | {pred_spend_str} | Pre-Execution `DynamicBudgetCalibrator` Estimate |",
            f"| **Prediction Accuracy** | {pred_acc_str} | Predicted vs. Actual Physical BPE Spend (`{thermo['total_spent']:,}` tokens) |",
            f"| **Exploratory Pool Cap (60%)** | `{thermo['exploratory_cap']:,}` | Generative & Deliberative Ceiling ({exp_util_str} utilized) |",
            f"| **Protected Pool Floor (40%)** | `{thermo['protected_floor']:,}` | Immutable Verification Sink Floor |",
            f"| **Gemini 4 Argon Deliberation** | `{thermo['argon_deliberation_tokens']:,}` | The Brain (SoC + Stack Decomposition) |",
            f"| **Gemini 3.8 Flash Leaf Emission** | `{thermo['flash_emission_tokens']:,}` | The Muscle (Indivisible Leaf Synthesis) |",
            f"| **Gemini 4 Argon Verification Sinks** | `{thermo['argon_verification_tokens']:,}` | The Brain (Protected Zero-Trust Audits) |",
            f"| **Total Exploratory Spent** | `{thermo['exploratory_spent']:,}` | `{thermo['exploratory_remaining']:,}` remaining ({exp_util_str} pool utilization) |",
            f"| **Total Protected Spent** | `{thermo['protected_spent']:,}` | `{thermo['protected_remaining']:,}` remaining |",
            f"| **Total Budget Spent** | `{thermo['total_spent']:,}` | {tot_util_str} overall budget utilization |",
            f"| **Emitted Epoch Disk Tokens** | `{disk['total_tokens']:,}` | Measured across `{disk['file_count']}` compiler epoch files |",
            f"| **Emitted App Directory Tokens** | `{thermo.get('app_disk_tokens', 0):,}` | Measured across `{app_disk['file_count'] if app_disk else 0}` application files |",
            f"| **Landauer Bits Erased** | `{thermo['bits_erased']:,}` bits | Discarded defective leaf attempts |",
            f"| **Landauer Heat Dissipated ($Q$)** | `{thermo['dissipated_joules']:.6e}` J | $Q = k_B T \\ln(2) \\cdot \\text{{bits}}$ at $T=300\\text{{K}}$ |",
            "",
            "---",
            "",
            "## 2. Subagent Spawning & Dual-Model Routing Witness (`[L1-G3B-014]`)",
            "",
            f"- **Status:** {subagent_status_str}",
        ])

        if subagents:
            lines.extend([
                "",
                "| Task ID | Subagent Role | Assigned Model Tier | Conversation ID | Total BPE Tokens | Live AGY Subagent |",
                "| :--- | :--- | :--- | :--- | :---: | :---: |",
            ])
            for sw in subagents:
                lines.append(
                    f"| `{sw['task_id']}` | `{sw['subagent_role']}` | `{sw['assigned_model']}` | "
                    f"`{sw['conversation_id']}` | `{sw['total_bpe_tokens']:,}` | `{sw['is_live_agy_subagent']}` |"
                )

        lines.extend([
            "",
            "---",
            "",
            "## 3. Emitted Physical Files on Disk (`[NEG-G1B-001]`)",
            "",
            "| Relative File Path | Physical BPE Tokens |",
            "| :--- | :---: |",
        ])
        for rel_path, tok_count in sorted(disk["files"].items()):
            lines.append(f"| `{rel_path}` | `{tok_count:,}` |")

        if app_disk and app_disk.get("files"):
            lines.extend([
                "",
                "### Full Application Directory (`apps/<app_id>/`) Physical Files",
                "",
                "| App File Path | Physical BPE Tokens |",
                "| :--- | :---: |",
            ])
            for rel_path, tok_count in sorted(app_disk["files"].items()):
                lines.append(f"| `{rel_path}` | `{tok_count:,}` |")

        if daughter:
            lines.extend([
                "",
                "---",
                "",
                "## 4. Quine Daughter Isolation Witness (`G3b -> G3b' -> Downstream App`)",
                "",
                f"- **Daughter Subprocess Exit Code:** `{daughter.get('daughter_exit_code')}`",
                f"- **Downstream Target SoC:** `{daughter.get('downstream_soc_id')}`",
                f"- **Daughter Chain Head Hash:** `{daughter.get('daughter_chain_head_hash')}`",
                f"- **Downstream Emitted Files:** `{daughter.get('downstream_file_count')}`",
                f"- **Downstream Physical Tokens:** `{daughter.get('downstream_physical_tokens')}`",
                f"- **Daughter Prediction Accuracy:** `{daughter.get('daughter_prediction_accuracy_pct')}%`",
                f"- **Daughter Exploratory Utilization:** `{daughter.get('daughter_exploratory_utilization_pct')}%`",
            ])

        lines.extend([
            "",
            "---",
            "",
            "## 5. SHA-256 Cryptographic Event Chain",
            "",
            "| Index | Event Type | Previous Hash (Prefix) | Event Hash (SHA-256) |",
            "| :---: | :--- | :--- | :--- |",
        ])
        for ev in data["hash_chain_events"]:
            lines.append(
                f"| `{ev['index']}` | `{ev['event_type']}` | `{ev['prev_hash'][:12]}...` | `{ev['event_hash']}` |"
            )

        return "\n".join(lines) + "\n"
