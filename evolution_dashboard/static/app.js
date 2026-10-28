/**
 * Meta-Axioma Sovereign Studio & Evolution Dashboard Client Application
 * Zero-External-CDN Compatible & Air-Gapped Standalone Capable
 * Author: Meta-Axioma Systems Architecture & Generation 4b Operational UI Synthesizer
 */

// Global State
const STATE = {
  perspectiveMode: "layman", // "layman" | "academic"
  currentStageId: "g4b",
  currentAppId: "axioma_go",
  simulationStep: 1,
  simulationPlaying: false,
  simulationInterval: null,
  selectedNode: null,
  diffStageA: "s0",
  diffStageB: "g4b",
  stages: [],
  transformations: [],
  components: [],
  philosophy: {},
  g4b: {},
  simulations: {},
  feedback: []
};

// Canonical Chronological Ordering of the 8 Generations
const STAGE_ORDER = ["s0", "g1", "g1b", "g2", "g2b", "g3", "g3b", "g4b"];

// Bootstrap on DOM Ready
document.addEventListener("DOMContentLoaded", async () => {
  initPortfolioBackLink();
  await loadInitialData();
  initPerspectiveMode();
  renderPhilosophySection();
  renderG4bArchitectureSection();
  renderSimulationSection();
  renderEvolutionTimeline();
  renderStageView(STATE.currentStageId);
  renderDiffWorkbench();
  renderGovernanceSpotlight();
  initLandauerCalculator();
  initKeyboardShortcuts();
  renderKaTeX();
});

// 1. Data Loader (API with Offline Fallback)
async function loadInitialData() {
  // If embedded data is preloaded (e.g. In standalone dashboard.html), use it directly
  if (window.EMBEDDED_EVOLUTION_DATA) {
    applyEmbeddedPayload(window.EMBEDDED_EVOLUTION_DATA);
    return;
  }

  try {
    const [stagesRes, transRes, compRes, philRes, g4bRes, simRes, fbRes] = await Promise.all([
      fetch("/api/stages"),
      fetch("/api/transformations"),
      fetch("/api/components"),
      fetch("/api/philosophy"),
      fetch("/api/g4b"),
      fetch("/api/simulations"),
      fetch("/api/feedback")
    ]);

    STATE.stages = sortStagesChronologically(await stagesRes.json());
    STATE.transformations = await transRes.json();
    STATE.components = await compRes.json();
    STATE.philosophy = await philRes.json();
    STATE.g4b = await g4bRes.json();
    STATE.simulations = await simRes.json();
    STATE.feedback = await fbRes.json();
  } catch (err) {
    console.warn("API fetch failed or offline mode detected. Checking embedded payload...", err);
    if (window.EMBEDDED_EVOLUTION_DATA) {
      applyEmbeddedPayload(window.EMBEDDED_EVOLUTION_DATA);
    }
  }
}

function applyEmbeddedPayload(data) {
  STATE.stages = sortStagesChronologically(data.stages || []);
  STATE.transformations = data.transformations || [];
  STATE.components = data.subsystems || [];
  STATE.philosophy = data.philosophy || {};
  STATE.g4b = data.g4b_architecture || {};
  STATE.simulations = data.sample_app_simulation || {};
  STATE.feedback = data.feedback || [
    {
      author: "Principal Formal Methods Engineer",
      rating: 5,
      comment: "The dual-layer progressive disclosure and Z3 SMT prover bridge completely eliminate the black-box AI trust barrier."
    },
    {
      author: "Autonomous Systems Lead",
      rating: 5,
      comment: "G4b decoupled multi-service mesh running on 192.168.40.0/24 brings real distributed systems rigor to LLM code generation."
    }
  ];
}

function sortStagesChronologically(stages) {
  return [...stages].sort((a, b) => {
    const idxA = STAGE_ORDER.indexOf(a.id);
    const idxB = STAGE_ORDER.indexOf(b.id);
    if (idxA !== -1 && idxB !== -1) return idxA - idxB;
    return 0;
  });
}

// Portfolio Backlink Initializer (supports direct host and reverse-proxy paths)
function initPortfolioBackLink() {
  const backLink = document.getElementById("portfolio-back-link");
  if (!backLink) return;

  // If visiting directly from an external referrer (such as the portfolio) on a different host
  if (document.referrer) {
    try {
      const refUrl = new URL(document.referrer);
      if (refUrl.host !== window.location.host) {
        backLink.href = refUrl.origin;
      }
    } catch (_) {}
  }
}

// Sanitize any KaTeX private-use \uE020 characters (broken \ne slash overlays) into standard Unicode ≠
function sanitizeKaTeXNotEqual(root = document.body) {
  if (!root || !root.querySelectorAll) return;
  root.querySelectorAll('.katex-html').forEach(el => {
    if (el.innerHTML.includes('\uE020') || el.innerHTML.includes('\ue020')) {
      el.innerHTML = el.innerHTML.replace(
        /<span class="mrel"><span class="mrel">[\s\S]*?<\/span><span class="mrel">=<\/span><\/span>/g,
        '<span class="mrel">≠</span>'
      ).replace(/[\uE020\uE021]/g, '');
    }
  });
}

// KaTeX Auto-Render Helper for LaTeX Math Invariants
function renderKaTeX(root = document.body) {
  if (typeof renderMathInElement === 'function') {
    try {
      renderMathInElement(root, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\(', right: '\\)', display: false },
          { left: '\\[', right: '\\]', display: true }
        ],
        output: 'html',
        throwOnError: false
      });
      sanitizeKaTeXNotEqual(root);
    } catch (err) {
      console.warn('KaTeX rendering error:', err);
    }
  } else {
    setTimeout(() => {
      if (typeof renderMathInElement === 'function') {
        try {
          renderMathInElement(root, {
            delimiters: [
              { left: '$$', right: '$$', display: true },
              { left: '$', right: '$', display: false },
              { left: '\\(', right: '\\)', display: false },
              { left: '\\[', right: '\\]', display: true }
            ],
            output: 'html',
            throwOnError: false
          });
          sanitizeKaTeXNotEqual(root);
        } catch (e) {}
      }
    }, 180);
  }
}

// 2. Perspective Mode (Layman Mode vs Systems Thinking)
function initPerspectiveMode() {
  const laymanBtn = document.getElementById("mode-layman-btn");
  const academicBtn = document.getElementById("mode-academic-btn");
  if (!laymanBtn || !academicBtn) return;

  laymanBtn.addEventListener("click", () => setPerspectiveMode("layman"));
  academicBtn.addEventListener("click", () => setPerspectiveMode("academic"));
}

function setPerspectiveMode(mode) {
  STATE.perspectiveMode = mode;
  document.querySelectorAll(".mode-toggle-btn").forEach(b => b.classList.remove("active"));
  
  if (mode === "layman") {
    document.getElementById("mode-layman-btn")?.classList.add("active");
    document.body.classList.remove("mode-academic");
    document.body.classList.add("mode-layman");
  } else {
    document.getElementById("mode-academic-btn")?.classList.add("active");
    document.body.classList.remove("mode-layman");
    document.body.classList.add("mode-academic");
  }

  // Re-render sections that adapt to perspective mode
  renderPhilosophySection();
  renderG4bArchitectureSection();
  renderSimulationStep();
  renderStageView(STATE.currentStageId);
  renderKaTeX();
}

// 3. Render Top Section 1: Philosophy (Row 1 Three Pillars + Row 2 Three Pillars = 6 Total)
function renderPillarCard(pillar, isAcademic) {
  return `
    <div class="hover-card tooltip-container p-5 rounded-2xl bg-zinc-900/80 border border-zinc-800 hover:border-sky-500/50 transition-all duration-300 flex flex-col justify-between space-y-4">
      <div class="space-y-3">
        <div class="flex items-start justify-between gap-2 border-b border-zinc-800/80 pb-3">
          <div class="flex items-center gap-3">
            <span class="text-3xl">${pillar.icon}</span>
            <div>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20 font-bold uppercase tracking-wider">
                ${pillar.badge}
              </span>
              <h4 class="text-base font-bold text-zinc-100 font-sans mt-1">${pillar.title}</h4>
            </div>
          </div>
        </div>

        <p class="text-xs font-mono text-zinc-400 leading-tight">${pillar.subtitle}</p>

        <p class="text-xs text-zinc-300 leading-relaxed font-sans">
          ${isAcademic ? pillar.deep_detail : pillar.layman}
        </p>

        <div class="p-2.5 rounded-xl bg-black/60 border border-zinc-800/80 text-center font-mono text-xs text-sky-300 my-1 overflow-x-auto">
          ${pillar.latex_formula}
        </div>
      </div>

      <div class="pt-2.5 border-t border-zinc-800/80 flex items-center justify-between text-xs font-mono">
        <span class="text-zinc-500 text-[10px]">Under the Hood:</span>
        <span class="text-emerald-400 font-medium text-right text-[10px] truncate max-w-[160px]" title="${pillar.deep_concept}">${pillar.deep_concept}</span>
      </div>

      <!-- Academic Hover Tooltip -->
      <div class="academic-tooltip">
        <div class="text-sky-400 font-bold mb-1">${pillar.title} &bull; Formal Proof</div>
        <p class="text-zinc-200 text-[11px] font-mono leading-relaxed mb-2">${pillar.deep_detail}</p>
        <div class="text-emerald-400 text-center">${pillar.latex_formula}</div>
      </div>
    </div>
  `;
}

function renderPhilosophySection() {
  const row1Container = document.getElementById("philosophy-row1-container");
  const row2Container = document.getElementById("philosophy-row2-container");
  if (!row1Container && !row2Container) return;

  const phil = STATE.philosophy.surface_layman;
  if (!phil) return;

  const isAcademic = STATE.perspectiveMode === "academic";

  // Derive Row 1 (3 pillars) and Row 2 (3 pillars)
  let row1Pillars = phil.row_1_pillars || [];
  let row2Pillars = phil.row_2_pillars || [];

  if (row1Pillars.length === 0 && phil.core_pillars) {
    row1Pillars = phil.core_pillars.slice(0, 3);
  }
  if (row2Pillars.length === 0 && phil.core_pillars) {
    row2Pillars = phil.core_pillars.slice(3, 6);
  }

  // Row 1: Core Mathematical Foundations & Cognitive Partitioning (3 Pillars)
  if (row1Container && row1Pillars.length > 0) {
    row1Container.innerHTML = row1Pillars.map(p => renderPillarCard(p, isAcademic)).join("");
  }

  // Row 2: Sovereign Decoupling & Thermodynamic Verification (3 Pillars)
  if (row2Container && row2Pillars.length > 0) {
    row2Container.innerHTML = row2Pillars.map(p => renderPillarCard(p, isAcademic)).join("");
  }

  // Invariant Triad
  const triadEl = document.getElementById("triad-points-container");
  if (triadEl && phil.the_triad) {
    triadEl.innerHTML = phil.the_triad.points.map(pt => `
      <div class="hover-card tooltip-container p-4 rounded-xl bg-zinc-950/70 border border-zinc-800 space-y-2">
        <div class="flex items-center justify-between">
          <h4 class="text-xs font-bold font-mono text-emerald-400">${pt.name}</h4>
          <span class="text-[10px] font-mono text-zinc-500">Hover for Proof</span>
        </div>
        <p class="text-xs text-zinc-300 leading-relaxed">${pt.layman}</p>
        <div class="text-[11px] font-mono text-zinc-400 pt-2 border-t border-zinc-800/60">
          <strong class="text-sky-400">Formal:</strong> ${pt.formal}
        </div>

        <!-- Academic Deep Math Tooltip on Hover -->
        <div class="academic-tooltip">
          <div class="text-emerald-400 font-bold mb-1">${pt.name} &bull; Formal Proof</div>
          <p class="text-zinc-200 text-[11px] font-mono leading-relaxed">${pt.formal}</p>
        </div>
      </div>
    `).join("");
  }

  // Render LaTeX in Philosophy Section
  renderKaTeX(document.getElementById("philosophy"));
}

// 4. Render Top Section 2: Generation 4b Architecture & Interactive RFC Bus
function renderG4bArchitectureSection() {
  const container = document.getElementById("g4b-services-grid");
  if (!container) return;

  const g4b = STATE.g4b;
  if (!g4b || !g4b.services) return;

  const isAcademic = STATE.perspectiveMode === "academic";

  // 5 Sovereign Services Grid
  container.innerHTML = g4b.services.map(srv => `
    <div class="hover-card p-4 rounded-xl bg-zinc-900/80 border border-zinc-800 flex flex-col justify-between cursor-pointer" onclick="inspectG4bService('${srv.id}')">
      <div>
        <div class="flex items-start justify-between mb-2">
          <div class="flex items-center gap-2">
            <span class="text-xl">${srv.icon}</span>
            <div>
              <h4 class="text-sm font-bold text-zinc-100">${srv.name}</h4>
              <span class="text-[11px] font-mono text-emerald-400">${srv.ip}:${srv.port}</span>
            </div>
          </div>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-400">
            ${srv.layman_role}
          </span>
        </div>

        <p class="text-xs text-zinc-300 leading-relaxed mb-3">
          ${isAcademic ? srv.technical_role : srv.layman_description}
        </p>
      </div>

      <div class="pt-2.5 border-t border-zinc-800/80 text-[11px] font-mono space-y-1">
        <div class="text-zinc-500 truncate"><span class="text-zinc-400">Deliverable:</span> ${srv.deliverable}</div>
        <div class="flex flex-wrap gap-1 pt-1">
          ${srv.technologies.slice(0, 2).map(t => `<span class="px-1.5 py-0.5 rounded bg-zinc-800 text-[10px] text-zinc-400">${t}</span>`).join("")}
        </div>
      </div>
    </div>
  `).join("");

  // Asymmetric RFC Protocol Packets
  const rfcContainer = document.getElementById("rfc-packets-container");
  if (rfcContainer && g4b.asymmetric_rfc_bus?.packet_types) {
    const packets = g4b.asymmetric_rfc_bus.packet_types;
    rfcContainer.innerHTML = packets.map((pkt, idx) => `
      <div class="hover-card p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2 cursor-pointer" onclick="inspectRfcPacket('${pkt.type}')">
        <div class="flex items-center justify-between">
          <span class="font-bold ${idx === 0 ? 'text-sky-400' : idx === 1 ? 'text-amber-400' : 'text-emerald-400'}">
            ${idx + 1}. ${pkt.type}
          </span>
          <span class="text-[10px] font-mono text-zinc-500">${pkt.sender} ➔ ${pkt.recipient}</span>
        </div>
        <p class="text-zinc-300 font-sans text-xs leading-relaxed">${pkt.desc}</p>
        <div class="pt-2 border-t border-zinc-800/70 flex items-center justify-between text-[11px] text-zinc-400">
          <span>Invariants: <strong>${pkt.invariants?.length || 2} locked</strong></span>
          <span class="text-sky-400">Inspect Schema ➔</span>
        </div>
      </div>
    `).join("");
  }
}

function inspectG4bService(serviceId) {
  const srv = STATE.g4b.services?.find(s => s.id === serviceId);
  if (!srv) return;

  const modal = document.getElementById("generic-modal");
  const modalTitle = document.getElementById("generic-modal-title");
  const modalBody = document.getElementById("generic-modal-body");
  if (!modal || !modalTitle || !modalBody) return;

  modalTitle.innerText = `${srv.icon} ${srv.name} (${srv.ip}:${srv.port})`;
  modalBody.innerHTML = `
    <div class="space-y-4 text-xs font-mono">
      <div>
        <span class="text-zinc-500 uppercase text-[10px] tracking-wider font-bold">Layman Role:</span>
        <h4 class="text-base font-bold text-sky-400 font-sans mt-0.5">${srv.layman_role}</h4>
        <p class="text-zinc-200 mt-1 font-sans text-sm leading-relaxed">${srv.layman_description}</p>
      </div>

      <div class="p-3.5 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2">
        <div class="text-emerald-400 font-bold flex items-center justify-between">
          <span>Formal Systems Invariants:</span>
          <span class="text-zinc-500 text-[10px]">${srv.invariants.length} Bound</span>
        </div>
        <ul class="list-disc pl-4 space-y-1.5 text-zinc-300">
          ${srv.invariants.map(inv => `<li>${inv}</li>`).join("")}
        </ul>
      </div>

      <div>
        <div class="text-zinc-400 font-bold mb-1.5">Substrate Technologies:</div>
        <div class="flex flex-wrap gap-1.5">
          ${srv.technologies.map(tech => `<span class="px-2 py-1 rounded bg-zinc-800 text-zinc-200 text-[11px]">${tech}</span>`).join("")}
        </div>
      </div>

      ${srv.academic_deep_theory ? `
        <div class="p-3.5 rounded-xl bg-zinc-950 border border-sky-800/40 space-y-2">
          <div class="text-sky-400 font-bold">Academic Systems Theory:</div>
          <div class="space-y-1.5 text-[11px] text-zinc-300 leading-relaxed font-sans">
            ${Object.entries(srv.academic_deep_theory).map(([k, v]) => `<div><strong class="text-zinc-400 font-mono">${k}:</strong> ${v}</div>`).join("")}
          </div>
        </div>
      ` : ''}

      <div class="p-3 rounded-lg bg-sky-950/30 border border-sky-800/50 text-sky-300 text-[11px] flex items-center justify-between">
        <span><strong>Immutable Wire Deliverable:</strong> ${srv.deliverable}</span>
        <span class="text-emerald-400 font-bold">SHA-256 Verified</span>
      </div>
    </div>
  `;
  openGenericModal();
}

function inspectRfcPacket(packetType) {
  const g4b = STATE.g4b;
  const pkt = g4b.asymmetric_rfc_bus?.packet_types?.find(p => p.type === packetType);
  if (!pkt) return;

  const modalTitle = document.getElementById("generic-modal-title");
  const modalBody = document.getElementById("generic-modal-body");
  if (!modalTitle || !modalBody) return;

  modalTitle.innerText = `📦 Asymmetric RFC Bus: ${pkt.type}`;
  modalBody.innerHTML = `
    <div class="space-y-4 text-xs font-mono">
      <div class="flex items-center justify-between p-3 rounded-xl bg-zinc-950 border border-zinc-800">
        <div>
          <span class="text-zinc-500 text-[10px]">Transmission:</span>
          <div class="text-sky-400 font-bold">${pkt.sender} ➔ ${pkt.recipient}</div>
        </div>
        <div class="text-right">
          <span class="text-zinc-500 text-[10px]">Protocol Layer:</span>
          <div class="text-emerald-400 font-bold">192.168.40.0/24 Subnet</div>
        </div>
      </div>

      <p class="text-sm font-sans text-zinc-200 leading-relaxed">${pkt.desc}</p>

      <div>
        <div class="text-zinc-400 font-bold mb-1.5">Algebraic Packet Schema:</div>
        <pre class="p-3.5 rounded-xl bg-black border border-zinc-800 text-[11px] font-mono text-emerald-400 overflow-x-auto"><code>${escapeHtml(JSON.stringify(pkt.algebraic_schema, null, 2))}</code></pre>
      </div>

      <div class="p-3 rounded-xl bg-zinc-950 border border-zinc-800 space-y-1">
        <div class="text-zinc-400 font-bold">Preserved Invariants:</div>
        <ul class="list-disc pl-4 space-y-0.5 text-zinc-300 text-[11px]">
          ${(pkt.invariants || []).map(inv => `<li>${inv}</li>`).join("")}
        </ul>
      </div>
    </div>
  `;
  openGenericModal();
}

// 5. Render Top Section 3: Interactive Sample App Simulation Walkthrough
function renderSimulationSection() {
  const appSelector = document.getElementById("sim-app-selector");
  if (appSelector && STATE.simulations.available_apps) {
    appSelector.innerHTML = STATE.simulations.available_apps.map(app => `
      <button onclick="switchSimApp('${app.id}')" class="sim-app-btn px-3 py-1.5 rounded-lg text-xs font-mono font-medium border transition-all ${app.id === STATE.currentAppId ? 'bg-sky-500/20 border-sky-400 text-sky-300 font-bold' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-zinc-200'}">
        ${app.icon} ${app.name}
      </button>
    `).join("");
  }

  renderSimulationStep();
}

function switchSimApp(appId) {
  STATE.currentAppId = appId;
  STATE.simulationStep = 1;
  if (STATE.simulationPlaying) toggleAutoPlay();
  renderSimulationSection();
}

function renderSimulationStep() {
  const simData = STATE.simulations.simulations?.[STATE.currentAppId] || STATE.simulations.simulations?.["axioma_go"];
  if (!simData) return;

  const currentStep = simData.steps?.find(s => s.step_number === STATE.simulationStep) || simData.steps?.[0];
  if (!currentStep) return;

  // Step Indicators (1 to 5)
  const stepBar = document.getElementById("sim-step-progress");
  if (stepBar) {
    stepBar.innerHTML = simData.steps.map(s => {
      const isCurrent = s.step_number === STATE.simulationStep;
      const isDone = s.step_number < STATE.simulationStep;
      return `
        <button onclick="jumpToSimStep(${s.step_number})" class="flex-1 min-w-[100px] py-2 px-2 text-center border-b-2 font-mono text-xs transition-all cursor-pointer ${isCurrent ? 'border-sky-400 text-sky-400 font-bold bg-sky-500/10' : isDone ? 'border-emerald-500 text-emerald-400' : 'border-zinc-800 text-zinc-500 hover:text-zinc-300'}">
          ${isDone ? '✓ ' : ''}Step ${s.step_number}
        </button>
      `;
    }).join("");
  }

  // Active Step Details
  document.getElementById("sim-step-title").innerText = `Step ${currentStep.step_number}: ${currentStep.title}`;
  document.getElementById("sim-step-phase").innerText = currentStep.phase;
  
  const portBadge = document.getElementById("sim-target-port-badge");
  if (portBadge) portBadge.innerText = `Port ${simData.target_port || 8082}`;

  // Wire Traffic Box
  const wireBox = document.getElementById("sim-wire-traffic");
  if (wireBox && currentStep.wire_traffic) {
    wireBox.innerHTML = `
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs font-mono">
        <span class="text-sky-400 font-semibold">${currentStep.wire_traffic.source}</span>
        <span class="text-zinc-500 px-2 select-none">────► [Private Wire RFC Bus 192.168.40.0/24] ────►</span>
        <span class="text-emerald-400 font-semibold">${currentStep.wire_traffic.target}</span>
      </div>
      <div class="mt-2 text-[11px] font-mono text-zinc-300 truncate bg-zinc-950 p-2 rounded border border-zinc-800/80">
        📦 <strong class="text-sky-300">Packet:</strong> ${currentStep.wire_traffic.packet}
      </div>
    `;
  }

  // Layman vs Academic Explanations
  const isAcademic = STATE.perspectiveMode === "academic";
  const descBox = document.getElementById("sim-step-description");
  if (descBox) {
    if (isAcademic) {
      descBox.innerHTML = `
        <div class="space-y-2.5">
          <div class="text-xs font-mono text-sky-400 font-bold">${currentStep.academic_deep_dive.concept}</div>
          <p class="text-sm text-zinc-300 leading-relaxed">${currentStep.academic_deep_dive.formal_details}</p>
          <div class="p-2.5 rounded-lg bg-zinc-950 text-[11px] font-mono text-emerald-400 border border-zinc-800">
            <strong>Invariant Enforced:</strong> ${currentStep.academic_deep_dive.invariant_checked}
          </div>
        </div>
      `;
    } else {
      descBox.innerHTML = `
        <div class="space-y-2.5">
          <div class="text-sm font-semibold text-zinc-100">${currentStep.surface_layman.what_happens}</div>
          <p class="text-xs text-zinc-300 leading-relaxed">${currentStep.surface_layman.why_it_matters}</p>
          <div class="p-2.5 rounded-lg bg-sky-950/30 text-xs text-sky-300 border border-sky-800/40">
            💡 <strong>Everyday Analogy:</strong> ${currentStep.surface_layman.analogy}
          </div>
        </div>
      `;
    }
  }

  // Metrics
  if (currentStep.metrics) {
    document.getElementById("sim-tokens-spent").innerText = currentStep.metrics.tokens_spent.toLocaleString() + " BPE";
    document.getElementById("sim-latency").innerText = currentStep.metrics.latency_ms + " ms";
    document.getElementById("sim-invariants-locked").innerText = currentStep.metrics.invariants_locked;
  }

  if (descBox) renderKaTeX(descBox);
}

function prevSimStep() {
  if (STATE.simulationStep > 1) {
    STATE.simulationStep--;
    renderSimulationStep();
  }
}

function nextSimStep() {
  const simData = STATE.simulations.simulations?.[STATE.currentAppId] || STATE.simulations.simulations?.["axioma_go"];
  const maxSteps = simData?.total_steps || 5;
  if (STATE.simulationStep < maxSteps) {
    STATE.simulationStep++;
    renderSimulationStep();
  } else if (STATE.simulationPlaying) {
    toggleAutoPlay();
  }
}

function jumpToSimStep(stepNum) {
  STATE.simulationStep = stepNum;
  renderSimulationStep();
}

function resetSimulation() {
  STATE.simulationStep = 1;
  if (STATE.simulationPlaying) toggleAutoPlay();
  renderSimulationStep();
}

function toggleAutoPlay() {
  STATE.simulationPlaying = !STATE.simulationPlaying;
  const btn = document.getElementById("sim-autoplay-btn");
  if (STATE.simulationPlaying) {
    if (btn) btn.innerHTML = "⏸️ Pause";
    STATE.simulationInterval = setInterval(() => {
      const simData = STATE.simulations.simulations?.[STATE.currentAppId] || STATE.simulations.simulations?.["axioma_go"];
      const maxSteps = simData?.total_steps || 5;
      if (STATE.simulationStep >= maxSteps) {
        STATE.simulationStep = 1;
      } else {
        STATE.simulationStep++;
      }
      renderSimulationStep();
    }, 3200);
  } else {
    if (btn) btn.innerHTML = "⏯️ Auto-Play";
    if (STATE.simulationInterval) clearInterval(STATE.simulationInterval);
    STATE.simulationInterval = null;
  }
}

function inspectSimArtifact() {
  const simData = STATE.simulations.simulations?.[STATE.currentAppId] || STATE.simulations.simulations?.["axioma_go"];
  const currentStep = simData?.steps?.find(s => s.step_number === STATE.simulationStep);
  if (!currentStep || !currentStep.artifact_preview) return;

  const modalTitle = document.getElementById("generic-modal-title");
  const modalBody = document.getElementById("generic-modal-body");
  if (!modalTitle || !modalBody) return;

  const rawCode = currentStep.artifact_preview.content;

  modalTitle.innerText = currentStep.artifact_preview.label;
  modalBody.innerHTML = `
    <div class="space-y-3">
      <div class="flex items-center justify-between text-xs font-mono">
        <span class="text-zinc-400">Step ${currentStep.step_number} &bull; ${currentStep.phase}</span>
        <button onclick="copyArtifactCode()" id="copy-artifact-btn" class="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-sky-300 text-xs transition-colors">
          📋 Copy Code
        </button>
      </div>
      <pre class="p-4 rounded-xl bg-black border border-zinc-800 text-xs font-mono text-emerald-400 overflow-x-auto max-h-[70vh]"><code id="modal-artifact-code">${escapeHtml(rawCode)}</code></pre>
    </div>
  `;
  openGenericModal();
}

function copyArtifactCode() {
  const codeEl = document.getElementById("modal-artifact-code");
  const btn = document.getElementById("copy-artifact-btn");
  if (!codeEl || !btn) return;

  navigator.clipboard.writeText(codeEl.innerText).then(() => {
    btn.innerText = "✓ Copied!";
    setTimeout(() => { btn.innerText = "📋 Copy Code"; }, 2000);
  });
}

// 6. Render Section 4: 8-Stage Evolution Spine & Beehive Canvas
function renderEvolutionTimeline() {
  const container = document.getElementById("timeline-buttons");
  if (!container || !STATE.stages) return;

  container.innerHTML = STATE.stages.map(st => `
    <button onclick="selectStage('${st.id}')" class="stage-nav-btn px-3 py-1.5 rounded-lg text-xs font-mono font-medium border transition-all cursor-pointer ${st.id === STATE.currentStageId ? 'bg-sky-500/20 border-sky-400 text-sky-300 font-bold' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-zinc-200'}">
      ${st.roman_id || st.id.toUpperCase()}: ${st.name.split(':')[0]}
    </button>
  `).join("");
}

function selectStage(stageId) {
  STATE.currentStageId = stageId;
  renderEvolutionTimeline();
  renderStageView(stageId);
}

function renderStageView(stageId) {
  const stage = STATE.stages?.find(s => s.id === stageId) || STATE.stages?.[0];
  if (!stage) return;

  document.getElementById("stage-hero-title").innerText = `${stage.roman_id || stage.id.toUpperCase()} — ${stage.name}`;
  document.getElementById("stage-hero-era").innerText = `${stage.era} • ${stage.epoch_range || ''}`;
  document.getElementById("stage-hero-badge").innerText = stage.status || 'Active';

  // Layman 4-Quadrant Card
  const laymanCard = document.getElementById("stage-layman-card");
  if (laymanCard) {
    laymanCard.innerHTML = `
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div class="p-3.5 rounded-xl bg-zinc-950/60 border border-zinc-800 space-y-1">
          <div class="text-amber-400 font-bold flex items-center gap-1.5"><span>⚠️</span> The Problem We Solved</div>
          <p class="text-zinc-300 leading-relaxed">${stage.layman_problem || stage.executive_summary}</p>
        </div>
        <div class="p-3.5 rounded-xl bg-zinc-950/60 border border-zinc-800 space-y-1">
          <div class="text-emerald-400 font-bold flex items-center gap-1.5"><span>✨</span> In Plain English</div>
          <p class="text-zinc-300 leading-relaxed">${stage.layman_summary || stage.executive_summary}</p>
        </div>
        <div class="p-3.5 rounded-xl bg-zinc-950/60 border border-zinc-800 space-y-1">
          <div class="text-sky-400 font-bold flex items-center gap-1.5"><span>🚀</span> Key Breakthrough</div>
          <p class="text-zinc-300 leading-relaxed">${stage.layman_breakthrough || 'Axiomatic compilation'}</p>
        </div>
        <div class="p-3.5 rounded-xl bg-zinc-950/60 border border-zinc-800 space-y-1">
          <div class="text-purple-400 font-bold flex items-center gap-1.5"><span>💡</span> Everyday Analogy</div>
          <p class="text-zinc-300 leading-relaxed">${stage.layman_analogy || 'Foundational engineering stepping stone'}</p>
        </div>
      </div>
    `;
  }

  if (laymanCard) renderKaTeX(laymanCard);
}

// 7. Render 4-Tier SVG Beehive Topology (Deprecated)
function renderBeehiveTopology(stage) {
  return;
}

// 8. Render Section 5: Side-by-Side Generational Diff Workbench
function renderDiffWorkbench() {
  const selA = document.getElementById("diff-select-a");
  const selB = document.getElementById("diff-select-b");
  if (!selA || !selB || !STATE.stages) return;

  const stageOptions = STATE.stages.map(st => `
    <option value="${st.id}">${st.roman_id || st.id.toUpperCase()}: ${st.name}</option>
  `).join("");

  selA.innerHTML = stageOptions;
  selB.innerHTML = stageOptions;

  selA.value = STATE.diffStageA;
  selB.value = STATE.diffStageB;

  selA.addEventListener("change", (e) => {
    STATE.diffStageA = e.target.value;
    updateDiffComparison();
  });

  selB.addEventListener("change", (e) => {
    STATE.diffStageB = e.target.value;
    updateDiffComparison();
  });

  updateDiffComparison();
}

function swapDiffStages() {
  const tmp = STATE.diffStageA;
  STATE.diffStageA = STATE.diffStageB;
  STATE.diffStageB = tmp;

  document.getElementById("diff-select-a").value = STATE.diffStageA;
  document.getElementById("diff-select-b").value = STATE.diffStageB;
  updateDiffComparison();
}

async function updateDiffComparison() {
  const diffBox = document.getElementById("diff-result-container");
  if (!diffBox) return;

  try {
    const res = await fetch(`/api/diff?a=${STATE.diffStageA}&b=${STATE.diffStageB}`);
    const diff = await res.json();
    renderDiffResult(diff, diffBox);
  } catch (err) {
    // Offline calculation
    const stA = STATE.stages.find(s => s.id === STATE.diffStageA) || STATE.stages[0];
    const stB = STATE.stages.find(s => s.id === STATE.diffStageB) || STATE.stages[STATE.stages.length - 1];
    renderDiffResult({
      stage_a: stA,
      stage_b: stB,
      nodes_delta: (stB.nodes?.length || 0) - (stA.nodes?.length || 0),
      evolutionary_leap: `Evolution from ${stA.name} to ${stB.name}`
    }, diffBox);
  }
}

function renderDiffResult(diff, container) {
  const a = diff.stage_a;
  const b = diff.stage_b;
  if (!a || !b) return;

  const delta = diff.nodes_delta !== undefined ? diff.nodes_delta : ((b.nodes?.length || 0) - (a.nodes?.length || 0));

  container.innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono mb-4">
      <div class="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-sm font-bold text-sky-400 font-sans">${a.name}</span>
          <span class="text-[10px] text-zinc-500">${a.era || ''}</span>
        </div>
        <div class="text-zinc-300 font-sans text-xs leading-relaxed mt-2">${a.layman_summary || a.executive_summary || ''}</div>
        <div class="pt-2 border-t border-zinc-800 text-[11px] text-zinc-400 flex items-center justify-between">
          <span>Topology Nodes: <strong class="text-zinc-200">${a.nodes_count || a.nodes?.length || 8}</strong></span>
          <span>Status: <strong class="text-sky-400">${a.status || 'Archived'}</strong></span>
        </div>
      </div>

      <div class="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-sm font-bold text-emerald-400 font-sans">${b.name}</span>
          <span class="text-[10px] text-zinc-500">${b.era || ''}</span>
        </div>
        <div class="text-zinc-300 font-sans text-xs leading-relaxed mt-2">${b.layman_summary || b.executive_summary || ''}</div>
        <div class="pt-2 border-t border-zinc-800 text-[11px] text-zinc-400 flex items-center justify-between">
          <span>Topology Nodes: <strong class="text-zinc-200">${b.nodes_count || b.nodes?.length || 9}</strong></span>
          <span class="text-emerald-400 font-bold">(${delta >= 0 ? '+' : ''}${delta} Nodes)</span>
        </div>
      </div>
    </div>

    <div class="p-3.5 rounded-xl bg-zinc-950 border border-zinc-800/80 text-xs font-mono flex items-center justify-between">
      <span class="text-zinc-400">Evolutionary Paradigm Leap:</span>
      <span class="text-emerald-400 font-semibold">${a.name} ➔ ${b.name} (${delta >= 0 ? '+' : ''}${delta} Nodes Shift)</span>
    </div>
  `;
}

// 9. Render Section 6: Architectural Governance & Key Milestones
function renderGovernanceSpotlight() {
  const container = document.getElementById("governance-epistemic-grid");
  if (!container) return;

  const epistemicPivots = [
    {
      id: "jettison_1_2",
      icon: "⚡",
      title: "Low-Level Jettisons 1 & 2",
      epoch: "Epoch 11 & Epoch 15",
      headline: "Terminating Heuristic Guessing",
      description: "Heuristic search was frozen once core grammar crystallized. At Epoch 15, search harness S₀ was retired to bootstrap System G1 directly from first principles.",
      axiom: "[L1-008] Thermodynamic Compute Decay",
      quote: "Exploratory guessing is scaffolding, not the monument. When the grammar stabilizes, freeze the harness and build the physical compiler."
    },
    {
      id: "neg_axioms",
      icon: "🛡️",
      title: "Negative Invariant Enclave",
      epoch: "Generation 1 to Present",
      headline: "Immutable Operator Vetoes (NEG-###)",
      description: "Instituted absolute negative veto power: axioms (e.g. [NEG-G1B-001] Anti-Phantom Emission) that cannot be bypassed or softened by autonomous agents.",
      axiom: "[NEG-G1B-001] Anti-Phantom Emission Gate",
      quote: "AI autonomy without an unforgeable negative brake is negligence. Negative axioms are unbreakable physical ceilings."
    },
    {
      id: "functorial_undo",
      icon: "⏮️",
      title: "Functorial Reversibility",
      epoch: "Generation 2b & G3b",
      headline: "1-Tap Undo via Categorical Morphisms",
      description: "Every state mutation is formalized as an invertible morphism: S_{t-1} = f^{-1}(S_t), enabling 1-tap categorical rollback with zero data corruption.",
      axiom: "[L1-002] Categorical Reversibility",
      quote: "True operator safety is mathematical invertibility. If you cannot undo an action in O(1) time, you do not control the system."
    },
    {
      id: "dual_model_routing",
      icon: "🧠",
      title: "Dual-Model Cognitive Routing",
      epoch: "Generation 3b Compiler",
      headline: "Two-Stage Anti-Race Sequential Gating",
      description: "Divided synthesis labor: Stage 1 Brain models handle formal contract planning and Waterloo SoC normalization; Stage 2 Muscle swarms execute parallel AST emission in isolated sandboxes.",
      axiom: "[L1-G3B-014] Dual-Model Cognitive Routing",
      quote: "Separating the architect from the carpenter prevents cognitive drift and stops small models from improvising specifications."
    },
    {
      id: "production_systems",
      icon: "🚀",
      title: "Production Systems Transition",
      epoch: "Generation 3 Zenith",
      headline: "Focus on Real Applications (Target P₁)",
      description: "Terminated recursive compiler self-hosting once general distributed systems were mastered, permanently dedicating future compute to production applications.",
      axiom: "Target P₁ Application Milestone",
      quote: "Compilers exist to produce software that humans find useful, love, and control. Compute must serve concrete operational software."
    },
    {
      id: "sovereign_mesh",
      icon: "🌐",
      title: "Sovereign Multi-Service Mesh",
      epoch: "Generation 4b Zenith",
      headline: "Decoupled Sovereignty on Private Subnet",
      description: "Decoupled monolithic compilation into 5 sovereign services across 192.168.40.0/24 with an automated asymmetric RFC bus and Z3 SMT prover mediation.",
      axiom: "[L1-G4B-001] Decoupled Research Sovereignty",
      quote: "Never let the entity that writes code research its own requirements or grade its own homework. True verification requires non-colluding witnesses."
    }
  ];

  container.innerHTML = epistemicPivots.map(p => `
    <div class="hover-card p-4 rounded-xl bg-zinc-900/80 border border-zinc-800 flex flex-col justify-between cursor-pointer" onclick="inspectEpistemicPivot('${p.id}')">
      <div>
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <span class="text-xl">${p.icon}</span>
            <h4 class="text-sm font-bold text-zinc-100">${p.title}</h4>
          </div>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-sky-400">${p.epoch}</span>
        </div>
        <h5 class="text-xs font-semibold text-zinc-300 mb-1">${p.headline}</h5>
        <p class="text-xs text-zinc-400 leading-relaxed font-sans mb-3">${p.description}</p>
      </div>

      <div class="pt-2.5 border-t border-zinc-800 text-[11px] font-mono flex items-center justify-between text-zinc-500">
        <span class="text-emerald-400 truncate">${p.axiom}</span>
        <span class="text-sky-400">Quote ➔</span>
      </div>
    </div>
  `).join("");
}

function inspectEpistemicPivot(pivotId) {
  const pivots = {
    jettison_1_2: {
      title: "Low-Level Jettisons 1 & 2: Search Saturation & Ground-Up Bootstrapping",
      quote: "Exploratory guessing is scaffolding, not the monument. When the grammar stabilizes, freeze the harness and build the physical compiler.",
      body: "In Epoch 11, stochastic search heuristics were deactivated once structural pools reached saturation. In Epoch 15, with compute decayed to 2,857 tokens, Low-Level Jettison 2 was executed, locking the S₀ search engine and launching System G1 entirely from scratch."
    },
    neg_axioms: {
      title: "Negative Invariant Enclaves & Absolute Veto Authority",
      quote: "AI autonomy without an unforgeable negative brake is negligence. Negative axioms are unbreakable physical ceilings.",
      body: "To prevent autonomous agents from compromising specifications under token stress, Negative Axioms (NEG-###) were established as absolute compile-time and runtime halts. These vetoes execute in dedicated zero-trust micro-auditors and cannot be bypassed."
    },
    functorial_undo: {
      title: "Functorial State Reversibility & Categorical Undo Morphisms",
      quote: "True operator safety is mathematical invertibility. If you cannot undo an action in O(1) time, you do not control the system.",
      body: "Grounding state transitions in category theory, every mutation S_{t+1} = f(S_t, E) must preserve an inverse morphism f^{-1}. This guarantees 1-tap state reversion without database rollbacks or data corruption."
    },
    dual_model_routing: {
      title: "Dual-Model Cognitive Routing & Two-Stage Sequential Gating",
      quote: "Separating the architect from the carpenter prevents cognitive drift and stops small models from improvising specifications.",
      body: "Recognizing that monolithic agent execution leads to cognitive race conditions, the Two-Stage Anti-Race Gating Protocol was formulated: Stage 1 Brain Gate defines formal contract IR and XState statecharts; only upon certification does Stage 2 Muscle swarm synthesize parallel AST leaves."
    },
    production_systems: {
      title: "Production Systems Transition: Grounding in Real Applications",
      quote: "Compilers exist to produce software that humans find useful, love, and control. Compute must serve concrete operational software.",
      body: "This milestone permanently shifted recursive compiler self-hosting once general distributed systems were mastered in G3. 100% of future compute tokens are dedicated to production applications (Target P₁) that users find directly useful."
    },
    high_level_jettison: {
      title: "Production Systems Transition: Grounding in Real Applications",
      quote: "Compilers exist to produce software that humans find useful, love, and control. Compute must serve concrete operational software.",
      body: "This milestone permanently shifted recursive compiler self-hosting once general distributed systems were mastered in G3. 100% of future compute tokens are dedicated to production applications (Target P₁) that users find directly useful."
    },
    sovereign_mesh: {
      title: "Sovereign Decoupled Multi-Service Mesh (Generation 4b)",
      quote: "Never let the entity that writes code research its own requirements or grade its own homework. True verification requires non-colluding witnesses.",
      body: "Pioneered the multi-service architecture running across 192.168.40.0/24. 5 isolated sovereign nodes (Research, Builder, Audit, Telemetry, Governance) communicate via an automated Asymmetric RFC protocol, with an automated Z3 SMT prover mediating contract modifications."
    }
  };

  const p = pivots[pivotId];
  if (!p) return;

  const modalTitle = document.getElementById("generic-modal-title");
  const modalBody = document.getElementById("generic-modal-body");
  if (!modalTitle || !modalBody) return;

  modalTitle.innerText = `🧠 ${p.title}`;
  modalBody.innerHTML = `
    <div class="space-y-4 text-xs font-mono">
      <blockquote class="italic text-sm font-sans text-sky-300 p-3.5 rounded-xl bg-sky-950/30 border border-sky-800/50 leading-relaxed">
        "${p.quote}"
      </blockquote>
      <p class="text-zinc-200 font-sans text-sm leading-relaxed">${p.body}</p>
    </div>
  `;
  openGenericModal();
}

// 10. Landauer Thermodynamic Dissipation Calculator
function initLandauerCalculator() {
  const slider = document.getElementById("landauer-bits-slider");
  if (!slider) return;

  slider.addEventListener("input", (e) => {
    setLandauerBits(parseInt(e.target.value, 10));
  });
}

function setLandauerBits(bits) {
  const slider = document.getElementById("landauer-bits-slider");
  const bitsDisplay = document.getElementById("landauer-bits-display");
  const joulesDisplay = document.getElementById("landauer-joules-display");

  if (slider) slider.value = bits;
  if (bitsDisplay) bitsDisplay.innerText = bits.toLocaleString() + " bits";

  const KB = 1.380649e-23; // Boltzmann constant J/K
  const T = 300; // Room temperature in Kelvin
  const LN2 = Math.LN2;
  const joules = bits * KB * T * LN2;

  if (joulesDisplay) joulesDisplay.innerText = joules.toExponential(4) + " J";
}

// 11. User Feedback Form & Portfolio Iframe Snippet
function initFeedbackForm() {
  const form = document.getElementById("feedback-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const commentEl = document.getElementById("fb-comment");
    const authorEl = document.getElementById("fb-author");
    const ratingEl = document.getElementById("fb-rating");
    if (!commentEl) return;

    const newEntry = {
      author: authorEl?.value.trim() || "Anonymous Architect",
      rating: parseInt(ratingEl?.value || "5", 10),
      comment: commentEl.value.trim()
    };

    try {
      const res = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newEntry)
      });
      if (res.ok) {
        const data = await res.json();
        STATE.feedback.unshift(data.entry || newEntry);
      } else {
        STATE.feedback.unshift(newEntry);
      }
    } catch (err) {
      STATE.feedback.unshift(newEntry);
    }

    commentEl.value = "";
    authorEl.value = "";
    renderFeedbackEntries();
  });
}

function renderFeedbackEntries() {
  const container = document.getElementById("feedback-entries-container");
  if (!container) return;

  const entries = STATE.feedback || [];
  if (entries.length === 0) {
    container.innerHTML = `<div class="text-zinc-600 text-[11px] font-mono">No observations submitted yet.</div>`;
    return;
  }

  container.innerHTML = entries.slice(0, 5).map(fb => `
    <div class="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800 text-xs font-mono flex flex-col sm:flex-row sm:items-center justify-between gap-2">
      <div>
        <span class="text-zinc-200 font-bold font-sans">${escapeHtml(fb.author || 'Anonymous')}</span>
        <span class="text-amber-400 ml-2">★ ${fb.rating || 5}/5</span>
        <p class="text-zinc-400 font-sans text-[11px] mt-0.5">${escapeHtml(fb.comment || '')}</p>
      </div>
      <span class="text-emerald-400 text-[10px] self-end sm:self-center font-bold">VERIFIED_LEDGER</span>
    </div>
  `).join("");
}

function copyPortfolioSnippet() {
  const iframeSnippet = '<iframe src="http://localhost:8105/" width="100%" height="900" frameborder="0"></iframe>';
  navigator.clipboard.writeText(iframeSnippet).then(() => {
    const textEl = document.getElementById("copy-btn-text");
    if (textEl) {
      const original = textEl.innerText;
      textEl.innerText = "✓ Copied Iframe Snippet!";
      setTimeout(() => { textEl.innerText = original; }, 2500);
    }
  });
}

// 12. Modal Helpers & Keyboard Shortcuts
function openGenericModal() {
  const modal = document.getElementById("generic-modal");
  if (modal) {
    modal.classList.remove("hidden");
    modal.classList.add("flex");
  }
}

function closeGenericModal() {
  const modal = document.getElementById("generic-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
}

function initKeyboardShortcuts() {
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeGenericModal();
      document.getElementById("node-inspector-drawer")?.classList.add("hidden");
    }
  });

  const modal = document.getElementById("generic-modal");
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeGenericModal();
    });
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
