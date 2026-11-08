"""Domain Presets for Generation 4b Applications and Services ([L1-G4B-008])."""
from __future__ import annotations
from typing import Optional, List, Dict, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from ..schema import CustomDashboardSection, DashboardAST

from . import canvas, consensus, crucible, go, phenoflora, audit, builder, governance, telemetry

PRESET_MAP = {
    "axioma_canvas": canvas,
    "canvas": canvas,
    "axioma_consensus": consensus,
    "consensus": consensus,
    "axioma_crucible": crucible,
    "crucible": crucible,
    "axioma_go": go,
    "go": go,
    "axioma_phenoflora": phenoflora,
    "phenoflora": phenoflora,
    "audit": audit,
    "soc_g4b_audit": audit,
    "builder": builder,
    "soc_g4b_builder": builder,
    "governance": governance,
    "soc_g4b_governance": governance,
    "telemetry": telemetry,
    "soc_g4b_telemetry": telemetry,
}

def get_preset_for_target(target_name: str):
    t = target_name.lower().strip()
    return PRESET_MAP.get(t)