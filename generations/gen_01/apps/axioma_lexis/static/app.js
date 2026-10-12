// Axioma Lexis Client Logic for Android Mobile PWA (Target P1 Ergonomics)

let appState = { words: [], stats: {}, history_depth: 0 };
let reviewQueue = [];
let currentCardIndex = 0;
let isFlipped = false;
let currentLookupWord = null;
let currentFilter = 'all';
let searchTimeout = null;
let deferredPrompt = null;

// PWA Service Worker Registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {});
  });
}

// Android PWA Install Prompt Listener
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const installBtn = document.getElementById('btn-install');
  if (installBtn) installBtn.classList.remove('hidden');
});

document.getElementById('btn-install')?.addEventListener('click', async () => {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      showToast('Axioma Lexis installed to your Android Home Screen!');
    }
    deferredPrompt = null;
    document.getElementById('btn-install')?.classList.add('hidden');
  }
});

// 1. Fetch State & Initialize
async function fetchState(preserveView = true) {
  try {
    const res = await fetch('/api/state');
    if (!res.ok) throw new Error('Failed to load state');
    const data = await res.json();
    appState = data;
    updateStatsRibbon(data);
    updateUndoBadge(data.history_depth);
    buildReviewQueue();
    renderDeckList();
  } catch (err) {
    showToast('Offline / connecting to local backend...');
  }
}

function updateStatsRibbon(data) {
  const stats = data.stats || {};
  const thermo = data.thermodynamics || {};

  setText('stat-total-words', stats.total_count || 0);
  setText('stat-mastered-words', stats.mastered_count || 0);
  setText('stat-learning-words', stats.learning_count || 0);
  setText('stat-due-words', stats.due_count || 0);

  setText('count-all', stats.total_count || 0);
  setText('count-due', stats.due_count || 0);
  setText('count-learning', stats.learning_count || 0);
  setText('count-mastered', stats.mastered_count || 0);

  setText('stat-erased-bits', (thermo.total_erased_bits || 0).toLocaleString() + ' bits');
  setText('stat-joules', (thermo.total_joules || 0).toExponential(2) + ' J');

  const navBadge = document.getElementById('nav-due-badge');
  if (navBadge) {
    if (stats.due_count > 0) {
      navBadge.innerText = stats.due_count;
      navBadge.classList.remove('hidden');
    } else {
      navBadge.classList.add('hidden');
    }
  }
}

function updateUndoBadge(depth) {
  const badge = document.getElementById('badge-undo');
  if (badge) badge.innerText = depth || 0;
}

// 2. Review & Flashcards Queue Management
function buildReviewQueue() {
  const now = timeNow();
  const words = appState.words || [];
  // Filter cards due for review
  reviewQueue = words.filter(w => (w.next_review || 0) <= now);
  currentCardIndex = 0;
  isFlipped = false;
  renderCurrentCard();
}

function startOnDemandReview() {
  const words = appState.words || [];
  if (words.length === 0) {
    showToast('Your vocabulary deck is empty. Search words to add!');
    return;
  }
  reviewQueue = [...words];
  currentCardIndex = 0;
  isFlipped = false;
  renderCurrentCard();
  showToast('Starting On-Demand Review session!');
}

function renderCurrentCard() {
  const cardElem = document.getElementById('flashcard');
  const emptyState = document.getElementById('review-empty-state');
  const cardContainer = document.getElementById('flashcard-container');
  const srsControls = document.getElementById('srs-controls');
  const dueText = document.getElementById('session-due-text');

  if (cardElem) cardElem.classList.remove('flipped');
  isFlipped = false;

  if (!reviewQueue || reviewQueue.length === 0 || currentCardIndex >= reviewQueue.length) {
    // Session completed
    if (cardContainer) cardContainer.classList.add('hidden');
    if (srsControls) srsControls.classList.add('hidden');
    if (emptyState) emptyState.classList.remove('hidden');
    if (dueText) dueText.innerText = '0 words due for review';
    return;
  }

  const word = reviewQueue[currentCardIndex];
  if (cardContainer) cardContainer.classList.remove('hidden');
  if (emptyState) emptyState.classList.add('hidden');
  if (srsControls) srsControls.classList.add('hidden'); // hidden until flipped

  const remaining = reviewQueue.length - currentCardIndex;
  if (dueText) dueText.innerText = `${remaining} word${remaining > 1 ? 's' : ''} left in session`;

  // Front values
  setText('card-word', word.word);
  setText('card-pos', word.part_of_speech || 'noun');
  setText('card-phonetic', word.phonetic_us || word.phonetic_uk || '');

  // Back values
  setText('card-back-word', word.word);
  setText('card-back-pos', word.part_of_speech || 'noun');
  setText('card-back-level', `Rep ${word.repetition_level || 0} • ${word.status}`);
  setText('card-definition', word.definition || 'No definition available.');
  setText('card-example', word.example ? `"${word.example}"` : 'No example context.');

  const transWrap = document.getElementById('card-translation-box');
  if (transWrap) {
    if (word.translation_es) {
      transWrap.classList.remove('hidden');
      setText('card-translation', word.translation_es);
    } else {
      transWrap.classList.add('hidden');
    }
  }

  // Synonyms
  const synsWrap = document.getElementById('card-synonyms');
  if (synsWrap) {
    synsWrap.innerHTML = '';
    const syns = word.synonyms || [];
    if (syns.length > 0) {
      document.getElementById('card-synonyms-wrap')?.classList.remove('hidden');
      syns.forEach(s => {
        const chip = document.createElement('span');
        chip.className = 'chip';
        chip.innerText = s;
        synsWrap.appendChild(chip);
      });
    } else {
      document.getElementById('card-synonyms-wrap')?.classList.add('hidden');
    }
  }
}

function flipCard() {
  const cardElem = document.getElementById('flashcard');
  const srsControls = document.getElementById('srs-controls');
  if (!cardElem) return;

  isFlipped = !isFlipped;
  if (isFlipped) {
    cardElem.classList.add('flipped');
    if (srsControls) srsControls.classList.remove('hidden');
  } else {
    cardElem.classList.remove('flipped');
    if (srsControls) srsControls.classList.add('hidden');
  }
}

// 3. Submit Spaced Repetition Rating
async function submitRating(rating) {
  if (currentCardIndex >= reviewQueue.length) return;
  const word = reviewQueue[currentCardIndex];

  try {
    const res = await fetch('/api/deck/review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word_id: word.id, rating: rating }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to review');

    currentCardIndex++;
    showToast(`Rated ${rating} • Next review in ${data.word.interval_days}d`);
    renderCurrentCard();
    fetchState(false);
  } catch (err) {
    showToast('Review rating failed: ' + err.message);
  }
}

// 4. Native Speech Audio Pronunciation (US/UK)
function speakWord(accent = 'us') {
  if (!reviewQueue || currentCardIndex >= reviewQueue.length) return;
  const word = reviewQueue[currentCardIndex].word;
  speakHeadword(word, accent);
}

function speakLookupWord(accent = 'us') {
  if (!currentLookupWord) return;
  speakHeadword(currentLookupWord.word, accent);
}

function speakHeadword(text, accent = 'us') {
  if (!('speechSynthesis' in window)) {
    showToast('Speech synthesis not supported on this device.');
    return;
  }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = accent === 'uk' ? 'en-GB' : 'en-US';
  utterance.rate = 0.9;
  window.speechSynthesis.speak(utterance);
}

// 5. Dictionary Lookup
function handleDictSearchInput(e) {
  const query = e.target.value.trim();
  const clearBtn = document.getElementById('btn-clear-search');
  if (clearBtn) {
    if (query.length > 0) clearBtn.classList.remove('hidden');
    else clearBtn.classList.add('hidden');
  }

  clearTimeout(searchTimeout);
  if (!query) {
    document.getElementById('dict-result-wrap')?.classList.add('hidden');
    document.getElementById('dict-suggestions')?.classList.remove('hidden');
    return;
  }

  searchTimeout = setTimeout(() => {
    executeLookup(query);
  }, 300);
}

function clearSearch() {
  const input = document.getElementById('dict-search-input');
  if (input) input.value = '';
  document.getElementById('btn-clear-search')?.classList.add('hidden');
  document.getElementById('dict-result-wrap')?.classList.add('hidden');
  document.getElementById('dict-suggestions')?.classList.remove('hidden');
}

function quickLookup(word) {
  const input = document.getElementById('dict-search-input');
  if (input) input.value = word;
  document.getElementById('btn-clear-search')?.classList.remove('hidden');
  executeLookup(word);
}

async function executeLookup(word) {
  try {
    const res = await fetch(`/api/dictionary?word=${encodeURIComponent(word)}`);
    if (!res.ok) throw new Error('Lookup failed');
    const data = await res.json();
    currentLookupWord = data;
    renderDictResult(data);
  } catch (err) {
    showToast('Lookup error: ' + err.message);
  }
}

function renderDictResult(data) {
  const wrap = document.getElementById('dict-result-wrap');
  const suggs = document.getElementById('dict-suggestions');
  if (!wrap) return;

  wrap.classList.remove('hidden');
  if (suggs) suggs.classList.add('hidden');

  setText('dict-headword', data.word);
  setText('dict-pos', data.part_of_speech || 'noun');
  setText('dict-phonetic-us', data.phonetic_us || data.phonetic_uk || '');
  setText('dict-definition', data.definition || 'No definition available.');
  setText('dict-example', data.example ? `"${data.example}"` : 'No example context.');

  const transWrap = document.getElementById('dict-trans-wrap');
  if (transWrap) {
    if (data.translation_es) {
      transWrap.classList.remove('hidden');
      setText('dict-translation', data.translation_es);
    } else {
      transWrap.classList.add('hidden');
    }
  }

  // Synonyms
  const synsWrap = document.getElementById('dict-synonyms');
  if (synsWrap) {
    synsWrap.innerHTML = '';
    const syns = data.synonyms || [];
    if (syns.length > 0) {
      syns.forEach(s => {
        const chip = document.createElement('span');
        chip.className = 'chip';
        chip.innerText = s;
        synsWrap.appendChild(chip);
      });
    }
  }

  // Add to deck button state
  const addBtn = document.getElementById('btn-add-deck');
  if (addBtn) {
    if (data.already_in_deck) {
      addBtn.innerText = 'In Deck ✓';
      addBtn.className = 'btn-add in-deck';
    } else {
      addBtn.innerText = '+ Add to Deck';
      addBtn.className = 'btn-add';
    }
  }
}

async function addCurrentLookupToDeck() {
  if (!currentLookupWord) return;
  const addBtn = document.getElementById('btn-add-deck');

  try {
    const res = await fetch('/api/deck/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word_info: currentLookupWord }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to add');

    if (addBtn) {
      addBtn.innerText = 'In Deck ✓';
      addBtn.className = 'btn-add in-deck';
    }
    showToast(`Added '${currentLookupWord.word}' to personal vocabulary deck!`);
    fetchState(false);
  } catch (err) {
    showToast('Failed to add word: ' + err.message);
  }
}

// 6. My Deck List View & Filters
function setDeckFilter(filter, elem) {
  currentFilter = filter;
  document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
  if (elem) elem.classList.add('active');
  renderDeckList();
}

function renderDeckList() {
  const container = document.getElementById('deck-list');
  if (!container) return;
  const words = appState.words || [];
  const now = timeNow();

  let filtered = words;
  if (currentFilter === 'due') {
    filtered = words.filter(w => (w.next_review || 0) <= now);
  } else if (currentFilter === 'learning') {
    filtered = words.filter(w => w.status === 'learning');
  } else if (currentFilter === 'mastered') {
    filtered = words.filter(w => w.status === 'mastered');
  }

  container.innerHTML = '';
  if (filtered.length === 0) {
    container.innerHTML = `<div class="empty-state" style="padding: 30px;"><p>No words in this filter category.</p></div>`;
    return;
  }

  filtered.forEach(w => {
    const item = document.createElement('div');
    item.className = 'deck-item';
    const isDue = (w.next_review || 0) <= now;
    const dueLabel = isDue ? '<span class="due-tag">DUE NOW</span>' : `<span class="status-badge">${formatDays(w.interval_days)}</span>`;

    item.innerHTML = `
      <div class="deck-item-left">
        <h4>${escapeHtml(w.word)} <span class="pos-badge" style="font-size: 9px; padding: 1px 5px;">${w.part_of_speech}</span></h4>
        <p>${escapeHtml(w.definition)}</p>
      </div>
      <div class="deck-item-right">
        ${dueLabel}
        <button class="btn-icon" style="width: 30px; height: 30px;" onclick="deleteDeckWord('${w.id}')" title="Delete word">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
        </button>
      </div>
    `;
    container.appendChild(item);
  });
}

async function deleteDeckWord(wordId) {
  if (!confirm('Remove this word from your vocabulary deck? (Audited against Landauer bit erasure limit)')) {
    return;
  }
  try {
    const res = await fetch('/api/deck/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word_id: wordId }),
    });
    if (!res.ok) throw new Error('Delete failed');
    showToast('Word removed from deck (128 bits erased)');
    fetchState(false);
  } catch (err) {
    showToast(err.message);
  }
}

// 7. Functorial Undo / Redo
async function triggerUndo() {
  try {
    const res = await fetch('/api/undo', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast('Undone! Previous rating restored (Functorial Reversibility)');
      fetchState(false);
    } else {
      showToast('Nothing to undo.');
    }
  } catch (err) {
    showToast(err.message);
  }
}

async function triggerRedo() {
  try {
    const res = await fetch('/api/redo', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast('Redone rating morphism.');
      fetchState(false);
    } else {
      showToast('Nothing to redo.');
    }
  } catch (err) {
    showToast(err.message);
  }
}

// 8. Tab Navigation
function switchTab(tabName) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  const targetView = document.getElementById(`view-${tabName}`);
  if (targetView) targetView.classList.add('active');

  const tabs = ['review', 'dictionary', 'deck', 'stats'];
  const idx = tabs.indexOf(tabName);
  if (idx !== -1) {
    const navItems = document.querySelectorAll('.bottom-nav .nav-item');
    if (navItems[idx]) navItems[idx].classList.add('active');
  }

  if (tabName === 'review') buildReviewQueue();
  else if (tabName === 'deck') renderDeckList();
}

// Helper utilities
function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.innerText = text;
}

function timeNow() {
  return Date.now() / 1000;
}

function formatDays(days) {
  if (!days || days < 0.1) return 'Due today';
  if (days < 1) return 'Due soon';
  return `${Math.round(days)}d interval`;
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.innerText = msg;
  toast.classList.remove('hidden');
  setTimeout(() => toast.classList.add('hidden'), 3500);
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[m]);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  fetchState();
});
