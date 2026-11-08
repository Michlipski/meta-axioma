"""Cryptographic SHA-256 Merkle DAG Chain Renderer ([L1-G4B-003], [L1-G3B-017])."""

from __future__ import annotations

import html
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .schema import DashboardAST, MerkleEvent


def render_merkle_chain(ast: DashboardAST) -> str:
    """Renders the Merkle Chain Head card and block DAG timeline."""
    height_str = f"Height #{len(ast.merkle_chain):03d}" if ast.merkle_chain else "Height #007"
    root_hash = ast.merkle_root or "3bd7f78af52464ce99ec6c1e0268167599d0dcc67dd85da3640639c0320db6a6"

    blocks_html = []
    for evt in ast.merkle_chain:
        blocks_html.append(
            f"""
            <div class="merkle-block">
              <span class="merkle-height">#{evt.block_height:03d}</span>
              <div class="merkle-info">
                <div class="merkle-title">{html.escape(evt.phase_name)}</div>
                <div class="merkle-hash">
                  Hash: <code style="color:var(--cyan);">{html.escape(evt.stage_hash)}</code>
                  {f'&bull; Parent: <code>{html.escape(evt.parent_hash[:12])}...</code>' if evt.parent_hash else ''}
                </div>
              </div>
              <div style="font-size:12px; color:var(--text-muted); font-family:var(--font-mono); text-align:right;">
                <div>{html.escape(evt.witness_role or 'Witness Intercept')}</div>
                <div style="font-size:10px; color:var(--text-dim);">{html.escape(evt.timestamp or ast.certified_at)}</div>
              </div>
              <div>
                <span class="badge badge-emerald">&#10003; {html.escape(evt.status)}</span>
              </div>
            </div>
            """
        )

    all_blocks = "\n".join(blocks_html)

    return f"""
    <!-- Cryptographic SHA-256 Merkle DAG Witness Stream -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <span>&#128279;</span> Tamper-Evident SHA-256 Merkle DAG Witness Stream ([L1-G4B-003] &bull; [L1-G3B-017])
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="badge badge-amber">{html.escape(height_str)}</span>
          <span class="badge badge-emerald">QUINE ATTESTED</span>
        </div>
      </div>
      <div style="background:var(--bg-surface-elevated); border:1px solid var(--border-bright); border-radius:10px; padding:14px 18px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
        <div>
          <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.6px; color:var(--text-muted);">Merkle Chain Root Head</div>
          <div class="mono-cell" style="color:var(--cyan); font-size:14px; font-weight:700; margin-top:2px;">
            0x{html.escape(root_hash)}
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.6px; color:var(--text-muted);">Attestation Timestamp</div>
          <div class="mono-cell" style="font-size:12px; color:var(--text); margin-top:2px;">{html.escape(ast.certified_at)}</div>
        </div>
      </div>
      <div class="merkle-dag-container">
        {all_blocks}
      </div>
    </div>
    """
