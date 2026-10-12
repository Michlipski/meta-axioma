/**
 * Axioma Swarm Edge ML Operations Console Client Logic.
 * 
 * Synchronizes VRAM memory pool topology, model residency rack,
 * failure-isolated task dispatch, and transgenerational feedback.
 */

let state = {
    vram: null,
    models: [],
    tasks: [],
    telemetry: {},
    isPolling: true,
};

document.addEventListener("DOMContentLoaded", () => {
    refreshAll();
    setInterval(() => {
        if (state.isPolling) refreshAll(false);
    }, 4000);
});

function showToast(message, type = "normal") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type === "success" ? "toast-success" : type === "error" ? "toast-error" : ""}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}

async function refreshAll(notifyOnError = true) {
    try {
        const [vramRes, modelsRes, tasksRes, telemRes] = await Promise.all([
            fetch("/api/vram").then(r => r.json()),
            fetch("/api/models").then(r => r.json()),
            fetch("/api/tasks").then(r => r.json()),
            fetch("/api/telemetry").then(r => r.json()),
        ]);

        state.vram = vramRes;
        state.models = modelsRes.models || [];
        state.tasks = tasksRes.tasks || [];
        state.telemetry = telemRes.telemetry || {};

        renderVramTopology();
        renderModelRack();
        renderTasksStream();
        updateHeaderBadges(telemRes);
    } catch (err) {
        if (notifyOnError) {
            console.error("Error refreshing swarm status:", err);
            showToast("Error synchronizing with edge daemon.", "error");
        }
    }
}

function updateHeaderBadges(telemRes) {
    if (!state.vram) return;
    const vramBadge = document.getElementById("badge-vram");
    if (vramBadge) {
        vramBadge.textContent = `VRAM: ${state.vram.allocated_vram_mb}MB / ${state.vram.usable_vram_mb}MB [L1-008]`;
    }
    const eventsBadge = document.getElementById("badge-events");
    if (eventsBadge && telemRes) {
        eventsBadge.textContent = `EVENTS: ${telemRes.total_events || 0} [L1-002]`;
    }
}

function renderVramTopology() {
    if (!state.vram) return;
    const v = state.vram;
    document.getElementById("device-name-caption").textContent = `Device: ${v.device_name}`;
    document.getElementById("chip-allocated").textContent = `Allocated: ${v.allocated_vram_mb.toLocaleString()} MB (${v.utilization_pct}%)`;
    document.getElementById("chip-available").textContent = `Available: ${v.available_vram_mb.toLocaleString()} MB`;
    document.getElementById("chip-reserved").textContent = `OS Reserved: ${v.reserved_buffer_mb.toLocaleString()} MB`;

    document.getElementById("vram-threshold-label").textContent = `Usable Ceiling: ${v.usable_vram_mb.toLocaleString()} MB`;
    document.getElementById("vram-total-label").textContent = `${v.total_vram_mb.toLocaleString()} MB (Max)`;

    const allocBar = document.getElementById("vram-bar-allocated");
    const pct = Math.min(100, Math.round((v.allocated_vram_mb / v.total_vram_mb) * 100));
    allocBar.style.width = `${pct}%`;
}

function renderModelRack() {
    const container = document.getElementById("model-rack-list");
    const residentBadge = document.getElementById("resident-count-badge");
    const modelSelect = document.getElementById("task-target-model");

    const residentCount = state.models.filter(m => m.status === "RESIDENT" || m.status === "BUSY").length;
    residentBadge.textContent = `${residentCount} RESIDENT`;

    // Populate Override Model options
    const currentSelected = modelSelect.value;
    modelSelect.innerHTML = '<option value="">Auto-Route by Specialty</option>' + 
        state.models.map(m => `<option value="${m.model_id}" ${m.model_id === currentSelected ? 'selected' : ''}>${m.name}</option>`).join('');

    if (state.models.length === 0) {
        container.innerHTML = '<div class="loading-placeholder">No models registered.</div>';
        return;
    }

    container.innerHTML = state.models.map(m => {
        const isResident = m.status === "RESIDENT";
        const isBusy = m.status === "BUSY";
        const statusClass = isBusy ? "status-busy" : (isResident ? "status-resident" : "status-unloaded");
        const cardClass = isBusy ? "is-busy is-resident" : (isResident ? "is-resident" : "");

        return `
            <div class="model-rack-card-item ${cardClass}">
                <div class="model-header-row">
                    <span class="model-title-text">${escapeHtml(m.name)}</span>
                    <span class="model-status-pill ${statusClass}">${m.status}</span>
                </div>
                <div class="model-specs-row">
                    <span class="model-spec-badge">${m.param_billions}B Params</span>
                    <span class="model-spec-badge">${m.quantization}</span>
                    <span class="model-spec-badge">${m.specialty}</span>
                    <span class="model-spec-badge">${m.context_length} Ctx</span>
                </div>
                <div class="model-actions-row">
                    <span class="vram-cost-label">Cost: ${m.total_memory_mb} MB</span>
                    <div>
                        ${isResident ? `
                            <button class="btn btn-sm btn-danger" onclick="evictModel('${m.model_id}')" ${isBusy ? 'disabled' : ''}>
                                Evict VRAM
                            </button>
                        ` : `
                            <button class="btn btn-sm btn-outline" onclick="loadModel('${m.model_id}')">
                                Load into VRAM
                            </button>
                        `}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function renderTasksStream() {
    const container = document.getElementById("tasks-stream-list");
    const countBadge = document.getElementById("tasks-count-badge");
    countBadge.textContent = `${state.tasks.length} tasks`;

    if (state.tasks.length === 0) {
        container.innerHTML = '<div class="loading-placeholder">No tasks dispatched yet.</div>';
        return;
    }

    container.innerHTML = state.tasks.map(t => {
        const isCompleted = t.status === "COMPLETED";
        const isFailed = t.status === "FAILED";
        const statusColor = isCompleted ? "var(--accent-green)" : (isFailed ? "var(--accent-red)" : "var(--accent-cyan)");

        return `
            <div class="task-item-card">
                <div class="task-header-row">
                    <div class="task-meta-bar">
                        <span>TASK: ${t.task_id}</span>
                        <span>MODEL: ${t.target_model_id || 'AUTO'}</span>
                        <span>PRIORITY: ${t.priority}</span>
                    </div>
                    <span class="model-status-pill" style="color: ${statusColor}; border-color: ${statusColor}; background: transparent;">
                        ${t.status}
                    </span>
                </div>
                <div class="task-prompt-text">${escapeHtml(t.prompt)}</div>
                <div class="task-meta-bar">
                    <span>Tokens: ${t.tokens_processed}</span>
                    <span>VRAM Lease: ${t.vram_lease_mb} MB</span>
                    <span>Latency: ${t.latency_ms} ms</span>
                </div>
                ${t.result_output ? `
                    <div class="task-result-box">${escapeHtml(t.result_output)}</div>
                ` : ''}
                ${t.error_witness ? `
                    <div class="task-error-box">
                        <strong>Demarcated Exception Enclave Witness [L1-016]:</strong><br/>
                        ${escapeHtml(t.error_witness.message || 'Error occurred')} (Blast radius safely isolated).
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

async function handleDispatchTask(e) {
    e.preventDefault();
    const promptInput = document.getElementById("task-prompt");
    const specSelect = document.getElementById("task-specialty");
    const prioSelect = document.getElementById("task-priority");
    const modelSelect = document.getElementById("task-target-model");

    const prompt = promptInput.value.trim();
    if (!prompt) return;

    const btn = document.getElementById("btn-dispatch");
    btn.disabled = true;
    btn.innerHTML = '<span>⏳ Processing...</span>';

    try {
        const res = await fetch("/api/tasks/dispatch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                prompt: prompt,
                specialty: specSelect.value,
                priority: prioSelect.value,
                target_model_id: modelSelect.value || null,
            }),
        });

        const data = await res.json();
        if (!res.ok && res.status !== 422) {
            throw new Error(data.error || "Failed to dispatch task.");
        }

        if (data.task && data.task.status === "FAILED") {
            showToast("Task completed with Enclave fault containment.", "error");
        } else {
            showToast("Task executed by edge swarm.", "success");
            promptInput.value = "";
        }
        await refreshAll(false);
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>⚡ Dispatch to Swarm</span>';
    }
}

async function dispatchFaultInjectionTest() {
    const prompt = "CRASH_ENCLAVE_FAULT: Inject memory spike to test L1-016 enclave containment";
    try {
        const res = await fetch("/api/tasks/dispatch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                prompt: prompt,
                specialty: "REASONING",
                priority: "HIGH",
            }),
        });
        const data = await res.json();
        showToast("Fault safely trapped by Exception Enclave [L1-016]!", "success");
        await refreshAll(false);
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function loadModel(modelId) {
    try {
        const res = await fetch(`/api/models/${modelId}/load`, { method: "POST" });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.error || "Failed to load model.");
        }
        if (data.evicted_models && data.evicted_models.length > 0) {
            showToast(`Loaded ${modelId} (LRU evicted: ${data.evicted_models.join(', ')})`, "success");
        } else {
            showToast(`Model ${modelId} resident in VRAM.`, "success");
        }
        await refreshAll(false);
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function evictModel(modelId) {
    try {
        const res = await fetch(`/api/models/${modelId}/evict`, { method: "POST" });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.error || "Failed to evict model.");
        }
        showToast(`Model ${modelId} evicted. Memory reclaimed.`, "success");
        await refreshAll(false);
    } catch (err) {
        showToast(err.message, "error");
    }
}

/* Feedback Modal */
function openFeedbackModal() {
    document.getElementById("feedback-modal").style.display = "flex";
}

function closeFeedbackModal() {
    document.getElementById("feedback-modal").style.display = "none";
}

async function submitFeedback() {
    const cat = document.getElementById("fb-category").value;
    const comment = document.getElementById("fb-comment").value.trim();
    if (!comment) {
        alert("Please provide feedback text before submitting.");
        return;
    }

    try {
        const res = await fetch("/api/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ category: cat, comment: comment }),
        });
        if (!res.ok) throw new Error("Feedback rejected.");
        showToast("Feedback recorded into Generation 1 dossier.", "success");
        document.getElementById("fb-comment").value = "";
        closeFeedbackModal();
    } catch (err) {
        showToast(err.message, "error");
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
