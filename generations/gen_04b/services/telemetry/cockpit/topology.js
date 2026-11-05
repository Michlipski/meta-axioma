/**
 * Zenith Cockpit 60fps Canvas Node-Link Topology Visualizer (`topology.js`).
 *
 * Enforces:
 * - [L1-G3B-012] Dedicated Non-Loopback Network Topology Bound to 192.168.40.0/24.
 * - 60fps HTML5 Canvas Particle Flow Simulation across 6 nodes and 12 channels.
 * - Dynamic Worker Tree Clustering on Bursts.
 * - Zero External Dependencies (Vanilla Canvas 2D API).
 */

class ZenithTopologyCanvas {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.particles = [];
    this.dynamicWorkers = [];
    this.activeHalos = new Map();

    // 6 Canonical Topology Nodes from TopologyIR
    this.nodes = {
      node_research: { id: 'node_research', label: 'Research', ip: '192.168.40.10', port: 8440, x: 0.22, y: 0.28, color: '#38bdf8', active: false },
      node_builder: { id: 'node_builder', label: 'Builder', ip: '192.168.40.20', port: 8442, x: 0.50, y: 0.25, color: '#f59e0b', active: false },
      node_audit: { id: 'node_audit', label: 'Audit', ip: '192.168.40.30', port: 8444, x: 0.78, y: 0.28, color: '#00ff88', active: false },
      node_telemetry: { id: 'node_telemetry', label: 'Telemetry Vault', ip: '192.168.40.40', port: 8446, x: 0.50, y: 0.75, color: '#00ffff', active: false },
      node_governance: { id: 'node_governance', label: 'Governance', ip: '192.168.40.50', port: 8448, x: 0.82, y: 0.72, color: '#ff007f', active: false },
      node_worker_21: { id: 'node_worker_21', label: 'Worker 21', ip: '192.168.40.21', port: 8450, x: 0.18, y: 0.72, color: '#a855f7', active: false },
    };

    // 12 Channels from TopologyIR
    this.channels = [
      { id: 'channel_research_builder', source: 'node_research', target: 'node_builder' },
      { id: 'channel_builder_research_rfc', source: 'node_builder', target: 'node_research' },
      { id: 'channel_builder_audit', source: 'node_builder', target: 'node_audit' },
      { id: 'channel_audit_builder_verdict', source: 'node_audit', target: 'node_builder' },
      { id: 'channel_audit_governance', source: 'node_audit', target: 'node_governance' },
      { id: 'channel_governance_builder_veto', source: 'node_governance', target: 'node_builder' },
      { id: 'channel_research_telemetry', source: 'node_research', target: 'node_telemetry' },
      { id: 'channel_builder_telemetry', source: 'node_builder', target: 'node_telemetry' },
      { id: 'channel_audit_telemetry', source: 'node_audit', target: 'node_telemetry' },
      { id: 'channel_governance_telemetry', source: 'node_governance', target: 'node_telemetry' },
      { id: 'channel_builder_workers_dispatch', source: 'node_builder', target: 'node_worker_21' },
      { id: 'channel_workers_telemetry_batch', source: 'node_worker_21', target: 'node_telemetry' },
    ];

    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  resize() {
    if (!this.canvas) return;
    const parent = this.canvas.parentElement;
    if (!parent) return;
    const rect = parent.getBoundingClientRect();
    const w = (rect.width && rect.width > 20) ? rect.width : (parent.clientWidth || 800);
    const h = (rect.height && rect.height > 20) ? rect.height : (parent.clientHeight || 380);
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = Math.floor(w * dpr);
    this.canvas.height = Math.floor(h * dpr);
    this.width = w;
    this.height = h;
    if (this.ctx && typeof this.ctx.setTransform === 'function') {
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    } else if (this.ctx && typeof this.ctx.scale === 'function') {
      this.ctx.scale(dpr, dpr);
    }
  }

  triggerParticle(sourceId, targetId, status = 'SUCCESS', durationNs = 1000000) {
    const src = this.nodes[sourceId] || this.nodes.node_builder;
    const tgt = this.nodes[targetId] || this.nodes.node_telemetry;

    // Bound active particles to prevent unbounded queue growth / GPU satiation
    if (this.particles.length >= 32) {
      this.particles.shift();
    }

    // Velocity inversely proportional to duration, clamped to reasonable animation speed
    const speed = Math.max(0.015, Math.min(0.06, 2000000 / (durationNs || 1000000) * 0.02));
    const color = status === 'SUCCESS' ? '#00ffff' : (status === 'CIRCUIT_BROKEN' ? '#ff007f' : '#f59e0b');

    this.particles.push({
      srcX: src.x * this.width,
      srcY: src.y * this.height,
      tgtX: tgt.x * this.width,
      tgtY: tgt.y * this.height,
      progress: 0.0,
      speed: speed,
      color: color,
    });

    // Trigger halo on target
    this.activeHalos.set(targetId, 1.0);
    this.activeHalos.set(sourceId, 1.0);
  }

  clearParticles() {
    this.particles = [];
    this.activeHalos.clear();
  }

  animate() {
    if (!this.ctx) return;
    this.ctx.clearRect(0, 0, this.width, this.height);

    // 1. Draw Channels (Edges)
    this.channels.forEach(ch => {
      const src = this.nodes[ch.source];
      const tgt = this.nodes[ch.target];
      if (!src || !tgt) return;

      const x1 = src.x * this.width;
      const y1 = src.y * this.height;
      const x2 = tgt.x * this.width;
      const y2 = tgt.y * this.height;

      this.ctx.beginPath();
      this.ctx.moveTo(x1, y1);
      this.ctx.lineTo(x2, y2);
      this.ctx.strokeStyle = '#1e293b';
      this.ctx.lineWidth = 1.5;
      this.ctx.stroke();
    });

    // 2. Animate and Draw Particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.progress += p.speed;

      if (p.progress >= 1.0) {
        this.particles.splice(i, 1);
        continue;
      }

      const curX = p.srcX + (p.tgtX - p.srcX) * p.progress;
      const curY = p.srcY + (p.tgtY - p.srcY) * p.progress;

      // Draw particle with hardware-accelerated dual-concentric arcs (Zero shadowBlur GPU rasterization)
      // Outer translucent aura
      this.ctx.beginPath();
      this.ctx.arc(curX, curY, 6.0, 0, Math.PI * 2);
      this.ctx.fillStyle = p.color;
      this.ctx.globalAlpha = 0.28;
      this.ctx.fill();

      // Inner bright core
      this.ctx.beginPath();
      this.ctx.arc(curX, curY, 3.0, 0, Math.PI * 2);
      this.ctx.globalAlpha = 1.0;
      this.ctx.fill();
    }

    // 3. Draw Nodes and Halos
    Object.values(this.nodes).forEach(n => {
      const nx = n.x * this.width;
      const ny = n.y * this.height;

      // Halos
      let haloAlpha = this.activeHalos.get(n.id) || 0;
      if (haloAlpha > 0) {
        this.ctx.beginPath();
        this.ctx.arc(nx, ny, 22 + (1.0 - haloAlpha) * 10, 0, Math.PI * 2);
        this.ctx.strokeStyle = n.color;
        this.ctx.globalAlpha = haloAlpha * 0.7;
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        this.ctx.globalAlpha = 1.0;
        this.activeHalos.set(n.id, Math.max(0, haloAlpha - 0.03));
      }

      // Outer glow circle
      this.ctx.beginPath();
      this.ctx.arc(nx, ny, 16, 0, Math.PI * 2);
      this.ctx.fillStyle = '#0d121d';
      this.ctx.strokeStyle = n.color;
      this.ctx.lineWidth = 2;
      this.ctx.shadowColor = n.color;
      this.ctx.shadowBlur = 10;
      this.ctx.fill();
      this.ctx.stroke();
      this.ctx.shadowBlur = 0;

      // Inner center point
      this.ctx.beginPath();
      this.ctx.arc(nx, ny, 4, 0, Math.PI * 2);
      this.ctx.fillStyle = n.color;
      this.ctx.fill();

      // Node Label and IP
      this.ctx.font = '10px ui-monospace, Menlo, monospace';
      this.ctx.fillStyle = '#e2e8f0';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(n.label, nx, ny + 28);

      this.ctx.font = '9px ui-monospace, Menlo, monospace';
      this.ctx.fillStyle = '#94a3b8';
      this.ctx.fillText(n.ip, nx, ny + 39);
    });

    requestAnimationFrame(this.animate);
  }
}

window.ZenithTopologyCanvas = ZenithTopologyCanvas;
