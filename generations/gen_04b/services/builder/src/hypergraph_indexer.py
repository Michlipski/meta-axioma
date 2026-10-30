"""Generation 4b Universal Symbol URN Relational Hypergraph (`[Layer D]`).

Enforces:
- O(1) canonical URN symbol resolution (urn:axioma:g4b:<domain>:<entity>#<symbol>).
- Relational hypergraph edge modeling (callers, callees, contract bounds, type definitions).
- Topological dependency sorting and cycle detection.
- Fast diagnostic resolution for missing or broken dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from generations.gen_04b.protocols.urn_registry import SymbolURN, URNFormatError
from .domain_models import ASTNodeType, DomainInvariantViolation


@dataclass
class HypergraphNode:
    """A symbol node in the universal relational hypergraph."""
    urn: SymbolURN
    node_type: ASTNodeType
    file_path: str
    signature: str = ""
    dependencies: Set[str] = field(default_factory=set)  # Set of target URN strings
    dependents: Set[str] = field(default_factory=set)    # Set of source URN strings
    metadata: Dict[str, Any] = field(default_factory=dict)

    def canonical_urn_str(self) -> str:
        return self.urn.to_string()


@dataclass
class Hyperedge:
    """A multi-way relational hyperedge connecting a group of related symbols."""
    edge_id: str
    relation_name: str
    member_urns: Set[str] = field(default_factory=set)
    invariants: List[str] = field(default_factory=list)


class SymbolHypergraphIndexer:
    """O(1) Universal Symbol URN Relational Hypergraph Indexer."""

    def __init__(self):
        # Primary symbol table: canonical_urn -> HypergraphNode
        self._nodes: Dict[str, HypergraphNode] = {}
        # Hyperedges: edge_id -> Hyperedge
        self._hyperedges: Dict[str, Hyperedge] = {}
        # Domain index: domain -> set of URN strings
        self._domain_index: Dict[str, Set[str]] = {}

    def index_symbol(
        self,
        urn_str: str,
        node_type: ASTNodeType,
        file_path: str,
        signature: str = "",
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> HypergraphNode:
        """Indexes a symbol with O(1) storage and updates dependency graph."""
        parsed_urn = SymbolURN.parse(urn_str)
        canonical = parsed_urn.to_string()

        node = HypergraphNode(
            urn=parsed_urn,
            node_type=node_type,
            file_path=file_path,
            signature=signature,
            dependencies=set(dependencies or []),
            metadata=metadata or {},
        )

        self._nodes[canonical] = node

        # Update domain index
        domain = parsed_urn.domain
        if domain not in self._domain_index:
            self._domain_index[domain] = set()
        self._domain_index[domain].add(canonical)

        # Update reverse dependents
        for dep in node.dependencies:
            if dep in self._nodes:
                self._nodes[dep].dependents.add(canonical)

        return node

    def resolve_symbol(self, urn_str: str) -> Optional[HypergraphNode]:
        """O(1) resolution of a symbol by canonical URN."""
        try:
            parsed = SymbolURN.parse(urn_str)
            return self._nodes.get(parsed.to_string())
        except URNFormatError:
            return None

    def get_dependents(self, urn_str: str) -> Set[str]:
        """Returns all symbols that depend on the given URN."""
        node = self.resolve_symbol(urn_str)
        return node.dependents if node else set()

    def get_dependencies(self, urn_str: str) -> Set[str]:
        """Returns all dependencies required by the given URN."""
        node = self.resolve_symbol(urn_str)
        return node.dependencies if node else set()

    def register_hyperedge(self, edge_id: str, relation_name: str, member_urns: List[str], invariants: Optional[List[str]] = None) -> Hyperedge:
        """Registers a multi-way relational hyperedge between symbols."""
        edge = Hyperedge(
            edge_id=edge_id,
            relation_name=relation_name,
            member_urns=set(member_urns),
            invariants=invariants or [],
        )
        self._hyperedges[edge_id] = edge
        return edge

    def find_unresolved_dependencies(self) -> Dict[str, Set[str]]:
        """Identifies any referenced URNs that are not indexed in the hypergraph."""
        unresolved: Dict[str, Set[str]] = {}
        for urn, node in self._nodes.items():
            missing = {dep for dep in node.dependencies if dep not in self._nodes}
            if missing:
                unresolved[urn] = missing
        return unresolved

    def topological_sort(self) -> List[str]:
        """Computes a topological ordering of symbols or detects cycles."""
        in_degree: Dict[str, int] = {u: 0 for u in self._nodes}
        for u, node in self._nodes.items():
            for dep in node.dependencies:
                if dep in in_degree:
                    # In standard dep graph, if u depends on dep, dep must be built before u
                    in_degree[u] += 1

        queue: List[str] = [u for u, deg in in_degree.items() if deg == 0]
        sorted_order: List[str] = []

        while queue:
            curr = queue.pop(0)
            sorted_order.append(curr)
            # Find nodes that depend on curr
            curr_node = self._nodes[curr]
            for dep_urn in curr_node.dependents:
                if dep_urn in in_degree:
                    in_degree[dep_urn] -= 1
                    if in_degree[dep_urn] == 0:
                        queue.append(dep_urn)

        if len(sorted_order) < len(self._nodes):
            # Cyclic dependency detected
            remaining = [u for u in self._nodes if u not in sorted_order]
            raise DomainInvariantViolation(f"Cyclic dependency detected in Hypergraph symbols: {remaining}")

        return sorted_order

    def count(self) -> int:
        return len(self._nodes)
