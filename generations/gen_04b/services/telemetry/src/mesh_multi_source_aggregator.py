"""Mesh Multi-Source Telemetry Aggregator (`soc_g4b_telemetry`).

Enforces:
- Invariant [L1-G4B-001]: Service-Oriented Sovereign Mesh Protocol Standardization.
- Invariant [L1-G3B-012]: Dedicated Non-Loopback Network Topology.
- Multi-source aggregation from:
  - Phase 1 Research (`192.168.40.10:8440`)
  - Phase 2 Builder (`192.168.40.20:8442`)
  - Phase 3 Audit (`192.168.40.30:8444`)
  - Phase 4 Telemetry (`192.168.40.40:8446`)
- Aggregates node witnesses, heartbeats, Merkle roots, and cumulative Landauer dissipation across the mesh.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from .domain_models import (
    assert_non_loopback,
    LandauerDissipationLedger,
    ServiceMeshTopologyState,
    ServiceNodeWitness,
    TelemetryDomainInvariantViolation,
    TelemetryTopologyState,
)


class MeshMultiSourceAggregator:
    """Aggregates telemetry, heartbeats, and thermodynamic dissipation from sovereign mesh peers."""

    CANONICAL_PEERS = {
        "research_service": ("192.168.40.10", 8440),
        "builder_service": ("192.168.40.20", 8442),
        "audit_service": ("192.168.40.30", 8444),
        "telemetry_service": ("192.168.40.40", 8446),
    }

    def __init__(
        self,
        self_node_ip: str = "192.168.40.40",
        self_port: int = 8446,
        auto_register_canonical: bool = True,
    ) -> None:
        assert_non_loopback(self_node_ip, "MeshMultiSourceAggregator self_node_ip")
        if not (1024 <= self_port <= 65535):
            raise TelemetryDomainInvariantViolation(f"Invalid self_port: {self_port}")

        self.self_node_ip = self_node_ip
        self.self_port = self_port
        self.topology_state = ServiceMeshTopologyState(
            topology_id="mesh_g4b_topology",
            self_node_ip=self_node_ip,
            self_port=self_port,
        )

        if auto_register_canonical:
            self._register_canonical_peers()

    def _register_canonical_peers(self) -> None:
        """Initializes canonical sovereign mesh peer registry."""
        for s_name, (ip, port) in self.CANONICAL_PEERS.items():
            self.register_mesh_node(s_name, ip, port)

    def register_mesh_node(
        self,
        service_name: str,
        node_ip: str,
        port: int,
        initial_status: TelemetryTopologyState = TelemetryTopologyState.HEALTHY,
    ) -> ServiceNodeWitness:
        """Registers or updates a sovereign node witness in the mesh topology."""
        if not service_name:
            raise TelemetryDomainInvariantViolation("service_name must not be empty.")
        assert_non_loopback(node_ip, f"MeshMultiSourceAggregator.register_mesh_node '{service_name}'")
        if not (1024 <= port <= 65535):
            raise TelemetryDomainInvariantViolation(f"port ({port}) must be in range [1024, 65535].")

        witness = ServiceNodeWitness(
            service_name=service_name,
            node_ip=node_ip,
            port=port,
            last_heartbeat=int(time.time() * 1000),
            status=initial_status,
        )
        self.topology_state.register_witness(witness)
        return witness

    def record_node_heartbeat(
        self,
        service_name: str,
        merkle_root: str,
        bits_erased: int,
        status: TelemetryTopologyState = TelemetryTopologyState.HEALTHY,
    ) -> ServiceNodeWitness:
        """Records a certified heartbeat from a sovereign mesh service node."""
        if service_name not in self.topology_state.registered_nodes:
            raise TelemetryDomainInvariantViolation(
                f"Cannot record heartbeat for unregistered service '{service_name}'."
            )
        if bits_erased < 0:
            raise TelemetryDomainInvariantViolation("bits_erased must be non-negative.")

        node = self.topology_state.registered_nodes[service_name]
        node.last_heartbeat = int(time.time() * 1000)
        node.Merkle_root = merkle_root
        node.bits_erased = bits_erased
        node.status = status
        node.validate_invariants()

        self.topology_state.last_topology_update = int(time.time() * 1000)
        return node

    def aggregate_mesh_dissipation(self) -> Dict[str, Any]:
        """Calculates total Landauer bit erasure and heat dissipation across all mesh nodes."""
        total_bits = 0
        per_node: Dict[str, Dict[str, Any]] = {}

        for s_name, node in self.topology_state.registered_nodes.items():
            bits = node.bits_erased
            total_bits += bits
            heat_joules = LandauerDissipationLedger.BOLTZMANN_K * 300.0 * LandauerDissipationLedger.LN_2 * float(bits)
            per_node[s_name] = {
                "node_ip": node.node_ip,
                "port": node.port,
                "bits_erased": bits,
                "heat_dissipated_joules": heat_joules,
                "merkle_root": node.Merkle_root,
                "status": node.status.value,
            }

        total_heat_joules = LandauerDissipationLedger.BOLTZMANN_K * 300.0 * LandauerDissipationLedger.LN_2 * float(total_bits)

        return {
            "total_mesh_bits_erased": total_bits,
            "total_mesh_heat_dissipated_joules": total_heat_joules,
            "nodes_count": len(self.topology_state.registered_nodes),
            "per_node": per_node,
        }

    def get_cluster_topology_state(self) -> ServiceMeshTopologyState:
        """Returns the current sovereign mesh topology state."""
        self.topology_state.validate_invariants()
        return self.topology_state

    def get_registered_nodes(self) -> Dict[str, ServiceNodeWitness]:
        """Returns the dictionary of registered peer node witnesses."""
        return dict(self.topology_state.registered_nodes)
