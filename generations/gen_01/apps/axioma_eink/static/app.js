/**
 * Axioma E-Ink Task Router Client Logic.
 * 
 * Manages reactive Daily Big 3-5 focus orchestration, event stream mutations,
 * undo/redo operations, and synchronizes the live electrophoretic hardware preview.
 */

let state = {
    focusTasks: [],
    backlogTasks: [],
    totalEvents: 0,
    canUndo: false,
};

document.addEventListener("DOMContentLoaded", () => {
    fetchTasks();
    setupKeyboardShortcuts();
});

function setupKeyboardShortcuts() {
    window.addEventListener("keydown", (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === "z") {
            e.preventDefault();
            handleUndo();
        }
    });
}

function showToast(message, type = "normal") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type === "success" ? "toast-success" : type === "error" ? "toast-error" : ""}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 3500);
}

async function fetchTasks() {
    try {
        const res = await fetch("/api/tasks");
        if (!res.ok) throw new Error("Failed to load tasks");
        const data = await res.json();
        
        state.focusTasks = data.focus_tasks || [];
        state.backlogTasks = data.backlog_tasks || [];
        state.totalEvents = data.total_events || 0;
        state.canUndo = data.can_undo || false;

        renderTasks();
        updateBadges();
    } catch (err) {
        console.error("Error fetching tasks:", err);
        showToast("Error synchronizing with task event stream.", "error");
    }
}

function updateBadges() {
    const eventBadge = document.getElementById("event-count-badge");
    if (eventBadge) {
        eventBadge.textContent = `EVENTS: ${state.totalEvents} [L1-002]`;
    }

    const focusCountNum = document.getElementById("focus-count-num");
    if (focusCountNum) {
        focusCountNum.textContent = state.focusTasks.length;
    }

    const backlogCountNum = document.getElementById("backlog-count-num");
    if (backlogCountNum) {
        backlogCountNum.textContent = `${state.backlogTasks.length} items`;
    }

    const undoBtn = document.getElementById("btn-undo");
    if (undoBtn) {
        undoBtn.disabled = !state.canUndo;
        undoBtn.style.opacity = state.canUndo ? "1" : "0.5";
    }
}

function renderTasks() {
    const focusContainer = document.getElementById("focus-task-list");
    const backlogContainer = document.getElementById("backlog-task-list");

    // 1. Render Focus Tasks
    if (state.focusTasks.length === 0) {
        focusContainer.innerHTML = `
            <div class="loading-placeholder">
                No active focus tasks. Capture 1 to 5 priorities above.
            </div>`;
    } else {
        focusContainer.innerHTML = state.focusTasks.map((t, idx) => `
            <div class="task-item-card ${t.status === 'DONE' ? 'is-done' : ''}" data-id="${t.task_id}">
                <div class="task-rank-pill">${idx + 1}</div>
                <button class="task-toggle-btn ${t.status === 'DONE' ? 'checked' : ''}" 
                        onclick="toggleTask('${t.task_id}')" 
                        title="Mark ${t.status === 'DONE' ? 'TODO' : 'DONE'}">
                    ${t.status === 'DONE' ? '✓' : ''}
                </button>
                <div class="task-body-wrapper">
                    <div class="task-title-text">${escapeHtml(t.title)}</div>
                    <div class="task-meta-row">
                        <span class="task-context-tag">${escapeHtml(t.tag)}</span>
                    </div>
                </div>
                <div class="task-item-actions">
                    <button class="icon-btn" onclick="moveTaskRank('${t.task_id}', -1)" title="Move Up" ${idx === 0 ? 'disabled style="opacity:0.3"' : ''}>▲</button>
                    <button class="icon-btn" onclick="moveTaskRank('${t.task_id}', 1)" title="Move Down" ${idx === state.focusTasks.length - 1 ? 'disabled style="opacity:0.3"' : ''}>▼</button>
                    <button class="icon-btn" onclick="setTaskFocus('${t.task_id}', false)" title="Move to Backlog">📥</button>
                    <button class="icon-btn danger" onclick="deleteTask('${t.task_id}')" title="Delete">✕</button>
                </div>
            </div>
        `).join("");
    }

    // 2. Render Backlog Tasks
    if (state.backlogTasks.length === 0) {
        backlogContainer.innerHTML = `
            <div class="loading-placeholder">
                Backlog is clear.
            </div>`;
    } else {
        backlogContainer.innerHTML = state.backlogTasks.map((t) => `
            <div class="task-item-card ${t.status === 'DONE' ? 'is-done' : ''}" data-id="${t.task_id}">
                <button class="task-toggle-btn ${t.status === 'DONE' ? 'checked' : ''}" 
                        onclick="toggleTask('${t.task_id}')" 
                        title="Mark ${t.status === 'DONE' ? 'TODO' : 'DONE'}">
                    ${t.status === 'DONE' ? '✓' : ''}
                </button>
                <div class="task-body-wrapper">
                    <div class="task-title-text">${escapeHtml(t.title)}</div>
                    <div class="task-meta-row">
                        <span class="task-context-tag">${escapeHtml(t.tag)}</span>
                    </div>
                </div>
                <div class="task-item-actions">
                    <button class="icon-btn" onclick="setTaskFocus('${t.task_id}', true)" title="Promote to Daily Big 3–5">⭐ Focus</button>
                    <button class="icon-btn danger" onclick="deleteTask('${t.task_id}')" title="Delete">✕</button>
                </div>
            </div>
        `).join("");
    }
}

async function handleCreateTask(e) {
    e.preventDefault();
    const titleInput = document.getElementById("task-title");
    const tagSelect = document.getElementById("task-tag");
    const prioritySelect = document.getElementById("task-priority");
    const isFocusCheck = document.getElementById("task-is-focus");

    const title = titleInput.value.trim();
    if (!title) return;

    try {
        const res = await fetch("/api/tasks", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                title: title,
                tag: tagSelect.value,
                priority: parseInt(prioritySelect.value, 10),
                is_focus: isFocusCheck.checked,
            }),
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.error || "Failed to commit task.");
        }

        titleInput.value = "";
        showToast("Task committed to event stream.", "success");
        await fetchTasks();
        reloadSimulatorFrame();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function toggleTask(taskId) {
    try {
        const res = await fetch(`/api/tasks/${taskId}/toggle`, { method: "POST" });
        if (!res.ok) throw new Error("Failed to toggle task.");
        await fetchTasks();
        reloadSimulatorFrame();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function setTaskFocus(taskId, isFocus) {
    try {
        const res = await fetch(`/api/tasks/${taskId}/focus`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ is_focus: isFocus }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Failed to update focus status.");
        showToast(isFocus ? "Promoted to Daily Big 3–5." : "Moved to backlog.");
        await fetchTasks();
        reloadSimulatorFrame();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function moveTaskRank(taskId, delta) {
    const ids = state.focusTasks.map(t => t.task_id);
    const currIdx = ids.indexOf(taskId);
    if (currIdx === -1) return;

    const newIdx = currIdx + delta;
    if (newIdx < 0 || newIdx >= ids.length) return;

    // Swap
    const temp = ids[currIdx];
    ids[currIdx] = ids[newIdx];
    ids[newIdx] = temp;

    try {
        const res = await fetch("/api/tasks/reorder", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_ids: ids }),
        });
        if (!res.ok) throw new Error("Failed to reorder priorities.");
        await fetchTasks();
        reloadSimulatorFrame();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function deleteTask(taskId) {
    try {
        const res = await fetch(`/api/tasks/${taskId}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Failed to delete task.");
        showToast("Task removed from active board.");
        await fetchTasks();
        reloadSimulatorFrame();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function handleUndo() {
    try {
        const res = await fetch("/api/undo", { method: "POST" });
        const data = await res.json();
        if (data.status === "undone") {
            showToast("Action reverted via compensatory event.", "success");
            await fetchTasks();
            reloadSimulatorFrame();
        } else {
            showToast(data.message || "Nothing to undo.");
        }
    } catch (err) {
        showToast("Error executing undo operation.", "error");
    }
}

function reloadSimulatorFrame() {
    const frame = document.getElementById("eink-frame");
    if (frame) {
        frame.src = `/display?_ts=${Date.now()}`;
    }
}

function triggerEinkRefreshFlash() {
    const overlay = document.getElementById("flash-overlay");
    if (!overlay) return;
    overlay.classList.remove("flashing");
    // Force reflow
    void overlay.offsetWidth;
    overlay.classList.add("flashing");
    setTimeout(() => {
        reloadSimulatorFrame();
    }, 250);
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
        alert("Please provide an observation or critique before submitting.");
        return;
    }

    try {
        const res = await fetch("/api/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ category: cat, comment: comment }),
        });
        if (!res.ok) throw new Error("Feedback submission rejected.");
        showToast("Feedback persisted into Generation 1 ledger.", "success");
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
