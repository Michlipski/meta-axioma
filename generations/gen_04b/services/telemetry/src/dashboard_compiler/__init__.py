"""Sovereign Telemetry Dashboard Compiler Package ([L1-G4B-008]).

Provides canonical compilation of 100% self-contained, zero-CDN HTML5
telemetry dashboards across all Meta-Axioma applications and services.
"""

from __future__ import annotations

from .compiler import TelemetryDashboardCompiler
from .schema import (
    CustomDashboardSection,
    DashboardAST,
    InvariantAxiom,
    MerkleEvent,
    MeshEdge,
    MeshNode,
    MeshTopology,
    SubagentWitness,
    TokenMetrics,
)

__all__ = [
    "TelemetryDashboardCompiler",
    "DashboardAST",
    "TokenMetrics",
    "SubagentWitness",
    "CustomDashboardSection",
    "MerkleEvent",
    "MeshTopology",
    "MeshNode",
    "MeshEdge",
    "InvariantAxiom",
]
