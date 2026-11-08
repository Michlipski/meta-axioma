"""Distributed Cluster Topology and Non-Loopback Subnet SVG Renderer ([L1-G3B-012], HERM-001)."""

from __future__ import annotations

import html
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .schema import DashboardAST, MeshNode


def render_mesh_topology(ast: DashboardAST) -> str:
    """Renders the non-loopback distributed subnet topology graph and node table."""
    topo = ast.mesh_topology
    nodes = topo.nodes

    # SVG layout math
    svg_width = 860
    svg_height = 240
    n = len(nodes)

    node_coords = {}
    if n > 0:
        center_x = svg_width / 2
        center_y = svg_height / 2
        radius_x = svg_width * 0.38
        radius_y = svg_height * 0.32
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / n - (math.pi / 2)
            nx = center_x + radius_x * math.cos(angle)
            ny = center_y + radius_y * math.sin(angle)
            node_coords[node.node_id] = (nx, ny)

    # Render SVG lines (edges)
    edge_elements = []
    if topo.edges:
        for edge in topo.edges:
            if edge.source_id in node_coords and edge.target_id in node_coords:
                x1, y1 = node_coords[edge.source_id]
                x2, y2 = node_coords[edge.target_id]
                edge_elements.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="rgba(56, 189, 248, 0.3)" stroke-width="2" stroke-dasharray="4 4" />'
                )
    else:
        # Default fully/ring connected edges
        node_ids = list(node_coords.keys())
        for i in range(len(node_ids)):
            x1, y1 = node_coords[node_ids[i]]
            x2, y2 = node_coords[node_ids[(i + 1) % len(node_ids)]]
            edge_elements.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="rgba(56, 189, 248, 0.3)" stroke-width="2" stroke-dasharray="4 4" />'
            )

    # Render SVG nodes
    node_elements = []
    for node in nodes:
        nx, ny = node_coords.get(node.node_id, (svg_width / 2, svg_height / 2))
        is_gw = "gateway" in node.role.lower() or "orchestrator" in node.role.lower()
        node_color = "var(--purple)" if is_gw else "var(--cyan)"
        node_elements.append(
            f"""
            <g transform="translate({nx:.1f}, {ny:.1f})">
              <circle r="18" fill="rgba(13, 18, 30, 0.95)" stroke="{node_color}" stroke-width="2" />
              <circle r="6" fill="{node_color}" />
              <text y="28" text-anchor="middle" fill="var(--text)" font-size="11" font-weight="600" font-family="var(--font-mono)">
                {html.escape(node.node_id)}
              </text>
              <text y="41" text-anchor="middle" fill="var(--text-muted)" font-size="9" font-family="var(--font-mono)">
                {html.escape(node.ip)}:{node.port}
              </text>
            </g>
            """
        )

    all_edges_svg = "\n".join(edge_elements)
    all_nodes_svg = "\n".join(node_elements)

    # Table rows
    table_rows = []
    for node in nodes:
        role_badge = (
            f'<span class="badge badge-purple">{html.escape(node.role.upper())}</span>'
            if "gateway" in node.role.lower() or "orchestrator" in node.role.lower()
            else f'<span class="badge badge-cyan">{html.escape(node.role.upper())}</span>'
        )
        table_rows.append(
            f"""
            <tr>
              <td class="mono-cell"><strong>{html.escape(node.node_id)}</strong></td>
              <td>{role_badge}</td>
              <td class="mono-cell" style="color:var(--cyan);">{html.escape(node.ip)}</td>
              <td class="mono-cell">{node.port}</td>
              <td>{html.escape(node.description or 'Active Cluster Enclave')}</td>
              <td><span class="badge badge-emerald">&#10003; {html.escape(node.status)}</span></td>
            </tr>
            """
        )

    all_table_rows = "\n".join(table_rows)

    return f"""
    <!-- Distributed Cluster Mesh Topology -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <span>&#127760;</span> Dedicated Non-Loopback Cluster Topology ([L1-G3B-012] &bull; HERM-001)
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="badge badge-purple">SUBNET: {html.escape(topo.subnet)}</span>
          <span class="badge badge-emerald">&#10003; HERM-001 NON-LOOPBACK</span>
        </div>
      </div>
      <div class="topology-container">
        <svg class="topology-svg" viewBox="0 0 {svg_width} {svg_height}">
          {all_edges_svg}
          {all_nodes_svg}
        </svg>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Cluster Node ID</th>
                <th>Enclave Role</th>
                <th>Virtual Subnet IP</th>
                <th>Port</th>
                <th>Description</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {all_table_rows}
            </tbody>
          </table>
        </div>
      </div>
    </div>
    """
