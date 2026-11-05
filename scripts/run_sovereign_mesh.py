#!/usr/bin/env python3
"""Sovereign Service Mesh Master Launcher (`run_sovereign_mesh.py`).

Boots all 5 Generation 4b Sovereign Service Enclaves concurrently:
  1. Sovereign Research Service (Default: 192.168.40.10:8440)
  2. Sovereign Builder Enclave (Default: 192.168.40.20:8442)
  3. Sovereign Audit & Verification Service (Default: 192.168.40.30:8444)
  4. Sovereign Telemetry & Evaluation Service (Default: 192.168.40.40:8446 Ingest, 8447 Cockpit HUD)
  5. Sovereign Governance & Safety Service (Default: 192.168.40.50:8448)

Networking Profile:
  - If 192.168.40.X is reachable on the OS (e.g. via 'sudo ./scripts/setup_macos_subnet.sh'
    or Docker bridge), binds directly to each dedicated IP (SOVEREIGN_MESH).
  - If not aliased, automatically falls back to 127.0.0.1 on distinct ports (LOCAL_IPC)
    with a clear warning banner. Zero crashes, 100% verifiable.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
import random
import socket
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# Setup paths
REPO_ROOT = Path(__file__).resolve().parent.parent
GEN_04B = REPO_ROOT / "generations" / "gen_04b"
TELEMETRY_SRC = GEN_04B / "services" / "telemetry" / "src"
COCKPIT_DIR = GEN_04B / "services" / "telemetry" / "cockpit"

for p in [REPO_ROOT, GEN_04B, TELEMETRY_SRC]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from generations.gen_04b.services.telemetry.src.ingest_server import IngestServer
    from generations.gen_04b.services.telemetry.src.cockpit_server import CockpitServer, Profile
    from generations.gen_04b.services.telemetry.src.telemetry_vault import MeshTransaction, TelemetryVault
    from generations.gen_04b.services.telemetry.src.rollback_engine import RollbackEngine
except ImportError:
    from ingest_server import IngestServer
    from cockpit_server import CockpitServer, Profile
    from telemetry_vault import MeshTransaction, TelemetryVault
    from rollback_engine import RollbackEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("sovereign_mesh")


def can_bind_ip(ip: str, test_port: int = 18999) -> bool:
    """Checks whether the operating system allows binding to the given IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((ip, test_port))
        s.close()
        return True
    except OSError:
        s.close()
        return False


def find_available_port(host: str, starting_port: int, reserved_ports: Optional[set[int]] = None, max_attempts: int = 20) -> int:
    """Finds the first available port starting from starting_port that is not in reserved_ports."""
    reserved = reserved_ports or set()
    for p in range(starting_port, starting_port + max_attempts):
        if p in reserved:
            continue
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, p))
            s.close()
            return p
        except OSError:
            s.close()
            continue
    return starting_port


class SimpleHTTPService:
    """Lightweight native AsyncIO HTTP service for sovereign enclaves."""

    def __init__(self, name: str, host: str, port: int, metadata: Dict[str, Any]):
        self.name = name
        self.host = host
        self.port = port
        self.metadata = metadata
        self._server: Optional[asyncio.Server] = None
        self.request_count = 0

    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            line = await reader.readline()
            if not line:
                return
            req_str = line.decode("utf-8", errors="replace").strip()
            parts = req_str.split()
            if len(parts) < 2:
                return
            method, path = parts[0], parts[1]

            # Read remaining headers
            while True:
                h = await reader.readline()
                if not h or h == b"\r\n":
                    break

            self.request_count += 1
            payload: Dict[str, Any] = {
                "service": self.name,
                "host": self.host,
                "port": self.port,
                "status": "HEALTHY",
                "uptime_seconds": time.time() - self.start_time,
                "requests_served": self.request_count,
            }
            payload.update(self.metadata)

            if path in ("/health", "/healthz", "/"):
                body = json.dumps(payload, indent=2).encode("utf-8")
                status = "200 OK"
            else:
                body = json.dumps({"service": self.name, "path": path, "status": "ACK"}).encode("utf-8")
                status = "200 OK"

            resp = (
                f"HTTP/1.1 {status}\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"Access-Control-Allow-Origin: *\r\n"
                f"Connection: close\r\n\r\n"
            ).encode("utf-8") + body

            writer.write(resp)
            await writer.drain()
        except Exception as e:
            logger.debug("Request error on %s: %s", self.name, e)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def start(self) -> None:
        self.start_time = time.time()
        self._server = await asyncio.start_server(self.handle_request, self.host, self.port)
        logger.info("[ENCLAVE ONLINE] %-20s -> http://%s:%d/health", self.name, self.host, self.port)

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()


class SovereignMeshCluster:
    """Master orchestrator for all 5 Generation 4b Sovereign Services."""

    def __init__(
        self,
        mode: str = "auto",
        service: str = "all",
        enable_traffic: bool = True,
        research_port: int = 8440,
        builder_port: int = 8442,
        audit_port: int = 8444,
        ingest_port: int = 8446,
        cockpit_port: int = 8447,
        governance_port: int = 8448,
    ):
        self.mode = mode
        self.service = service.lower()
        self.enable_traffic = enable_traffic
        self.base_ports = {
            "research": research_port,
            "builder": builder_port,
            "audit": audit_port,
            "ingest": ingest_port,
            "cockpit": cockpit_port,
            "governance": governance_port,
        }
        self.active_ports: Dict[str, int] = {}
        self.services: List[SimpleHTTPService] = []
        self.telemetry_ingest: Optional[IngestServer] = None
        self.telemetry_cockpit: Optional[CockpitServer] = None
        self.vault: Optional[TelemetryVault] = None
        self._traffic_task: Optional[asyncio.Task] = None
        self._running = False

    def determine_network_profile(self) -> Tuple[str, Dict[str, str]]:
        """Determines whether to bind to sovereign IPs or local fallback."""
        sovereign_ips = {
            "research": "192.168.40.10",
            "builder": "192.168.40.20",
            "audit": "192.168.40.30",
            "telemetry": "192.168.40.40",
            "governance": "192.168.40.50",
        }

        if self.mode == "native":
            return "SOVEREIGN_MESH", sovereign_ips
        elif self.mode == "local":
            return "LOCAL_IPC", {k: "127.0.0.1" for k in sovereign_ips}

        # Auto-detect
        can_bind = can_bind_ip("192.168.40.10") and can_bind_ip("192.168.40.40")
        if can_bind:
            return "SOVEREIGN_MESH", sovereign_ips
        else:
            return "LOCAL_IPC", {k: "127.0.0.1" for k in sovereign_ips}

    async def start(self) -> None:
        self._running = True
        profile_name, ip_map = self.determine_network_profile()

        print("\n" + "=" * 80)
        print("  META-AXIOMA GENERATION 4b: SOVEREIGN SERVICE MESH CLUSTER")
        print("=" * 80)
        print(f"  Network Profile:  {profile_name}")
        if profile_name == "SOVEREIGN_MESH":
            print("  Interface Mode:   NATIVE DISCRETE SUBNET (192.168.40.0/24)")
            print("  Isolation:        Hardware/OS Alias Bound [L1-G3B-012]")
        else:
            print("  Interface Mode:   LOCAL PORT ISOLATION (127.0.0.1)")
            print("  Note:             To activate 192.168.40.0/24 on macOS, run:")
            print("                    sudo ./scripts/setup_macos_subnet.sh")
        print("=" * 80 + "\n")

        # Determine active ports (auto-selecting next available if base port occupied)
        ingest_host = ip_map["telemetry"]
        cockpit_host = ip_map["telemetry"]
        allocated: set[int] = set()
        self.active_ports = {}
        for svc_key in ["ingest", "cockpit", "research", "builder", "audit", "governance"]:
            h = ip_map["telemetry"] if svc_key in ("ingest", "cockpit") else ip_map[svc_key]
            p = find_available_port(h, self.base_ports[svc_key], reserved_ports=allocated)
            allocated.add(p)
            self.active_ports[svc_key] = p

        # 1. Telemetry Storage & Vault
        if self.service in ("all", "telemetry"):
            db_path = REPO_ROOT / ".scratch" / "live_mesh_vault.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self.vault = TelemetryVault(db_path=str(db_path), keyframe_interval=100)
            rollback_engine = RollbackEngine(self.vault)

            # 2. Ingest Server
            self.telemetry_ingest = IngestServer(
                vault=self.vault,
                host=ingest_host,
                port=self.active_ports["ingest"],
                allow_any_interface_for_testing=True,
                profile="SOVEREIGN_MESH" if profile_name == "SOVEREIGN_MESH" else "LOCAL_IPC",
            )
            await self.telemetry_ingest.start()
            logger.info("[ENCLAVE ONLINE] %-20s -> http://%s:%d/api/v1/telemetry/health", "Telemetry (Ingest)", ingest_host, self.active_ports["ingest"])

            # 3. Cockpit Server
            self.telemetry_cockpit = CockpitServer(
                vault=self.vault,
                ingest_server=self.telemetry_ingest,
                rollback_engine=rollback_engine,
                host=cockpit_host,
                port=self.active_ports["cockpit"],
                static_dir=str(COCKPIT_DIR),
                allow_any_interface_for_testing=True,
                profile=Profile.SOVEREIGN_MESH if profile_name == "SOVEREIGN_MESH" else Profile.LOCAL_IPC,
            )
            await self.telemetry_cockpit.start()
            logger.info("[ENCLAVE ONLINE] %-20s -> http://%s:%d/ (Cockpit HUD)", "Telemetry (Cockpit)", cockpit_host, self.active_ports["cockpit"])

        # 4. Research Service
        if self.service in ("all", "research"):
            svc_research = SimpleHTTPService(
                name="Research Service",
                host=ip_map["research"],
                port=self.active_ports["research"],
                metadata={
                    "role": "Epistemic Formulation & Waterloo SoC Normalization",
                    "urn": "urn:axioma:g4b:research:kernel#v1",
                    "zero_code_boundary": True,
                    "islands_active": 3,
                },
            )
            await svc_research.start()
            self.services.append(svc_research)

        # 5. Builder Enclave
        if self.service in ("all", "builder"):
            svc_builder = SimpleHTTPService(
                name="Builder Enclave",
                host=ip_map["builder"],
                port=self.active_ports["builder"],
                metadata={
                    "role": "Isolated Code Synthesis & Quine Crucible",
                    "urn": "urn:axioma:g4b:builder:enclave#v1",
                    "fractal_depth_max": 4,
                    "capital_ratio": "60% Exploratory / 40% Protected",
                },
            )
            await svc_builder.start()
            self.services.append(svc_builder)

        # 6. Audit Service
        if self.service in ("all", "audit"):
            svc_audit = SimpleHTTPService(
                name="Audit Service",
                host=ip_map["audit"],
                port=self.active_ports["audit"],
                metadata={
                    "role": "Z3 SMT Invariant Prover & Micro-Auditor Gate",
                    "urn": "urn:axioma:g4b:audit:kernel#v1",
                    "micro_auditors_active": 14,
                    "hermetic_checks": ["HERM-001", "HERM-002", "HERM-003", "HERM-004", "HERM-005"],
                },
            )
            await svc_audit.start()
            self.services.append(svc_audit)

        # 7. Governance Service
        if self.service in ("all", "governance"):
            svc_gov = SimpleHTTPService(
                name="Governance Service",
                host=ip_map["governance"],
                port=self.active_ports["governance"],
                metadata={
                    "role": "Executive Architectural Guard & Human Veto Invariants",
                    "urn": "urn:axioma:g4b:governance:kernel#v1",
                    "active_vetoes": ["NEG-GOV-GATE-001", "NEG-G1B-001", "NEG-G1B-002", "NEG-PRIVACY-001"],
                },
            )
            await svc_gov.start()
            self.services.append(svc_gov)

        print("\n" + "=" * 80)
        print("  SOVEREIGN MESH OPERATIONAL SUMMARY:")
        print("=" * 80)
        print(f"  • Telemetry Cockpit UI:  http://{cockpit_host}:{self.active_ports['cockpit']}/ (or http://localhost:{self.active_ports['cockpit']})")
        print(f"  • Telemetry Healthz:     http://{cockpit_host}:{self.active_ports['cockpit']}/healthz")
        print(f"  • Ingest Stream & SSE:   http://{ingest_host}:{self.active_ports['ingest']}/api/v1/telemetry/health")
        print(f"  • Research Service:      http://{ip_map['research']}:{self.active_ports['research']}/health")
        print(f"  • Builder Enclave:       http://{ip_map['builder']}:{self.active_ports['builder']}/health")
        print(f"  • Audit Service:         http://{ip_map['audit']}:{self.active_ports['audit']}/health")
        print(f"  • Governance Service:    http://{ip_map['governance']}:{self.active_ports['governance']}/health")
        print("=" * 80)
        print("  Press Ctrl+C to gracefully stop the mesh cluster.\n")

        # Start simulated live traffic if requested
        if self.enable_traffic:
            self._traffic_task = asyncio.create_task(self._generate_traffic_loop(ip_map))

    async def _generate_traffic_loop(self, ip_map: Dict[str, str]) -> None:
        """Emits periodic synthetic mesh transactions into IngestServer to showcase live telemetry."""
        logger.info("[TRAFFIC GENERATOR ACTIVE] Streaming inter-service telemetry transactions...")
        seq = 1000

        event_types = [
            ("research", "builder", "RFC_SPEC_ADJUSTMENT", 1500),
            ("builder", "audit", "EMIT_AST_MODULE", 2800),
            ("audit", "governance", "SMT_VERIFICATION_PASS", 850),
            ("governance", "telemetry", "SEAL_MERKLE_WITNESS", 420),
            ("builder", "telemetry", "THERMODYNAMIC_TOKEN_SPEND", 1240),
            ("research", "audit", "Z3_CONTRACT_PROOFS_SAT", 930),
            ("audit", "builder", "MICRO_AUDITOR_CLEAN_ROOM", 310),
        ]

        while self._running:
            try:
                await asyncio.sleep(random.uniform(1.2, 2.5))
                src_svc, dst_svc, ev_name, bpe_tokens = random.choice(event_types)
                seq += 1

                tx = MeshTransaction(
                    transaction_id=f"tx_mesh_{seq}_{int(time.time()*1000)%100000}",
                    sequence_number=seq,
                    timestamp_ns=time.time_ns(),
                    source_service=f"services/{src_svc}",
                    target_service=f"services/{dst_svc}",
                    payload_type=ev_name,
                    status="SUCCESS",
                    bpe_tokens=bpe_tokens,
                    latency_ms=round(random.uniform(2.1, 14.8), 2),
                    metadata={
                        "source_ip": f"{ip_map[src_svc]}",
                        "target_ip": f"{ip_map[dst_svc]}",
                        "state_checkpoint": f"chk_{seq}",
                        "landauer_dissipated_joules": f"{round(bpe_tokens * 1.38e-23 * 300 * 0.693, 22):.2e}",
                    },
                )
                if self.telemetry_ingest:
                    self.telemetry_ingest.enqueue(tx)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug("Error in traffic generator: %s", e)

    async def stop(self) -> None:
        self._running = False
        if self._traffic_task:
            self._traffic_task.cancel()
            try:
                await self._traffic_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopping sovereign services...")
        for svc in self.services:
            await svc.stop()

        if self.telemetry_cockpit:
            await self.telemetry_cockpit.stop()
        if self.telemetry_ingest:
            await self.telemetry_ingest.stop()
        if self.vault:
            self.vault.close()

        logger.info("All sovereign services cleanly stopped.")


def main():
    parser = argparse.ArgumentParser(description="Meta-Axioma Generation 4b Sovereign Service Mesh Launcher")
    parser.add_argument("--mode", choices=["auto", "native", "local"], default="auto", help="Networking profile")
    parser.add_argument(
        "--service",
        choices=["all", "research", "builder", "audit", "telemetry", "governance"],
        default="all",
        help="Target sovereign service to run (default: all)",
    )
    parser.add_argument("--docker", action="store_true", help="Spin up the 5 sovereign services via Docker Compose")
    parser.add_argument("--no-traffic", action="store_true", help="Disable synthetic telemetry traffic generator")
    args = parser.parse_args()

    if args.docker:
        compose_file = REPO_ROOT / "docker-compose.yml"
        cmd = ["docker", "compose", "-f", str(compose_file), "up"]
        print("\n" + "=" * 80)
        print("  LAUNCHING 5 SOVEREIGN CONTAINERS VIA DOCKER COMPOSE")
        print("=" * 80)
        print("  Subnet:      192.168.40.0/24")
        print("  Containers:  soc-research (192.168.40.10:8440)")
        print("               soc-builder  (192.168.40.20:8442)")
        print("               soc-audit    (192.168.40.30:8444)")
        print("               soc-telemetry(192.168.40.40:8446/8447)")
        print("               soc-governance(192.168.40.50:8448)")
        print("=" * 80 + "\n")
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n[INTERRUPT] Stopping Docker containers...")
            subprocess.run(["docker", "compose", "-f", str(compose_file), "down"])
        sys.exit(0)

    cluster = SovereignMeshCluster(mode=args.mode, service=args.service, enable_traffic=not args.no_traffic)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(cluster.start())
        loop.run_forever()
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Shutting down cluster...")
        loop.run_until_complete(cluster.stop())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
