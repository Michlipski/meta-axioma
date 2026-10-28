"""Dynamically Compiled Distributed Topology Verifier for: topo_soc_system_g3b_researcher_quine."""

import json
from pathlib import Path
from typing import Dict, Any, List


class TopologicalFidelityError(RuntimeError):
    """Raised when [L1-G3B-012] anti-loopback boundary realism is breached."""
    pass


class GeneratedTopologyVerifier:
    LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1", "0.0.0.0"}

    @classmethod
    def load_and_verify(cls, config_path: Path = None) -> Dict[str, Any]:
        if config_path is None:
            config_path = Path(__file__).resolve().parent / 'topology_config.json'
        data = json.loads(config_path.read_text(encoding='utf-8'))
        nodes = data.get('nodes', {})
        if len(nodes) > 1:
            for nid, n in nodes.items():
                host = n.get('host_interface', '').strip().lower()
                if host in cls.LOOPBACK_HOSTS:
                    raise TopologicalFidelityError(
                        f"[L1-G3B-012 Violation] Node '{nid}' binds to loopback '{host}'."
                    )
        return data
