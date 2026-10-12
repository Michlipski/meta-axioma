// Reactive Client Logic for Axioma Production App (Target P1)
let appState = { tasks: [] };
let draggingTaskId = null;

async function fetchState() {
  try {
    const res = await fetch('/api/state');
    if (!res.ok) throw new Error('Failed to load state');
    const data = await res.json();
    appState = data.state;
    updateTelemetry(data);
    renderBoard();
  } catch (err) {
    showToast('Failed to connect to backend: ' + err.message, true);
  }
}

function updateTelemetry(data) {
  const thermo = data.thermodynamics || {};
  const bitsElem = document.getElementById('stat-erased-bits');
  const joulesElem = document.getElementById('stat-joules');
  const undoCount = document.getElementById('undo-count');
  const redoCount = document.getElementById('redo-count');

  if (bitsElem) bitsElem.innerText = (thermo.total_erased_bits || 0).toLocaleString() + ' bits';
  if (joulesElem) joulesElem.innerText = (thermo.total_joules || 0).toExponential(2) + ' J';
  if (undoCount) undoCount.innerText = data.history_depth || 0;
  if (redoCount) redoCount.innerText = data.future_depth || 0;
}

function renderBoard() {
  const columns = ['backlog', 'in_progress', 'review', 'done'];
  const tasks = appState.tasks || [];

  columns.forEach(col => {
    const container = document.getElementById('col-' + col);
    const countBadge = document.getElementById('count-' + col);
    if (!container) return;

    const colTasks = tasks.filter(t => t.status === col);
    if (countBadge) countBadge.innerText = colTasks.length;

    container.innerHTML = '';
    colTasks.forEach(task => {
      const card = document.createElement('div');
      card.className = 'task-card';
      card.draggable = true;
      card.dataset.id = task.id;

      card.ondragstart = (e) => {
        draggingTaskId = task.id;
        card.style.opacity = '0.5';
      };
      card.ondragend = (e) => {
        card.style.opacity = '1';
        draggingTaskId = null;
      };

      const priority = task.priority || 'medium';
      card.innerHTML = `
        <div class="card-header">
          <span class="card-title">${escapeHtml(task.title)}</span>
          <span class="priority-tag ${priority}">${priority}</span>
        </div>
        ${task.description ? `<p class="card-desc">${escapeHtml(task.description)}</p>` : ''}
        <div class="card-footer">
          <span>#${escapeHtml(task.id.slice(-6))}</span>
          <div class="card-actions">
            <button class="btn-icon" onclick="deleteTask('${task.id}')" title="Delete Task">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
          </div>
        </div>
      `;
      container.appendChild(card);
    });
  });
}

function allowDrop(e) {
  e.preventDefault();
}

async function handleDrop(e, targetStatus) {
  e.preventDefault();
  if (!draggingTaskId) return;

  try {
    const res = await fetch('/api/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'MOVE_ITEM',
        params: { type: 'tasks', id: draggingTaskId, status: targetStatus },
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Move failed');
    appState = data.state;
    fetchState();
    showToast(`Task moved to ${targetStatus}`);
  } catch (err) {
    showToast(err.message, true);
  }
}

async function handleCreateTask(e) {
  e.preventDefault();
  const title = document.getElementById('task-title').value.trim();
  const description = document.getElementById('task-desc').value.trim();
  const status = document.getElementById('task-status').value;
  const priority = document.getElementById('task-priority').value;

  if (!title) return;

  try {
    const res = await fetch('/api/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'CREATE_ITEM',
        params: {
          type: 'tasks',
          item: { title, description, status, priority },
        },
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to create task');
    closeModal();
    document.getElementById('form-new-task').reset();
    appState = data.state;
    fetchState();
    showToast('Task created successfully');
  } catch (err) {
    showToast(err.message, true);
  }
}

async function deleteTask(id) {
  if (!confirm('Are you sure you want to delete this task? (Lossy bit erasure will be audited against Landauer limit)')) {
    return;
  }
  try {
    const res = await fetch('/api/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'DELETE_ITEM',
        params: { type: 'tasks', id },
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Delete failed');
    appState = data.state;
    fetchState();
    showToast('Task deleted (Landauer dissipation recorded)');
  } catch (err) {
    showToast(err.message, true);
  }
}

async function triggerUndo() {
  try {
    const res = await fetch('/api/undo', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      appState = data.state;
      fetchState();
      showToast('Undone state transformation (Functorial Reversibility)');
    } else {
      showToast('Nothing to undo');
    }
  } catch (err) {
    showToast(err.message, true);
  }
}

async function triggerRedo() {
  try {
    const res = await fetch('/api/redo', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      appState = data.state;
      fetchState();
      showToast('Redone state transformation');
    } else {
      showToast('Nothing to redo');
    }
  } catch (err) {
    showToast(err.message, true);
  }
}

function openModal() {
  const modal = document.getElementById('modal-new-task');
  if (modal) modal.classList.remove('hidden');
}

function closeModal() {
  const modal = document.getElementById('modal-new-task');
  if (modal) modal.classList.add('hidden');
}

function showToast(msg, isError = false) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.innerText = msg;
  toast.style.borderColor = isError ? 'var(--accent-red)' : 'var(--border-focus)';
  toast.classList.remove('hidden');
  setTimeout(() => toast.classList.add('hidden'), 3500);
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[m]);
}

// Bind events
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('btn-undo')?.addEventListener('click', triggerUndo);
  document.getElementById('btn-redo')?.addEventListener('click', triggerRedo);
  document.getElementById('btn-new-task')?.addEventListener('click', openModal);

  // Keyboard shortcuts (Cmd+Z / Ctrl+Z for Undo)
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'z') {
      if (e.shiftKey) {
        triggerRedo();
      } else {
        triggerUndo();
      }
    }
  });

  fetchState();
});
