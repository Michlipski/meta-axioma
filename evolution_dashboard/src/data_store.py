"""
Data Store for Reimagined Axioma Evolution Dashboard (Root Level).
Provides high-performance, thread-safe access to:
- 8-stage evolutionary trajectory (S0, G1, G2, G3, G1b, G2b, G3b, G4b)
- 7 generational transformations (deltas, technical & thermodynamic catalysts)
- 6 component subsystem lineages
- Top-level Meta-Axioma philosophy (layman & deep systems theory)
- Generation 4b Sovereign Service Mesh specifications
- Interactive sample app compilation simulations (axioma_go, axioma_flow, axioma_sentinel)
- Dynamic side-by-side generational diff engine
- User feedback logging & telemetry
"""

from __future__ import annotations

import json
import re
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

APP_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = APP_ROOT / "data"
EVOLUTION_DATA_PATH = DATA_DIR / "evolution_data.json"
PHILOSOPHY_DATA_PATH = DATA_DIR / "philosophy_data.json"
G4B_DATA_PATH = DATA_DIR / "g4b_architecture.json"
SIMULATION_DATA_PATH = DATA_DIR / "sample_app_simulation.json"
FEEDBACK_DATA_PATH = DATA_DIR / "user_feedback.json"

SUBSYSTEM_ALIASES: dict[str, str] = {
    "compiler_core": "compiler_and_code_emission",
    "compiler_and_code_emission": "compiler_core",
    "fsm_statecharts": "state_and_persistence",
    "state_and_persistence": "fsm_statecharts",
    "verification_auditing": "verification_and_governance_gates",
    "verification_and_governance_gates": "verification_auditing",
    "telemetry_provenance": "thermodynamics_and_token_economy",
    "thermodynamics_and_token_economy": "telemetry_provenance",
    "human_usability": "human_in_the_loop_and_personas",
    "human_in_the_loop_and_personas": "human_usability",
    "distributed_topology": "consensus_and_distributed_topology",
    "consensus_and_distributed_topology": "distributed_topology",
}


def parse_invariant(item: Any) -> dict[str, str]:
    """
    Normalizes invariant records across both dictionary-based schemas (S0..G3b)
    and string-based schemas (G4b).
    Extracts canonical invariant ID (e.g. L1-G3B-000, L1-002, NEG-G1B-001, L1-G4B-001)
    along with name, description, status, and formatted display label.
    """
    if isinstance(item, dict):
        inv_id = str(item.get("id") or item.get("code") or item.get("invariant_id") or item.get("name") or "").strip()
        name = str(item.get("name") or item.get("title") or item.get("label") or inv_id).strip()
        desc = str(item.get("desc") or item.get("description") or "").strip()
        status = str(item.get("status") or "ACTIVE_STRUCTURAL").strip()
        label = f"{inv_id} ({name})" if name and name != inv_id else inv_id
        return {"id": inv_id, "name": name, "desc": desc, "status": status, "label": label}

    s = str(item).strip()

    # Pattern 1: [ID] (Name) or [ID]: Name or [ID] Name
    m1 = re.match(r"^\[([A-Za-z0-9_\-\.]+)\][:\s\-]*(.*)$", s)
    if m1:
        inv_id = m1.group(1).strip()
        rest = m1.group(2).strip().strip("() ")
        name = rest if rest else inv_id
        label = f"{inv_id} ({name})" if name != inv_id else inv_id
        return {"id": inv_id, "name": name, "desc": "", "status": "ACTIVE_STRUCTURAL", "label": label}

    # Pattern 2: ID (Name)
    m2 = re.match(r"^([A-Za-z0-9_\-\.]+)\s*\((.+)\)$", s)
    if m2:
        inv_id = m2.group(1).strip()
        name = m2.group(2).strip()
        return {"id": inv_id, "name": name, "desc": "", "status": "ACTIVE_STRUCTURAL", "label": f"{inv_id} ({name})"}

    # Pattern 3: ID: Name
    m3 = re.match(r"^([A-Za-z0-9_\-\.]+)\s*:\s*(.+)$", s)
    if m3:
        inv_id = m3.group(1).strip()
        name = m3.group(2).strip()
        return {"id": inv_id, "name": name, "desc": "", "status": "ACTIVE_STRUCTURAL", "label": f"{inv_id} ({name})"}

    # Pattern 4: ID - Name (with whitespace around hyphen)
    m4 = re.match(r"^([A-Za-z0-9_\-\.]+)\s+-\s+(.+)$", s)
    if m4:
        inv_id = m4.group(1).strip()
        name = m4.group(2).strip()
        return {"id": inv_id, "name": name, "desc": "", "status": "ACTIVE_STRUCTURAL", "label": f"{inv_id} ({name})"}

    # Pattern 5: Standalone ID matching common invariant token formats (e.g. L1-002, NEG-G1B-001)
    m5 = re.match(r"^[A-Za-z0-9_]+(?:-[A-Za-z0-9_\.]+)+$", s)
    if m5:
        return {"id": s, "name": s, "desc": "", "status": "ACTIVE_STRUCTURAL", "label": s}

    return {"id": s, "name": s, "desc": "", "status": "ACTIVE_STRUCTURAL", "label": s}


class EvolutionDataStore:
    """Thread-safe access to Meta-Axioma evolutionary trajectory and G4b data."""

    BOLTZMANN_K: float = 1.380649e-23  # Joules / Kelvin
    ROOM_TEMP_K: float = 300.0  # Room temperature in Kelvin

    def calculate_landauer_heat(self, bits: int | float, temp_k: float = 300.0) -> float:
        """
        Computes Landauer thermodynamic heat dissipation Q = bits * k_B * T * ln(2).
        Enforces non-negative heat dissipation invariant [L1-008].
        """
        import math
        if bits < 0:
            raise ValueError(f"Erased bits must be non-negative, got {bits} (invariant [L1-008])")
        if temp_k < 0:
            raise ValueError(f"Temperature in Kelvin must be non-negative, got {temp_k}")
        return float(bits) * self.BOLTZMANN_K * float(temp_k) * math.log(2)

    def __init__(
        self,
        evolution_path: Path | None = None,
        philosophy_path: Path | None = None,
        g4b_path: Path | None = None,
        simulation_path: Path | None = None,
        feedback_path: Path | None = None,
    ) -> None:
        self.evolution_path = evolution_path or EVOLUTION_DATA_PATH
        self.philosophy_path = philosophy_path or PHILOSOPHY_DATA_PATH
        self.g4b_path = g4b_path or G4B_DATA_PATH
        self.simulation_path = simulation_path or SIMULATION_DATA_PATH
        self.feedback_path = feedback_path or FEEDBACK_DATA_PATH
        self._lock = threading.RLock()
        self._start_time = time.time()
        self._data: dict[str, Any] = self._load_and_normalize_data()

    def _load_and_normalize_data(self) -> dict[str, Any]:
        """Loads and normalizes all master JSON datasets."""
        with self._lock:
            # 1. Base Evolution Data
            if not self.evolution_path.is_file():
                raise FileNotFoundError(f"Evolution data missing: {self.evolution_path}")
            with open(self.evolution_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Normalize Stages
            stages = data.get("stages", [])
            for st in stages:
                st_id = st.get("id", "").lower()
                st["id"] = st_id
                if not st.get("mandate"):
                    st["mandate"] = st.get("teleological_mission") or st.get("executive_summary", "")
                if not st.get("title"):
                    st["title"] = st.get("subtitle") or st.get("name", "")

                beehive = st.get("beehive_topology", {})
                raw_nodes = st.get("nodes") or beehive.get("nodes", [])
                if isinstance(raw_nodes, dict):
                    nodes_list = list(raw_nodes.values())
                elif isinstance(raw_nodes, list):
                    nodes_list = list(raw_nodes)
                else:
                    nodes_list = []

                for n in nodes_list:
                    if isinstance(n, dict) and "label" not in n:
                        n["label"] = n.get("shortLabel") or n.get("name") or n.get("id", "")
                st["nodes"] = nodes_list

                raw_edges = st.get("edges") or beehive.get("edges", [])
                st["edges"] = list(raw_edges) if isinstance(raw_edges, list) else []

                # Normalize architect epistemic contributions for backwards-compatibility aliases
                if "architect_epistemic_contributions" in st and "michaels_epistemic_contributions" not in st:
                    st["michaels_epistemic_contributions"] = st["architect_epistemic_contributions"]
                elif "michaels_epistemic_contributions" in st and "architect_epistemic_contributions" not in st:
                    st["architect_epistemic_contributions"] = st["michaels_epistemic_contributions"]

            # Normalize Transformations
            trans = data.get("transformations", [])
            for tr in trans:
                tr_id = tr.get("id", "").lower()
                tr["id"] = tr_id
                if "delta" in tr and isinstance(tr["delta"], dict) and "added" not in tr:
                    d_dict = tr["delta"]
                    tr["added"] = d_dict.get("added", [])
                    tr["removed"] = d_dict.get("removed", [])
                    tr["refactored"] = d_dict.get("refactored", [])
                if "catalyst" in tr and isinstance(tr["catalyst"], dict) and "technical_catalyst" not in tr:
                    c_dict = tr["catalyst"]
                    tr["technical_catalyst"] = c_dict.get("technical", "")
                    tr["thermodynamic_catalyst"] = c_dict.get("thermodynamic", "")

            # 2. Philosophy Data
            if self.philosophy_path.is_file():
                with open(self.philosophy_path, "r", encoding="utf-8") as f:
                    data["philosophy"] = json.load(f)
                    # Normalize core_pillars alias for full backwards compatibility
                    sl = data["philosophy"].get("surface_layman", {})
                    if "core_pillars" not in sl:
                        r1 = sl.get("row_1_pillars", [])
                        r2 = sl.get("row_2_pillars", [])
                        if r1 or r2:
                            sl["core_pillars"] = r1 + r2
                        elif "flagship_pillar" in sl and "complementary_pillars" in sl:
                            sl["core_pillars"] = [sl["flagship_pillar"]] + sl["complementary_pillars"]
            else:
                data["philosophy"] = {}

            # 3. G4b Architecture Data
            if self.g4b_path.is_file():
                with open(self.g4b_path, "r", encoding="utf-8") as f:
                    data["g4b_architecture"] = json.load(f)
            else:
                data["g4b_architecture"] = {}

            # 4. Sample App Simulation Data
            if self.simulation_path.is_file():
                with open(self.simulation_path, "r", encoding="utf-8") as f:
                    data["sample_app_simulation"] = json.load(f)
            else:
                data["sample_app_simulation"] = {}

            return data

    def reload(self) -> None:
        """Forces a thread-safe reload from disk."""
        with self._lock:
            self._data = self._load_and_normalize_data()

    def get_health(self) -> dict[str, Any]:
        """Returns runtime system health and telemetry counters."""
        with self._lock:
            stages = self._data.get("stages", [])
            trans = self._data.get("transformations", [])
            subs = self._data.get("subsystems", [])
            sub_count = len(subs) if isinstance(subs, list) else len(subs.keys())
            uptime = time.time() - self._start_time
            return {
                "status": "healthy",
                "uptime_seconds": round(uptime, 2),
                "stages_count": len(stages),
                "transformations_count": len(trans),
                "subsystems_count": sub_count,
                "zenith_stage_id": self._data.get("zenith_architecture", {}).get("generation_id", "g4b"),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }

    def get_zenith(self) -> dict[str, Any]:
        """Returns the pinned Zenith Architecture summary (G4b Apex)."""
        with self._lock:
            zenith = dict(self._data.get("zenith_architecture", {}))
            apex_id = zenith.get("generation_id", "g4b")
            stage = self.get_stage(apex_id)
            if stage:
                zenith["stage_details"] = stage
            return zenith

    def get_stages(self) -> list[dict[str, Any]]:
        """Returns all 8 generational stages in chronological order."""
        with self._lock:
            return list(self._data.get("stages", []))

    def get_stage(self, stage_id: str) -> dict[str, Any] | None:
        """Returns a single stage by canonical ID or alias."""
        target = stage_id.strip().lower()
        alias_map = {
            "genesis": "s0",
            "s_0": "s0",
            "generation_01": "g1",
            "generation_1": "g1",
            "gen_01": "g1",
            "generation_02": "g2",
            "generation_2": "g2",
            "gen_02": "g2",
            "generation_03": "g3",
            "generation_3": "g3",
            "gen_03": "g3",
            "generation_01b": "g1b",
            "gen_01b": "g1b",
            "generation_02b": "g2b",
            "gen_02b": "g2b",
            "generation_03b": "g3b",
            "gen_03b": "g3b",
            "generation_04b": "g4b",
            "gen_04b": "g4b",
            "g4": "g4b",
        }
        resolved = alias_map.get(target, target)
        with self._lock:
            for st in self._data.get("stages", []):
                if st.get("id", "").lower() == resolved:
                    return dict(st)
        return None

    def get_transformations(self) -> list[dict[str, Any]]:
        """Returns all 7 transformation nodes."""
        with self._lock:
            return list(self._data.get("transformations", []))

    def get_transformation(self, trans_id: str) -> dict[str, Any] | None:
        """Returns a single transformation node by ID or alias."""
        target = trans_id.strip().lower()
        with self._lock:
            for tr in self._data.get("transformations", []):
                if tr.get("id", "").lower() == target:
                    return dict(tr)
                # Check alias matching e.g. s0_to_g1
                src = tr.get("source_stage_id", "").lower()
                tgt = tr.get("target_stage_id", "").lower()
                if target in {f"{src}_to_{tgt}", f"{src}_{tgt}", f"t_{src}_{tgt}"}:
                    return dict(tr)
        return None

    def get_components(self) -> list[dict[str, Any]]:
        """Returns the 6 architectural subsystem lineages."""
        with self._lock:
            subs = self._data.get("subsystems", [])
            if isinstance(subs, list):
                return list(subs)
            elif isinstance(subs, dict):
                out = []
                for k, v in subs.items():
                    entry = dict(v)
                    entry.setdefault("id", k)
                    out.append(entry)
                return out
            return []

    def get_component(self, subsystem_id: str) -> dict[str, Any] | None:
        """Returns a single component lineage by ID or alias."""
        target = subsystem_id.strip().lower()
        resolved = SUBSYSTEM_ALIASES.get(target, target)
        with self._lock:
            subs = self.get_components()
            for s in subs:
                s_id = s.get("id", "").lower()
                if s_id in {target, resolved}:
                    return dict(s)
                # Check name match
                s_name = s.get("name", "").lower().replace(" ", "_")
                if s_name in {target, resolved}:
                    return dict(s)
        return None

    def get_philosophy(self) -> dict[str, Any]:
        """Returns the project philosophy dataset (layman + academic)."""
        with self._lock:
            return dict(self._data.get("philosophy", {}))

    def get_g4b_architecture(self) -> dict[str, Any]:
        """Returns the Generation 4b Sovereign Service Mesh specification."""
        with self._lock:
            return dict(self._data.get("g4b_architecture", {}))

    def get_simulations(self) -> dict[str, Any]:
        """Returns the available sample app simulation catalog."""
        with self._lock:
            return dict(self._data.get("sample_app_simulation", {}))

    def get_simulation(self, app_id: str = "") -> dict[str, Any] | None:
        """Returns a specific sample app compilation simulation walkthrough."""
        sims = self.get_simulations()
        app_sims = sims.get("simulations", {})
        target = app_id.strip().lower()
        if target and target in app_sims:
            return dict(app_sims[target])
        if not target and "axioma_go" in app_sims:
            return dict(app_sims["axioma_go"])
        return None

    def get_generational_diff(self, stage_a_id: str, stage_b_id: str) -> dict[str, Any]:
        """
        Dynamically computes a structural diff between any two generations (Option 3 Feature).
        Compares:
        - Architecture model (monolithic vs sovereign mesh)
        - Active invariants
        - Node count & topology density
        - Verification gate model
        - Human intervention model
        - Layman problem & breakthrough
        """
        st_a = self.get_stage(stage_a_id) or self.get_stage("s0")
        st_b = self.get_stage(stage_b_id) or self.get_stage("g4b")
        if not st_a or not st_b:
            return {"error": "Invalid stage IDs"}

        raw_inv_a = st_a.get("active_invariants", [])
        raw_inv_b = st_b.get("active_invariants", [])

        parsed_a = [parse_invariant(x) for x in raw_inv_a]
        parsed_b = [parse_invariant(x) for x in raw_inv_b]

        map_a = {p["id"]: p for p in parsed_a if p["id"]}
        map_b = {p["id"]: p for p in parsed_b if p["id"]}

        set_a = set(map_a.keys())
        set_b = set(map_b.keys())

        added_ids = sorted(list(set_b - set_a))
        retained_ids = sorted(list(set_a & set_b))
        retired_ids = sorted(list(set_a - set_b))

        nodes_a = st_a.get("nodes", [])
        nodes_b = st_b.get("nodes", [])

        return {
            "stage_a": {
                "id": st_a.get("id"),
                "name": st_a.get("name"),
                "era": st_a.get("era"),
                "nodes_count": len(nodes_a),
                "invariants_count": len(set_a),
                "layman_summary": st_a.get("layman_summary", st_a.get("executive_summary")),
                "layman_problem": st_a.get("layman_problem", "Initial exploratory phase"),
                "layman_breakthrough": st_a.get("layman_breakthrough", "Establishing invariants"),
                "academic_theory": st_a.get("academic_theory", "Foundational structural lattice"),
            },
            "stage_b": {
                "id": st_b.get("id"),
                "name": st_b.get("name"),
                "era": st_b.get("era"),
                "nodes_count": len(nodes_b),
                "invariants_count": len(set_b),
                "layman_summary": st_b.get("layman_summary", st_b.get("executive_summary")),
                "layman_problem": st_b.get("layman_problem", "Advanced decoupling and sovereign verification"),
                "layman_breakthrough": st_b.get("layman_breakthrough", "Sovereign multi-service mesh"),
                "academic_theory": st_b.get("academic_theory", "Decoupled epistemic research and SMT mediation"),
            },
            "invariants_added": added_ids,
            "invariants_retained": retained_ids,
            "invariants_retired": retired_ids,
            "invariants_details": {
                "added": [map_b[i] for i in added_ids],
                "retained": [map_b.get(i) or map_a.get(i) for i in retained_ids],
                "retired": [map_a[i] for i in retired_ids],
            },
            "invariants_added_labels": [map_b[i]["label"] for i in added_ids],
            "invariants_retained_labels": [(map_b.get(i) or map_a[i])["label"] for i in retained_ids],
            "invariants_retired_labels": [map_a[i]["label"] for i in retired_ids],
            "nodes_delta": len(nodes_b) - len(nodes_a),
            "invariants_delta": len(set_b) - len(set_a),
            "evolutionary_leap": f"Evolution from {st_a.get('name')} ({st_a.get('era')}) to {st_b.get('name')} ({st_b.get('era')})",
        }

    def get_feedback(self) -> list[dict[str, Any]]:
        """Returns all recorded user feedback items."""
        with self._lock:
            if not self.feedback_path.is_file():
                return []
            try:
                with open(self.feedback_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except Exception:
                return []

    def add_feedback(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Validates and persists a user feedback entry."""
        if not isinstance(entry, dict):
            raise ValueError(f"Feedback entry must be a dictionary, got {type(entry).__name__}")
        with self._lock:
            items = self.get_feedback()
            new_id = f"fb_{int(time.time() * 1000)}"
            raw_rating = entry.get("rating", 5)
            try:
                rating = int(raw_rating)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Rating must be an integer, got: {raw_rating!r}") from e
            if rating < 1 or rating > 5:
                raise ValueError(f"Rating must be between 1 and 5, got {rating}")
            comment = str(entry.get("comment", "")).strip()
            author = str(entry.get("author", "Anonymous Evaluator")).strip() or "Anonymous Evaluator"
            category = str(entry.get("category", "General Ergonomics")).strip() or "General Ergonomics"
            record = {
                "id": str(entry.get("id", new_id)),
                "timestamp": str(entry.get("timestamp", datetime.now(timezone.utc).isoformat())),
                "author": author,
                "category": category,
                "rating": rating,
                "comment": comment,
            }
            items.append(record)
            with open(self.feedback_path, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            return record
