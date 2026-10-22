"""Stateful Human Override Registry & Anti-Creep Governance for System G2b."""

from dataclasses import asdict, dataclass, field
import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class HeuristicExemption:
    exemption_id: str
    heuristic_id: str
    component_name: str
    component_hash: str
    human_rationale: str
    scope: str  # "COMPONENT_LOCAL" | "SUBDOMAIN" | "GLOBAL"
    timestamp: str
    ttl_epochs: int = 5
    epochs_active: int = 0
    is_active: bool = True


@dataclass
class HeuristicDebtReport:
    total_heuristics_checked: int
    active_exemptions: int
    heuristic_debt_ratio: float
    max_allowed_debt_ratio: float = 0.15
    is_creep_warning: bool = False
    active_exemption_ids: List[str] = field(default_factory=list)


class StatefulOverrideRegistry:
    """Persistent manager for human heuristic exemptions to prevent unverified creep."""

    def __init__(self, registry_path: Optional[Path] = None):
        if registry_path is None:
            # Default to workspace trace/overrides/heuristic_overrides.json
            repo_root = Path(__file__).resolve().parents[5]
            registry_path = repo_root / "trace" / "overrides" / "heuristic_overrides.json"
        self.registry_path = Path(registry_path)
        self.exemptions: List[HeuristicExemption] = []
        self._load()

    def _load(self):
        if self.registry_path.exists():
            try:
                data = json.loads(self.registry_path.read_text(encoding="utf-8"))
                self.exemptions = [
                    HeuristicExemption(**item) for item in data.get("exemptions", [])
                ]
            except Exception:
                self.exemptions = []
        else:
            self.exemptions = []

    def save(self):
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        report = self.compute_debt_report(total_checkpoints=max(1, len(self.exemptions) * 4))
        payload = {
            "version": "1.0",
            "exemptions": [asdict(e) for e in self.exemptions],
            "metadata": {
                "heuristic_debt_ratio": report.heuristic_debt_ratio,
                "max_allowed_debt_ratio": report.max_allowed_debt_ratio,
                "last_audit_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
        }
        self.registry_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def register_exemption(
        self,
        heuristic_id: str,
        component_name: str,
        component_hash: str,
        human_rationale: str,
        scope: str = "COMPONENT_LOCAL",
        ttl_epochs: int = 5
    ) -> HeuristicExemption:
        """Registers a formal, stateful human override."""
        exemption_id = f"EXEMPT-{heuristic_id}-{component_hash[:6]}"
        # Deactivate any duplicate
        self.exemptions = [e for e in self.exemptions if e.exemption_id != exemption_id]

        exemption = HeuristicExemption(
            exemption_id=exemption_id,
            heuristic_id=heuristic_id,
            component_name=component_name,
            component_hash=component_hash,
            human_rationale=human_rationale,
            scope=scope,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            ttl_epochs=ttl_epochs,
            is_active=True
        )
        self.exemptions.append(exemption)
        self.save()
        return exemption

    def is_exempt(self, heuristic_id: str, component_hash: str) -> Optional[HeuristicExemption]:
        """Checks if a component violation has an active, valid stateful override."""
        for ex in self.exemptions:
            if ex.is_active and ex.heuristic_id == heuristic_id:
                if ex.scope == "GLOBAL" or ex.component_hash == component_hash:
                    return ex
        return None

    def compute_debt_report(self, total_checkpoints: int = 20) -> HeuristicDebtReport:
        """Computes the Heuristic Debt Index to prevent anti-creep accumulation."""
        active = [e for e in self.exemptions if e.is_active]
        ratio = len(active) / max(1, total_checkpoints)
        return HeuristicDebtReport(
            total_heuristics_checked=total_checkpoints,
            active_exemptions=len(active),
            heuristic_debt_ratio=round(ratio, 3),
            max_allowed_debt_ratio=0.15,
            is_creep_warning=ratio > 0.15,
            active_exemption_ids=[e.exemption_id for e in active]
        )
