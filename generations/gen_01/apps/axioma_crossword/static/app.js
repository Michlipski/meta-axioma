// Axioma Crossword Client Application Engine
// Employs Client-Side Optimistic Execution, Functorial Reversibility (L1-002),
// and Decoupled Asynchronous Synthesis Polling (L1-015_1).

let currentPuzzle = null;
let currentSession = {
  session_id: 'session_' + Math.random().toString(36).substring(2, 9),
  cells_entered: {},
  version: 1
};

let activeCell = { r: 0, c: 0 };
let activeDirection = 'ACROSS'; // 'ACROSS' or 'DOWN'
let activeSlot = null;

const undoStack = [];
const redoStack = [];

let activeSynthesisJobId = null;
let synthesisPollTimer = null;

// --- Initialization ---
document.addEventListener('DOMContentLoaded', async () => {
  await fetchPuzzleList();
  await loadPuzzle('puzzle_quick_01');
  window.addEventListener('keydown', handlePhysicalKey);
});

// --- API Calls ---
async function fetchPuzzleList() {
  try {
    const res = await fetch('/api/puzzles');
    if (!res.ok) return;
    const data = await res.json();
    const select = document.getElementById('select-puzzle');
    select.innerHTML = '';
    (data.puzzles || []).forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.grid_id;
      opt.textContent = `${p.title} (${p.size})`;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error('Failed to fetch puzzles:', err);
  }
}

async function loadPuzzle(puzzleId) {
  try {
    const res = await fetch(`/api/puzzles/${puzzleId}`);
    if (!res.ok) return;
    currentPuzzle = await res.json();

    // Reset local solver session
    currentSession.cells_entered = {};
    currentSession.version = 1;
    undoStack.length = 0;
    redoStack.length = 0;
    updateUndoCount();

    // Pick first available slot as active
    if (currentPuzzle.slots && currentPuzzle.slots.length > 0) {
      const s0 = currentPuzzle.slots[0];
      activeCell = { r: s0.row, c: s0.col };
      activeDirection = s0.direction;
      activeSlot = s0;
    }

    renderGrid();
    renderCluesList();
    updateActiveClueDisplay();
    renderTelemetry();
  } catch (err) {
    console.error('Failed to load puzzle:', err);
  }
}

function changePuzzle(puzzleId) {
  loadPuzzle(puzzleId);
}

// --- Grid Matrix Rendering ---
function renderGrid() {
  if (!currentPuzzle) return;
  const container = document.getElementById('grid-container');
  container.innerHTML = '';

  const table = document.createElement('table');
  table.className = 'grid-table';

  const rows = currentPuzzle.size_rows;
  const cols = currentPuzzle.size_cols;

  // Build slot number lookup: "r,c" -> number
  const numberLookup = {};
  (currentPuzzle.slots || []).forEach(s => {
    numberLookup[`${s.row},${s.col}`] = s.number;
  });

  // Build active word coordinates set
  const activeWordCoords = getActiveWordCoords();

  for (let r = 0; r < rows; r++) {
    const tr = document.createElement('tr');
    for (let c = 0; c < cols; c++) {
      const td = document.createElement('td');
      td.className = 'grid-cell';
      td.id = `cell-${r}-${c}`;

      const isBlack = currentPuzzle.cells[r][c] === '#';
      if (isBlack) {
        td.classList.add('black-cell');
      } else {
        // Number badge
        const num = numberLookup[`${r},${c}`];
        if (num) {
          const numSpan = document.createElement('span');
          numSpan.className = 'cell-number';
          numSpan.textContent = num;
          td.appendChild(numSpan);
        }

        // Letter span
        const letterSpan = document.createElement('span');
        letterSpan.className = 'cell-letter';
        letterSpan.id = `letter-${r}-${c}`;
        const entered = currentSession.cells_entered[`${r},${c}`] || '';
        letterSpan.textContent = entered;
        td.appendChild(letterSpan);

        // Highlight active cell & word
        if (activeCell.r === r && activeCell.c === c) {
          td.classList.add('active-cell');
        } else if (activeWordCoords.has(`${r},${c}`)) {
          td.classList.add('word-highlight');
        }

        td.addEventListener('click', () => handleCellClick(r, c));
      }

      tr.appendChild(td);
    }
    table.appendChild(tr);
  }

  container.appendChild(table);
}

function getActiveWordCoords() {
  const coords = new Set();
  if (!activeSlot) return coords;

  for (let i = 0; i < activeSlot.length; i++) {
    if (activeSlot.direction === 'ACROSS') {
      coords.add(`${activeSlot.row},${activeSlot.col + i}`);
    } else {
      coords.add(`${activeSlot.row + i},${activeSlot.col}`);
    }
  }
  return coords;
}

function handleCellClick(r, c) {
  if (currentPuzzle.cells[r][c] === '#') return;

  if (activeCell.r === r && activeCell.c === c) {
    // Toggle direction if clicked same cell
    switchClueDirection();
  } else {
    activeCell = { r, c };
    findAndSetActiveSlot();
  }
  renderGrid();
  updateActiveClueDisplay();
}

function switchClueDirection() {
  activeDirection = activeDirection === 'ACROSS' ? 'DOWN' : 'ACROSS';
  findAndSetActiveSlot();
  renderGrid();
  updateActiveClueDisplay();
}

function findAndSetActiveSlot() {
  if (!currentPuzzle) return;
  // Look for a slot matching current activeCell and activeDirection
  let found = currentPuzzle.slots.find(s => {
    if (s.direction !== activeDirection) return false;
    if (s.direction === 'ACROSS') {
      return s.row === activeCell.r && activeCell.c >= s.col && activeCell.c < s.col + s.length;
    } else {
      return s.col === activeCell.c && activeCell.r >= s.row && activeCell.r < s.row + s.length;
    }
  });

  // If not found in current direction, check other direction
  if (!found) {
    const otherDir = activeDirection === 'ACROSS' ? 'DOWN' : 'ACROSS';
    found = currentPuzzle.slots.find(s => {
      if (s.direction !== otherDir) return false;
      if (s.direction === 'ACROSS') {
        return s.row === activeCell.r && activeCell.c >= s.col && activeCell.c < s.col + s.length;
      } else {
        return s.col === activeCell.c && activeCell.r >= s.row && activeCell.r < s.row + s.length;
      }
    });
    if (found) {
      activeDirection = otherDir;
    }
  }

  activeSlot = found || null;
}

// --- Clue List & Dissector Rendering ---
function renderCluesList() {
  if (!currentPuzzle) return;

  const acrossContainer = document.getElementById('list-across-clues');
  const downContainer = document.getElementById('list-down-clues');
  acrossContainer.innerHTML = '';
  downContainer.innerHTML = '';

  (currentPuzzle.clues || []).forEach(clue => {
    const div = document.createElement('div');
    div.className = 'clue-item';
    div.id = `clue-item-${clue.clue_id}`;
    div.innerHTML = `<strong>${clue.number}.</strong> ${clue.surface_text}`;

    if (activeSlot && activeSlot.slot_id === clue.slot_id) {
      div.classList.add('active-clue-item');
    }

    div.addEventListener('click', () => {
      const slot = currentPuzzle.slots.find(s => s.slot_id === clue.slot_id);
      if (slot) {
        activeCell = { r: slot.row, c: slot.col };
        activeDirection = slot.direction;
        activeSlot = slot;
        renderGrid();
        updateActiveClueDisplay();
      }
    });

    if (clue.direction === 'ACROSS') {
      acrossContainer.appendChild(div);
    } else {
      downContainer.appendChild(div);
    }
  });
}

function updateActiveClueDisplay() {
  if (!currentPuzzle || !activeSlot) return;

  const clue = currentPuzzle.clues.find(c => c.slot_id === activeSlot.slot_id);
  const badge = document.getElementById('active-clue-badge');
  const text = document.getElementById('active-clue-text');

  if (clue) {
    badge.textContent = `${clue.number} ${clue.direction === 'ACROSS' ? 'Across' : 'Down'}`;
    text.textContent = clue.surface_text;
    renderDissector(clue);
  } else {
    badge.textContent = `${activeSlot.direction}`;
    text.textContent = 'Select an intersecting word slot';
  }

  // Update active clue highlight in clue list
  document.querySelectorAll('.clue-item').forEach(el => el.classList.remove('active-clue-item'));
  if (clue) {
    const el = document.getElementById(`clue-item-${clue.clue_id}`);
    if (el) el.classList.add('active-clue-item');
  }
}

function renderDissector(clue) {
  if (!clue) return;
  document.getElementById('dissector-clue-label').textContent = `${clue.number} ${clue.direction}`;
  document.getElementById('dissector-type-badge').textContent = clue.clue_type;
  document.getElementById('dissector-surface').textContent = `"${clue.surface_text}"`;
  document.getElementById('dissector-def').textContent = clue.definition || 'target concept';
  document.getElementById('dissector-ind').textContent = clue.indicator ? `${clue.indicator} (${clue.clue_type} Indicator)` : 'None';
  document.getElementById('dissector-fodder').textContent = clue.fodder || clue.answer;
  document.getElementById('dissector-explanation').textContent = clue.explanation || 'Cryptic derivation complete.';
}

function showActiveClueDissection() {
  switchStudioTab('dissector');
}

function switchStudioTab(tab) {
  document.getElementById('tab-clues').classList.add('hidden');
  document.getElementById('tab-dissector').classList.add('hidden');
  document.getElementById('tab-studio').classList.add('hidden');

  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active-tab'));

  if (tab === 'clues') {
    document.getElementById('tab-clues').classList.remove('hidden');
    document.getElementById('tab-btn-clues').classList.add('active-tab');
  } else if (tab === 'dissector') {
    document.getElementById('tab-dissector').classList.remove('hidden');
    document.getElementById('tab-btn-dissector').classList.add('active-tab');
  } else if (tab === 'studio') {
    document.getElementById('tab-studio').classList.remove('hidden');
    document.getElementById('tab-btn-studio').classList.add('active-tab');
  }
}

// --- Keystroke & Input Handling ---
function handlePhysicalKey(e) {
  // Ignore if inside an input or textarea
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

  if (e.key === 'ArrowRight') {
    moveCursor(0, 1);
    e.preventDefault();
  } else if (e.key === 'ArrowLeft') {
    moveCursor(0, -1);
    e.preventDefault();
  } else if (e.key === 'ArrowDown') {
    moveCursor(1, 0);
    e.preventDefault();
  } else if (e.key === 'ArrowUp') {
    moveCursor(-1, 0);
    e.preventDefault();
  } else if (e.key === ' ' || e.key === 'Tab') {
    switchClueDirection();
    e.preventDefault();
  } else if (e.key === 'Backspace') {
    handleBackspace();
    e.preventDefault();
  } else if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'z') {
    if (e.shiftKey) redoStep();
    else undoStep();
    e.preventDefault();
  } else if (/^[a-zA-Z]$/.test(e.key)) {
    handleLetterInput(e.key.toUpperCase());
    e.preventDefault();
  }
}

function handleSoftKey(char) {
  handleLetterInput(char.toUpperCase());
}

function handleSoftBackspace() {
  handleBackspace();
}

function handleLetterInput(char) {
  const r = activeCell.r;
  const c = activeCell.c;
  if (!currentPuzzle || currentPuzzle.cells[r][c] === '#') return;

  const prevChar = currentSession.cells_entered[`${r},${c}`] || '';

  // Record mutation for functorial reversibility (L1-002)
  undoStack.push({ r, c, char, prevChar });
  redoStack.length = 0;
  updateUndoCount();

  // Apply optimistically
  currentSession.cells_entered[`${r},${c}`] = char;
  const el = document.getElementById(`letter-${r}-${c}`);
  if (el) el.textContent = char;

  // Sync delta asynchronously
  syncDelta(r, c, char);

  // Advance cursor forward
  advanceCursorForward();
  renderTelemetry();
}

function handleBackspace() {
  const r = activeCell.r;
  const c = activeCell.c;
  const prevChar = currentSession.cells_entered[`${r},${c}`] || '';

  if (prevChar) {
    undoStack.push({ r, c, char: '', prevChar });
    redoStack.length = 0;
    updateUndoCount();

    delete currentSession.cells_entered[`${r},${c}`];
    const el = document.getElementById(`letter-${r}-${c}`);
    if (el) el.textContent = '';
    syncDelta(r, c, '');
  } else {
    // Move backward and clear
    stepCursorBackward();
    const nr = activeCell.r;
    const nc = activeCell.c;
    const nPrev = currentSession.cells_entered[`${nr},${nc}`] || '';
    if (nPrev) {
      undoStack.push({ r: nr, c: nc, char: '', prevChar: nPrev });
      redoStack.length = 0;
      updateUndoCount();

      delete currentSession.cells_entered[`${nr},${nc}`];
      const el = document.getElementById(`letter-${nr}-${nc}`);
      if (el) el.textContent = '';
      syncDelta(nr, nc, '');
    }
  }
  renderGrid();
  renderTelemetry();
}

function advanceCursorForward() {
  if (activeDirection === 'ACROSS') {
    if (activeCell.c + 1 < currentPuzzle.size_cols && currentPuzzle.cells[activeCell.r][activeCell.c + 1] !== '#') {
      activeCell.c += 1;
    }
  } else {
    if (activeCell.r + 1 < currentPuzzle.size_rows && currentPuzzle.cells[activeCell.r + 1][activeCell.c] !== '#') {
      activeCell.r += 1;
    }
  }
  renderGrid();
}

function stepCursorBackward() {
  if (activeDirection === 'ACROSS') {
    if (activeCell.c - 1 >= 0 && currentPuzzle.cells[activeCell.r][activeCell.c - 1] !== '#') {
      activeCell.c -= 1;
    }
  } else {
    if (activeCell.r - 1 >= 0 && currentPuzzle.cells[activeCell.r - 1][activeCell.c] !== '#') {
      activeCell.r -= 1;
    }
  }
}

function moveCursor(dr, dc) {
  const nr = activeCell.r + dr;
  const nc = activeCell.c + dc;
  if (nr >= 0 && nr < currentPuzzle.size_rows && nc >= 0 && nc < currentPuzzle.size_cols) {
    if (currentPuzzle.cells[nr][nc] !== '#') {
      activeCell = { r: nr, c: nc };
      findAndSetActiveSlot();
      renderGrid();
      updateActiveClueDisplay();
    }
  }
}

// --- Functorial Reversibility (L1-002) ---
function undoStep() {
  if (undoStack.length === 0) return;
  const step = undoStack.pop();
  redoStack.push(step);
  updateUndoCount();

  if (step.prevChar) {
    currentSession.cells_entered[`${step.r},${step.c}`] = step.prevChar;
  } else {
    delete currentSession.cells_entered[`${step.r},${step.c}`];
  }
  activeCell = { r: step.r, c: step.c };
  renderGrid();
  syncDelta(step.r, step.c, step.prevChar);
  renderTelemetry();
}

function redoStep() {
  if (redoStack.length === 0) return;
  const step = redoStack.pop();
  undoStack.push(step);
  updateUndoCount();

  if (step.char) {
    currentSession.cells_entered[`${step.r},${step.c}`] = step.char;
  } else {
    delete currentSession.cells_entered[`${step.r},${step.c}`];
  }
  activeCell = { r: step.r, c: step.c };
  renderGrid();
  syncDelta(step.r, step.c, step.char);
  renderTelemetry();
}

function updateUndoCount() {
  document.getElementById('undo-count').textContent = undoStack.length;
}

// --- Delta Sync API ---
async function syncDelta(row, col, char) {
  try {
    const res = await fetch(`/api/sessions/${currentSession.session_id}/delta`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        row,
        col,
        char,
        expected_version: currentSession.version
      })
    });
    const data = await res.json();
    if (data.session) {
      currentSession.version = data.session.version;
      document.getElementById('stat-version').textContent = `v${currentSession.version} (Synced)`;
    }
  } catch (err) {
    console.warn('Delta sync delayed (offline resilience active):', err);
  }
}

// --- Solver Hints & Checks ---
function checkActiveWord() {
  if (!activeSlot) return;
  let allCorrect = true;

  for (let i = 0; i < activeSlot.length; i++) {
    const r = activeSlot.direction === 'ACROSS' ? activeSlot.row : activeSlot.row + i;
    const c = activeSlot.direction === 'ACROSS' ? activeSlot.col + i : activeSlot.col;
    const entered = (currentSession.cells_entered[`${r},${c}`] || '').toUpperCase();
    const target = activeSlot.answer[i];

    const el = document.getElementById(`letter-${r}-${c}`);
    if (el) {
      if (entered && entered !== target) {
        el.classList.add('cell-error');
        setTimeout(() => el.classList.remove('cell-error'), 1200);
        allCorrect = false;
      } else if (entered === target) {
        el.classList.add('cell-correct');
        setTimeout(() => el.classList.remove('cell-correct'), 1200);
      }
    }
  }
}

function revealActiveLetter() {
  if (!activeSlot) return;
  const idx = activeSlot.direction === 'ACROSS' ? activeCell.c - activeSlot.col : activeCell.r - activeSlot.row;
  if (idx >= 0 && idx < activeSlot.length) {
    const targetChar = activeSlot.answer[idx];
    handleLetterInput(targetChar);
  }
}

function revealActiveWord() {
  if (!activeSlot) return;
  for (let i = 0; i < activeSlot.length; i++) {
    const r = activeSlot.direction === 'ACROSS' ? activeSlot.row : activeSlot.row + i;
    const c = activeSlot.direction === 'ACROSS' ? activeSlot.col + i : activeSlot.col;
    activeCell = { r, c };
    handleLetterInput(activeSlot.answer[i]);
  }
}

function clearCurrentPuzzle() {
  currentSession.cells_entered = {};
  undoStack.length = 0;
  redoStack.length = 0;
  updateUndoCount();
  renderGrid();
  renderTelemetry();
}

function renderTelemetry() {
  if (!currentPuzzle) return;
  let filledCount = 0;
  let totalCount = 0;

  for (let r = 0; r < currentPuzzle.size_rows; r++) {
    for (let c = 0; c < currentPuzzle.size_cols; c++) {
      if (currentPuzzle.cells[r][c] !== '#') {
        totalCount++;
        if (currentSession.cells_entered[`${r},${c}`]) filledCount++;
      }
    }
  }

  const pct = totalCount > 0 ? Math.round((filledCount / totalCount) * 100) : 0;
  document.getElementById('stat-progress').textContent = `${filledCount} / ${totalCount} cells (${pct}%)`;
}

// --- Asynchronous CSP Synthesis Worker (L1-015_1) ---
async function triggerSynthesisJob() {
  const size = parseInt(document.getElementById('synth-size').value, 10);
  logSynth(`[DISPATCH] Requesting ${size}x${size} CSP synthesis job from worker pool...`);

  try {
    const res = await fetch('/api/jobs/synthesize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ grid_size: size })
    });
    const data = await res.json();
    if (res.status === 202 && data.job) {
      activeSynthesisJobId = data.job.job_id;
      document.getElementById('job-id-label').textContent = activeSynthesisJobId;
      document.getElementById('job-status-label').textContent = 'Status: RUNNING (Worker Thread)';
      logSynth(`[QUEUED] Job ID ${activeSynthesisJobId} accepted. Polling worker telemetry...`);
      startJobPolling();
    }
  } catch (err) {
    logSynth(`[ERROR] Job dispatch failed: ${err.message}`);
  }
}

function startJobPolling() {
  if (synthesisPollTimer) clearInterval(synthesisPollTimer);
  synthesisPollTimer = setInterval(pollActiveJob, 400);
}

async function pollActiveJob() {
  if (!activeSynthesisJobId) return;

  try {
    const res = await fetch(`/api/jobs/${activeSynthesisJobId}`);
    if (!res.ok) return;
    const job = await res.json();

    document.getElementById('job-backtracks').textContent = job.backtracks_count || 0;
    document.getElementById('job-pruned').textContent = job.pruned_candidates_count || 0;
    document.getElementById('job-joules').textContent = (job.joules_dissipated || 0).toExponential(2) + ' J';
    document.getElementById('stat-joules').textContent = (job.joules_dissipated || 0).toExponential(2) + ' J';

    const pct = Math.round(job.progress_pct || 0);
    document.getElementById('job-progress-pct').textContent = `${pct}%`;
    document.getElementById('job-progress-bar').style.width = `${pct}%`;

    if (job.status === 'COMPLETED') {
      clearInterval(synthesisPollTimer);
      document.getElementById('job-status-label').textContent = 'Status: COMPLETED';
      document.getElementById('job-status-label').className = 'font-bold text-emerald-400';
      logSynth(`[SUCCESS] Grid synthesized with ${job.backtracks_count} backtracks! Joules: ${job.joules_dissipated.toExponential(2)} J`);

      // Refresh puzzle list and switch to it
      await fetchPuzzleList();
      if (job.result_grid_id) {
        document.getElementById('select-puzzle').value = job.result_grid_id;
        await loadPuzzle(job.result_grid_id);
      }
    } else if (job.status === 'TIMEOUT' || job.status === 'FAILED') {
      clearInterval(synthesisPollTimer);
      document.getElementById('job-status-label').textContent = `Status: ${job.status}`;
      document.getElementById('job-status-label').className = 'font-bold text-red-400';
      logSynth(`[TERMINATED] Worker error: ${job.error}`);
    }
  } catch (err) {
    console.error('Polling error:', err);
  }
}

function logSynth(msg) {
  const box = document.getElementById('synth-log');
  const d = document.createElement('div');
  d.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
  box.appendChild(d);
  box.scrollTop = box.scrollHeight;
}

// --- Mobile Keypad Toggle ---
function toggleMobileKeypadView() {
  const el = document.getElementById('mobile-keypad-container');
  el.classList.toggle('hidden');
}

// --- Feedback Modal ---
function openFeedbackModal() {
  document.getElementById('modal-feedback').classList.remove('hidden');
}
function closeFeedbackModal() {
  document.getElementById('modal-feedback').classList.add('hidden');
}
async function submitFeedback() {
  const cat = document.getElementById('fb-cat').value;
  const comment = document.getElementById('fb-text').value.trim();
  if (!comment) return;

  try {
    const res = await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category: cat, comment })
    });
    const data = await res.json();
    closeFeedbackModal();
    document.getElementById('fb-text').value = '';
    alert('Thank you! Feedback recorded for Generation G2 learning stream.');
  } catch (err) {
    console.error(err);
  }
}
