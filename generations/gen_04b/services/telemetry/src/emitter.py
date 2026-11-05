"""Zero-Dependency Sovereign Telemetry Client SDK (`emitter.py`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G3B-011] Universal Compositional Contract IR (MeshTransaction).
- [L1-G3B-012] Dedicated Non-Loopback Network Topology.
- [L1-G3B-017] SHA-256 Chained Cryptographic Telemetry & Merkle Leaves.
- [L1-G3B-018] Non-Blocking Ingress & Landauer Thermodynamic Equilibrium.
- [INV-G4B-CAUSAL-001] Physical Grounding Witness Emission.
- [NEG-G1B-002] Anti-Mock Subprocess Entrypoint Smoke Invariant.
- Dual Synchronous (`TelemetryEmitter`) and Asynchronous (`AsyncTelemetryEmitter`) APIs.
- 50ms Circuit Breaker with Local Spillover Ledger Fallback (`.scratch/spillover_telemetry.jsonl`).
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

try:
    from .telemetry_vault import MeshTransaction, assert_non_loopback
except ImportError:
    try:
        from generations.gen_04b.services.telemetry.src.telemetry_vault import (
            MeshTransaction,
            assert_non_loopback,
        )
    except ImportError:
        from telemetry_vault import MeshTransaction, assert_non_loopback


DEFAULT_INGEST_URL = "http://127.0.0.1:8446/api/v1/telemetry/ingest"
DEFAULT_SOURCE_SERVICE = "services/builder"
DEFAULT_SOURCE_ENDPOINT = "192.168.40.20:8442"
DEFAULT_TARGET_SERVICE = "services/telemetry"
DEFAULT_TARGET_ENDPOINT = "192.168.40.40:8446"
DEFAULT_CIRCUIT_BREAKER_TIMEOUT = 0.05  # 50ms


def _find_scratch_spillover_path() -> Path:
    """Discovers designated .scratch/spillover_telemetry.jsonl path."""
    current = Path.cwd()
    if (current / ".scratch").exists() or (current / "generations").exists():
        return current / ".scratch" / "spillover_telemetry.jsonl"
    # Walk parents if nested
    for p in current.parents:
        if (p / ".scratch").exists() or (p / "generations").exists():
            return p / ".scratch" / "spillover_telemetry.jsonl"
    return Path(".scratch/spillover_telemetry.jsonl")


class TelemetryEmitter:
    """Synchronous zero-dependency client for emitting MeshTransactions to IngestServer."""

    def __init__(
        self,
        endpoint_url: str = DEFAULT_INGEST_URL,
        source_service: str = DEFAULT_SOURCE_SERVICE,
        source_endpoint: str = DEFAULT_SOURCE_ENDPOINT,
        target_service: str = DEFAULT_TARGET_SERVICE,
        target_endpoint: str = DEFAULT_TARGET_ENDPOINT,
        timeout_seconds: float = DEFAULT_CIRCUIT_BREAKER_TIMEOUT,
        spillover_path: Optional[Path] = None,
        causal_task_id: str = "task_root",
    ) -> None:
        assert_non_loopback(source_endpoint, f"TelemetryEmitter source_endpoint ({source_service})")
        assert_non_loopback(target_endpoint, f"TelemetryEmitter target_endpoint ({target_service})")

        self.endpoint_url = endpoint_url
        self.source_service = source_service
        self.source_endpoint = source_endpoint
        self.target_service = target_service
        self.target_endpoint = target_endpoint
        self.timeout_seconds = timeout_seconds
        self.spillover_path = spillover_path or _find_scratch_spillover_path()
        self.causal_task_id = causal_task_id

        self.logical_clock: int = 0
        self.prev_tx_hash: str = "0" * 64
        self.step_index: int = 0

    def _next_clock_and_hash(self, tx_hash: str) -> None:
        self.logical_clock += 1
        self.prev_tx_hash = tx_hash
        self.step_index += 1

    def _append_spillover(self, tx: MeshTransaction) -> None:
        try:
            self.spillover_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.spillover_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(tx.to_dict()) + "\n")
        except Exception:
            pass

    def emit(self, tx: MeshTransaction) -> bool:
        """Sends a MeshTransaction to the IngestServer with 50ms circuit breaker."""
        tx.validate_invariants()
        payload_bytes = json.dumps(tx.to_dict()).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint_url,
            data=payload_bytes,
            headers={"Content-Type": "application/json", "Connection": "close"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                if resp.status in (200, 202):
                    return True
                self._append_spillover(tx)
                return False
        except Exception:
            self._append_spillover(tx)
            return False

    def emit_phase(
        self,
        phase_name: str,
        status: str = "SUCCESS",
        details: Optional[Dict[str, Any]] = None,
        bpe_tokens: int = 0,
    ) -> MeshTransaction:
        """Emits compilation phase transition."""
        payload_data = details or {}
        payload_data["phase_name"] = phase_name

        clock = self.logical_clock + 1
        tx_id = f"tx_phase_{time.time_ns()}_{clock}"
        capital = "PROTECTED" if any(k in phase_name for k in ("VERIFICATION", "GROUNDING", "AUDIT")) else "EXPLORATORY"

        tx = MeshTransaction.create(
            transaction_id=tx_id,
            prev_transaction_hash=self.prev_tx_hash,
            logical_clock=clock,
            causal_task_id=self.causal_task_id,
            step_index=self.step_index,
            phase=phase_name,
            source_service=self.source_service,
            source_endpoint=self.source_endpoint,
            target_service=self.target_service,
            target_endpoint=self.target_endpoint,
            channel_id=f"channel_{self.source_service.split('/')[-1]}_{self.target_service.split('/')[-1]}",
            verb="TRANSITION_PHASE",
            payload_summary=f"Phase Transition: {phase_name} ({status})",
            payload_data=payload_data,
            bpe_tokens_in=bpe_tokens,
            capital_partition=capital,
            status=status,
            target_symbol_urn=f"urn:meta-axioma:phase:{phase_name.lower()}",
        )
        self._next_clock_and_hash(tx.transaction_hash)
        self.emit(tx)
        return tx

    def emit_leaf(
        self,
        leaf_name: str,
        file_path: str,
        byte_count: int,
        sha256_digest: str,
        tokens_spent: int = 0,
    ) -> MeshTransaction:
        """Emits source code leaf physical grounding witness ([INV-G4B-CAUSAL-001])."""
        if byte_count <= 0:
            raise ValueError(f"emit_leaf requires non-zero byte_count, got {byte_count}")
        if len(sha256_digest) != 64:
            raise ValueError(f"emit_leaf requires 64-char sha256_digest, got {len(sha256_digest)}")

        clock = self.logical_clock + 1
        tx_id = f"tx_leaf_{time.time_ns()}_{clock}"
        payload_data = {
            "leaf_name": leaf_name,
            "file_path": str(file_path),
            "byte_count": byte_count,
            "sha256": sha256_digest,
            "tokens_spent": tokens_spent,
        }

        tx = MeshTransaction.create(
            transaction_id=tx_id,
            prev_transaction_hash=self.prev_tx_hash,
            logical_clock=clock,
            causal_task_id=self.causal_task_id,
            step_index=self.step_index,
            phase="PHASE_2A_SYNTHESIS",
            source_service=self.source_service,
            source_endpoint=self.source_endpoint,
            target_service=self.target_service,
            target_endpoint=self.target_endpoint,
            channel_id="channel_builder_telemetry",
            verb="EMIT_CODE_LEAF",
            payload_summary=f"Emitted Code Leaf: {leaf_name} ({byte_count} bytes)",
            payload_data=payload_data,
            bpe_tokens_in=tokens_spent,
            bits_erased=byte_count * 8,
            capital_partition="EXPLORATORY",
            status="SUCCESS",
            target_symbol_urn=f"urn:meta-axioma:leaf:{leaf_name}",
        )
        self._next_clock_and_hash(tx.transaction_hash)
        self.emit(tx)
        return tx

    def emit_verification(
        self,
        test_suite: str,
        total_tests: int,
        passed: int,
        failed: int,
        witness_digest: str,
        duration_ns: int = 1_000_000,
    ) -> MeshTransaction:
        """Emits formal verification or test suite outcome under protected capital."""
        clock = self.logical_clock + 1
        tx_id = f"tx_verif_{time.time_ns()}_{clock}"
        status = "SUCCESS" if failed == 0 else "FAILED"
        payload_data = {
            "test_suite": test_suite,
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "witness_digest": witness_digest,
        }

        tx = MeshTransaction.create(
            transaction_id=tx_id,
            prev_transaction_hash=self.prev_tx_hash,
            logical_clock=clock,
            causal_task_id=self.causal_task_id,
            step_index=self.step_index,
            phase="PHASE_2C_VERIFICATION",
            source_service="services/audit",
            source_endpoint="192.168.40.30:8444",
            target_service=self.target_service,
            target_endpoint=self.target_endpoint,
            channel_id="channel_audit_telemetry",
            verb="VERIFY_TEST_SUITE",
            payload_summary=f"Test Suite: {test_suite} ({passed}/{total_tests} passed)",
            payload_data=payload_data,
            duration_ns=duration_ns,
            capital_partition="PROTECTED",
            status=status,
            target_symbol_urn=f"urn:meta-axioma:test_suite:{test_suite}",
            verification_witness=witness_digest,
        )
        self._next_clock_and_hash(tx.transaction_hash)
        self.emit(tx)
        return tx

    def emit_subprocess_smoke(
        self,
        entrypoint: str,
        exit_code: int,
        stdout_snippet: str,
        duration_ns: int = 1_000_000,
        success: bool = True,
    ) -> MeshTransaction:
        """Emits Anti-Mock Subprocess Entrypoint Smoke Verification ([NEG-G1B-002])."""
        clock = self.logical_clock + 1
        tx_id = f"tx_smoke_{time.time_ns()}_{clock}"
        status = "SUCCESS" if (exit_code == 0 and success) else "FAILED"
        witness = hashlib.sha256(stdout_snippet.encode("utf-8")).hexdigest()
        payload_data = {
            "entrypoint": entrypoint,
            "exit_code": exit_code,
            "stdout_snippet": stdout_snippet[:500],
            "success": success,
        }

        tx = MeshTransaction.create(
            transaction_id=tx_id,
            prev_transaction_hash=self.prev_tx_hash,
            logical_clock=clock,
            causal_task_id=self.causal_task_id,
            step_index=self.step_index,
            phase="PHASE_2C_VERIFICATION",
            source_service="services/audit",
            source_endpoint="192.168.40.30:8444",
            target_service=self.target_service,
            target_endpoint=self.target_endpoint,
            channel_id="channel_audit_telemetry",
            verb="SUBPROCESS_SMOKE_TEST",
            payload_summary=f"Subprocess Smoke Entrypoint: {entrypoint} (Exit {exit_code})",
            payload_data=payload_data,
            duration_ns=duration_ns,
            capital_partition="PROTECTED",
            status=status,
            target_symbol_urn=f"urn:meta-axioma:smoke:{entrypoint}",
            verification_witness=witness,
        )
        self._next_clock_and_hash(tx.transaction_hash)
        self.emit(tx)
        return tx

    def emit_tool_call(
        self,
        tool_name: str,
        args_summary: str,
        duration_ns: int = 1_000_000,
        success: bool = True,
        error: Optional[str] = None,
    ) -> MeshTransaction:
        """Emits programmatic tool invocation event."""
        clock = self.logical_clock + 1
        tx_id = f"tx_tool_{time.time_ns()}_{clock}"
        status = "SUCCESS" if success else "FAILED"
        payload_data = {
            "tool_name": tool_name,
            "args_summary": args_summary,
            "error": error,
        }

        tx = MeshTransaction.create(
            transaction_id=tx_id,
            prev_transaction_hash=self.prev_tx_hash,
            logical_clock=clock,
            causal_task_id=self.causal_task_id,
            step_index=self.step_index,
            phase="PHASE_2A_SYNTHESIS",
            source_service=self.source_service,
            source_endpoint=self.source_endpoint,
            target_service=self.target_service,
            target_endpoint=self.target_endpoint,
            channel_id="channel_builder_telemetry",
            verb="TOOL_CALL",
            payload_summary=f"Tool Execution: {tool_name} ({status})",
            payload_data=payload_data,
            duration_ns=duration_ns,
            capital_partition="EXPLORATORY",
            status=status,
            target_symbol_urn=f"urn:meta-axioma:tool:{tool_name}",
        )
        self._next_clock_and_hash(tx.transaction_hash)
        self.emit(tx)
        return tx

    def emit_subagent_dispatch(
        self,
        subagent_id: str,
        role: str,
        model: str,
        prompt_tokens: int = 0,
    ) -> MeshTransaction:
        """Emits distributed subagent dispatch event ([L1-G4B-001])."""
        clock = self.logical_clock + 1
        tx_id = f"tx_subagent_{time.time_ns()}_{clock}"
        payload_data = {
            "subagent_id": subagent_id,
            "role": role,
            "model": model,
            "prompt_tokens": prompt_tokens,
        }

        tx = MeshTransaction.create(
            transaction_id=tx_id,
            prev_transaction_hash=self.prev_tx_hash,
            logical_clock=clock,
            causal_task_id=self.causal_task_id,
            step_index=self.step_index,
            phase="PHASE_1_RESEARCH_GATE" if any(w in role.lower() for w in ("brain", "research")) else "PHASE_2A_SYNTHESIS",
            source_service="services/orchestrator",
            source_endpoint="192.168.40.50:8448",
            target_service=self.target_service,
            target_endpoint=self.target_endpoint,
            channel_id="channel_orchestrator_telemetry",
            verb="DISPATCH_SUBAGENT",
            payload_summary=f"Dispatched Subagent: {role} ({model})",
            payload_data=payload_data,
            bpe_tokens_in=prompt_tokens,
            capital_partition="EXPLORATORY",
            status="SUCCESS",
            subagent_id=subagent_id,
            subagent_role=role,
            target_symbol_urn=f"urn:meta-axioma:subagent:{subagent_id}",
        )
        self._next_clock_and_hash(tx.transaction_hash)
        self.emit(tx)
        return tx

    def emit_undo_event(
        self,
        checkpoint_id: str,
        bits_restored: int = 0,
    ) -> MeshTransaction:
        """Emits functorial rollback event ([L1-008] Thermodynamic Reversibility)."""
        clock = self.logical_clock + 1
        tx_id = f"tx_undo_{time.time_ns()}_{clock}"
        payload_data = {
            "checkpoint_id": checkpoint_id,
            "bits_restored": bits_restored,
        }

        tx = MeshTransaction.create(
            transaction_id=tx_id,
            prev_transaction_hash=self.prev_tx_hash,
            logical_clock=clock,
            causal_task_id=self.causal_task_id,
            step_index=self.step_index,
            phase="PHASE_2C_VERIFICATION",
            source_service="services/telemetry",
            source_endpoint=self.target_endpoint,
            target_service=self.source_service,
            target_endpoint=self.source_endpoint,
            channel_id="channel_telemetry_builder",
            verb="UNDO_CHECKPOINT",
            payload_summary=f"Functorial Rollback: Checkpoint {checkpoint_id} ({bits_restored} bits restored)",
            payload_data=payload_data,
            bits_erased=bits_restored,
            capital_partition="PROTECTED",
            status="SUCCESS",
            target_symbol_urn=f"urn:meta-axioma:checkpoint:{checkpoint_id}",
        )
        self._next_clock_and_hash(tx.transaction_hash)
        self.emit(tx)
        return tx

    def drain_spillover(self) -> int:
        """Drains local spillover buffer to IngestServer when connectivity is restored."""
        if not self.spillover_path.exists() or self.spillover_path.stat().st_size == 0:
            return 0

        with open(self.spillover_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            return 0

        drained_count = 0
        remaining_lines = []

        # Batch drain to IngestServer
        batch_records = []
        for line in lines:
            try:
                batch_records.append(json.loads(line))
            except Exception:
                pass

        if batch_records:
            payload_bytes = json.dumps(batch_records).encode("utf-8")
            req = urllib.request.Request(
                self.endpoint_url,
                data=payload_bytes,
                headers={"Content-Type": "application/json", "Connection": "close"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_seconds * 4) as resp:
                    if resp.status in (200, 202):
                        drained_count = len(batch_records)
                    else:
                        remaining_lines = lines
            except Exception:
                remaining_lines = lines

        # Rewrite remaining un-drained lines
        if remaining_lines:
            with open(self.spillover_path, "w", encoding="utf-8") as f:
                for line in remaining_lines:
                    f.write(line + "\n")
        else:
            try:
                self.spillover_path.unlink()
            except Exception:
                with open(self.spillover_path, "w", encoding="utf-8") as f:
                    f.write("")

        return drained_count


class AsyncTelemetryEmitter:
    """Asynchronous zero-dependency client for emitting MeshTransactions inside event loops."""

    def __init__(
        self,
        endpoint_url: str = DEFAULT_INGEST_URL,
        source_service: str = DEFAULT_SOURCE_SERVICE,
        source_endpoint: str = DEFAULT_SOURCE_ENDPOINT,
        target_service: str = DEFAULT_TARGET_SERVICE,
        target_endpoint: str = DEFAULT_TARGET_ENDPOINT,
        timeout_seconds: float = DEFAULT_CIRCUIT_BREAKER_TIMEOUT,
        spillover_path: Optional[Path] = None,
        causal_task_id: str = "task_root",
    ) -> None:
        self._sync_emitter = TelemetryEmitter(
            endpoint_url=endpoint_url,
            source_service=source_service,
            source_endpoint=source_endpoint,
            target_service=target_service,
            target_endpoint=target_endpoint,
            timeout_seconds=timeout_seconds,
            spillover_path=spillover_path,
            causal_task_id=causal_task_id,
        )

    @property
    def logical_clock(self) -> int:
        return self._sync_emitter.logical_clock

    @property
    def prev_tx_hash(self) -> str:
        return self._sync_emitter.prev_tx_hash

    async def emit(self, tx: MeshTransaction) -> bool:
        return await asyncio.to_thread(self._sync_emitter.emit, tx)

    async def emit_phase(
        self,
        phase_name: str,
        status: str = "SUCCESS",
        details: Optional[Dict[str, Any]] = None,
        bpe_tokens: int = 0,
    ) -> MeshTransaction:
        return await asyncio.to_thread(
            self._sync_emitter.emit_phase, phase_name, status, details, bpe_tokens
        )

    async def emit_leaf(
        self,
        leaf_name: str,
        file_path: str,
        byte_count: int,
        sha256_digest: str,
        tokens_spent: int = 0,
    ) -> MeshTransaction:
        return await asyncio.to_thread(
            self._sync_emitter.emit_leaf,
            leaf_name,
            file_path,
            byte_count,
            sha256_digest,
            tokens_spent,
        )

    async def emit_verification(
        self,
        test_suite: str,
        total_tests: int,
        passed: int,
        failed: int,
        witness_digest: str,
        duration_ns: int = 1_000_000,
    ) -> MeshTransaction:
        return await asyncio.to_thread(
            self._sync_emitter.emit_verification,
            test_suite,
            total_tests,
            passed,
            failed,
            witness_digest,
            duration_ns,
        )

    async def emit_subprocess_smoke(
        self,
        entrypoint: str,
        exit_code: int,
        stdout_snippet: str,
        duration_ns: int = 1_000_000,
        success: bool = True,
    ) -> MeshTransaction:
        return await asyncio.to_thread(
            self._sync_emitter.emit_subprocess_smoke,
            entrypoint,
            exit_code,
            stdout_snippet,
            duration_ns,
            success,
        )

    async def emit_tool_call(
        self,
        tool_name: str,
        args_summary: str,
        duration_ns: int = 1_000_000,
        success: bool = True,
        error: Optional[str] = None,
    ) -> MeshTransaction:
        return await asyncio.to_thread(
            self._sync_emitter.emit_tool_call,
            tool_name,
            args_summary,
            duration_ns,
            success,
            error,
        )

    async def emit_subagent_dispatch(
        self,
        subagent_id: str,
        role: str,
        model: str,
        prompt_tokens: int = 0,
    ) -> MeshTransaction:
        return await asyncio.to_thread(
            self._sync_emitter.emit_subagent_dispatch,
            subagent_id,
            role,
            model,
            prompt_tokens,
        )

    async def emit_undo_event(
        self,
        checkpoint_id: str,
        bits_restored: int = 0,
    ) -> MeshTransaction:
        return await asyncio.to_thread(
            self._sync_emitter.emit_undo_event, checkpoint_id, bits_restored
        )

    async def drain_spillover(self) -> int:
        return await asyncio.to_thread(self._sync_emitter.drain_spillover)
