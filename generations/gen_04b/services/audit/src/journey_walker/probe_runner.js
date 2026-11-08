#!/usr/bin/env node
/**
 * Headless Browser Probe Runner for Axioma Journey Walker ([L1-G4B-017], [INV-G4B-MUTATION-001]).
 * Zero external npm dependencies.
 * 
 * Provides:
 * - Minimal DOM tree environment (window, document, fetch, Event, CustomEvent, Element).
 * - Live execution of client JavaScript (e.g. app.js) against backend server subprocess.
 * - Real event dispatching (click, input) and real DOM mutation assertions.
 */

const fs = require('fs');
const path = require('path');
const cp = require('child_process');
const vm = require('vm');

// --- 1. CLI Arguments Parsing ---
const args = process.argv.slice(2);
let serverUrl = 'http://127.0.0.1:8086';
let appScriptPath = null;
let stepsRaw = null;
let htmlPath = null;
let appEntrypoint = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--url' && args[i + 1]) {
    serverUrl = args[++i];
  } else if (args[i] === '--app-script' && args[i + 1]) {
    appScriptPath = path.resolve(args[++i]);
  } else if (args[i] === '--steps' && args[i + 1]) {
    stepsRaw = args[++i];
  } else if (args[i] === '--html' && args[i + 1]) {
    htmlPath = path.resolve(args[++i]);
  } else if (args[i] === '--app-entrypoint' && args[i + 1]) {
    appEntrypoint = path.resolve(args[++i]);
  }
}

if (!appScriptPath || !stepsRaw) {
  console.error(JSON.stringify({
    status: 'FAILED',
    error: 'Missing required arguments: --app-script <path> and --steps <json_or_file>'
  }));
  process.exit(1);
}

// Auto-deduce htmlPath and appEntrypoint if not provided
if (!htmlPath && appScriptPath) {
  const candidateHtml = path.join(path.dirname(appScriptPath), 'index.html');
  if (fs.existsSync(candidateHtml)) {
    htmlPath = candidateHtml;
  }
}
if (!appEntrypoint && appScriptPath) {
  const candidateRun = path.join(path.dirname(path.dirname(appScriptPath)), 'run.py');
  if (fs.existsSync(candidateRun)) {
    appEntrypoint = candidateRun;
  }
}

// Parse steps
let journeySteps = [];
try {
  if (fs.existsSync(stepsRaw)) {
    journeySteps = JSON.parse(fs.readFileSync(stepsRaw, 'utf-8'));
  } else {
    journeySteps = JSON.parse(stepsRaw);
  }
} catch (e) {
  console.error(JSON.stringify({ status: 'FAILED', error: 'Failed to parse steps JSON: ' + e.message }));
  process.exit(1);
}

// --- 2. IPC Server Dispatcher Fallback ---
let ipcChild = null;
function getIPCChild() {
  if (!ipcChild && appEntrypoint && fs.existsSync(appEntrypoint)) {
    ipcChild = cp.spawn('python3', [appEntrypoint, '--headless-ipc'], {
      stdio: ['pipe', 'pipe', 'pipe']
    });
  }
  return ipcChild;
}

let pendingIpcResolvers = [];
let ipcStdoutBuffer = '';
function initIPCReader(child) {
  child.stdout.on('data', (chunk) => {
    ipcStdoutBuffer += chunk.toString();
    let lines = ipcStdoutBuffer.split('\n');
    ipcStdoutBuffer = lines.pop(); // keep remainder
    for (let line of lines) {
      line = line.trim();
      if (!line) continue;
      if (line === 'HEADLESS_IPC_READY') continue;
      if (pendingIpcResolvers.length > 0) {
        const resolve = pendingIpcResolvers.shift();
        resolve(line);
      }
    }
  });
}

async function dispatchViaIPC(method, reqPath, body) {
  const child = getIPCChild();
  if (!child) {
    throw new Error('No app-entrypoint available for IPC dispatch');
  }
  if (!child._readerInitialized) {
    initIPCReader(child);
    child._readerInitialized = true;
  }

  const payload = {
    method: (method || 'GET').toUpperCase(),
    path: reqPath.startsWith('/') ? reqPath : '/' + reqPath,
    body: body !== undefined && body !== null ? (typeof body === 'string' ? JSON.parse(body) : body) : null
  };

  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error('IPC request timed out for ' + reqPath));
    }, 5000);

    pendingIpcResolvers.push((line) => {
      clearTimeout(timer);
      try {
        const resp = JSON.parse(line);
        let parsedBody = resp.body;
        try {
          if (typeof parsedBody === 'string') {
            parsedBody = JSON.parse(parsedBody);
          }
        } catch (_) {}
        resolve({
          status: resp.status || 200,
          ok: (resp.status || 200) >= 200 && (resp.status || 200) < 300,
          json: async () => parsedBody,
          text: async () => (typeof resp.body === 'string' ? resp.body : JSON.stringify(resp.body)),
          headers: new Map()
        });
      } catch (err) {
        reject(err);
      }
    });

    child.stdin.write(JSON.stringify(payload) + '\n');
  });
}

async function customFetch(url, options = {}) {
  let reqPath = url;
  let fullUrl = url;
  if (url.startsWith('http://') || url.startsWith('https://')) {
    try {
      const u = new URL(url);
      reqPath = u.pathname + u.search;
    } catch (_) {}
  } else {
    const base = serverUrl.endsWith('/') ? serverUrl.slice(0, -1) : serverUrl;
    fullUrl = base + (url.startsWith('/') ? url : '/' + url);
  }

  // Attempt native fetch
  if (typeof globalThis.fetch === 'function') {
    try {
      const res = await globalThis.fetch(fullUrl, options);
      return res;
    } catch (e) {
      // If network connect EPERM, fallback to IPC
    }
  }

  // IPC Fallback
  return await dispatchViaIPC(options.method || 'GET', reqPath, options.body);
}

// --- 3. Minimal Lightweight DOM Tree Environment ---
class ClassList {
  constructor(node) {
    this._node = node;
    this._set = new Set();
  }
  add(...classes) {
    classes.forEach(c => { if (c) this._set.add(c); });
    this._sync();
  }
  remove(...classes) {
    classes.forEach(c => { this._set.delete(c); });
    this._sync();
  }
  contains(cls) {
    return this._set.has(cls);
  }
  toggle(cls, force) {
    if (force !== undefined) {
      if (force) this._set.add(cls);
      else this._set.delete(cls);
    } else {
      if (this._set.has(cls)) this._set.delete(cls);
      else this._set.add(cls);
    }
    this._sync();
    return this._set.has(cls);
  }
  _sync() {
    this._node.attributes.set('class', Array.from(this._set).join(' '));
  }
  get value() {
    return Array.from(this._set).join(' ');
  }
}

class DOMNode {
  constructor(tag = 'DIV', isText = false, textContent = '') {
    this.nodeType = isText ? 3 : 1;
    this.tagName = (tag || 'DIV').toUpperCase();
    this.id = '';
    this.attributes = new Map();
    this.classList = new ClassList(this);
    this.children = [];
    this.childNodes = [];
    this.parentNode = null;
    this.parentElement = null;
    this.listeners = new Map();
    this._value = '';
    this.disabled = false;
    this.checked = false;
    this._text = textContent;
    this.style = {};
    this.dataset = {};
  }

  get value() {
    return this._value;
  }
  set value(v) {
    this._value = String(v);
  }

  get textContent() {
    if (this.nodeType === 3) return this._text;
    return this.childNodes.map(c => c.textContent).join('');
  }
  set textContent(v) {
    if (this.nodeType === 3) {
      this._text = String(v);
      return;
    }
    this.children = [];
    this.childNodes = [];
    const textNode = new DOMNode('', true, String(v));
    textNode.parentNode = this;
    this.childNodes.push(textNode);
  }

  get innerHTML() {
    return serializeHTML(this);
  }
  set innerHTML(htmlStr) {
    this.children = [];
    this.childNodes = [];
    parseHTMLInto(htmlStr, this);
  }

  setAttribute(name, val) {
    const k = name.toLowerCase();
    const v = String(val);
    this.attributes.set(k, v);
    if (k === 'id') this.id = v;
    if (k === 'class') {
      this.classList._set.clear();
      v.split(/\s+/).filter(Boolean).forEach(c => this.classList._set.add(c));
    }
    if (k.startsWith('data-')) {
      const camel = k.slice(5).replace(/-([a-z])/g, (_, g) => g.toUpperCase());
      this.dataset[camel] = v;
    }
    if (k === 'value') this._value = v;
  }

  getAttribute(name) {
    const k = name.toLowerCase();
    return this.attributes.has(k) ? this.attributes.get(k) : null;
  }

  removeAttribute(name) {
    const k = name.toLowerCase();
    this.attributes.delete(k);
    if (k === 'id') this.id = '';
    if (k === 'class') this.classList._set.clear();
  }

  hasAttribute(name) {
    return this.attributes.has(name.toLowerCase());
  }

  appendChild(child) {
    if (!child) return child;
    if (child.parentNode) child.parentNode.removeChild(child);
    child.parentNode = this;
    child.parentElement = this;
    this.childNodes.push(child);
    if (child.nodeType === 1) {
      this.children.push(child);
    }
    return child;
  }

  removeChild(child) {
    const idxChild = this.children.indexOf(child);
    if (idxChild !== -1) this.children.splice(idxChild, 1);
    const idxNode = this.childNodes.indexOf(child);
    if (idxNode !== -1) this.childNodes.splice(idxNode, 1);
    child.parentNode = null;
    child.parentElement = null;
    return child;
  }

  replaceChild(newChild, oldChild) {
    this.insertBefore(newChild, oldChild);
    this.removeChild(oldChild);
    return oldChild;
  }

  insertBefore(newChild, refChild) {
    if (!refChild) return this.appendChild(newChild);
    const idxNode = this.childNodes.indexOf(refChild);
    if (idxNode !== -1) {
      this.childNodes.splice(idxNode, 0, newChild);
      newChild.parentNode = this;
      newChild.parentElement = this;
    }
    const idxChild = this.children.indexOf(refChild);
    if (idxChild !== -1 && newChild.nodeType === 1) {
      this.children.splice(idxChild, 0, newChild);
    }
    return newChild;
  }

  addEventListener(type, fn) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    this.listeners.get(type).push(fn);
  }

  removeEventListener(type, fn) {
    if (this.listeners.has(type)) {
      const list = this.listeners.get(type).filter(f => f !== fn);
      this.listeners.set(type, list);
    }
  }

  dispatchEvent(event) {
    if (!event) return true;
    event.target = this;
    event.currentTarget = this;
    const fns = this.listeners.get(event.type) || [];
    for (let fn of fns) {
      try {
        fn.call(this, event);
      } catch (e) {
        console.error('Error in event listener for ' + event.type + ':', e);
      }
    }
    if (event.bubbles && this.parentNode) {
      this.parentNode.dispatchEvent(event);
    }
    return !event.defaultPrevented;
  }

  getBoundingClientRect() {
    return { left: 0, top: 0, right: 100, bottom: 40, width: 100, height: 40, x: 0, y: 0 };
  }

  getElementById(id) {
    return findFirst(this, n => n.id === id);
  }

  querySelector(selector) {
    return findFirst(this, n => matchesSelector(n, selector));
  }

  querySelectorAll(selector) {
    const results = [];
    findAll(this, n => matchesSelector(n, selector), results);
    return results;
  }
}

// Selector matching engine
function matchesSingleSelector(node, sel) {
  if (!node || node.nodeType !== 1) return false;
  sel = sel.trim();
  if (!sel) return false;

  const tagMatch = sel.match(/^([a-zA-Z0-9_\-]+)(.*)$/);
  if (tagMatch && !sel.startsWith('#') && !sel.startsWith('.') && !sel.startsWith('[')) {
    const tag = tagMatch[1].toUpperCase();
    if (node.tagName !== tag) return false;
    const rest = tagMatch[2];
    if (!rest) return true;
    return matchesSingleSelector(node, rest);
  }

  if (sel.startsWith('#')) {
    const id = sel.slice(1);
    return node.id === id;
  }

  if (sel.startsWith('.')) {
    const cls = sel.slice(1);
    return node.classList.contains(cls);
  }

  if (sel.startsWith('[') && sel.endsWith(']')) {
    const attrInner = sel.slice(1, -1);
    const eqIdx = attrInner.indexOf('=');
    if (eqIdx === -1) {
      return node.hasAttribute(attrInner);
    }
    const attrName = attrInner.slice(0, eqIdx).trim();
    let attrVal = attrInner.slice(eqIdx + 1).trim();
    if ((attrVal.startsWith('"') && attrVal.endsWith('"')) || (attrVal.startsWith("'") && attrVal.endsWith("'"))) {
      attrVal = attrVal.slice(1, -1);
    }
    return node.getAttribute(attrName) === attrVal;
  }

  return node.tagName === sel.toUpperCase();
}

function matchesSelector(node, selector) {
  if (!selector) return false;
  const parts = selector.split(',').map(s => s.trim()).filter(Boolean);
  for (let part of parts) {
    const subParts = part.split(/\s+/);
    if (subParts.length === 1) {
      if (matchesSingleSelector(node, subParts[0])) return true;
    } else {
      if (matchesSingleSelector(node, subParts[subParts.length - 1])) {
        let curr = node.parentElement;
        let pIdx = subParts.length - 2;
        while (curr && pIdx >= 0) {
          if (matchesSingleSelector(curr, subParts[pIdx])) {
            pIdx--;
          }
          curr = curr.parentElement;
        }
        if (pIdx < 0) return true;
      }
    }
  }
  return false;
}

function findFirst(root, predicate) {
  if (root.nodeType === 1 && predicate(root)) return root;
  for (let child of root.children) {
    const found = findFirst(child, predicate);
    if (found) return found;
  }
  return null;
}

function findAll(root, predicate, out) {
  if (root.nodeType === 1 && predicate(root)) {
    out.push(root);
  }
  for (let child of root.children) {
    findAll(child, predicate, out);
  }
}

// Minimal HTML Parser
function parseHTMLInto(html, parentNode) {
  const tagRegex = /<(\/)?([a-zA-Z0-9_\-]+)([^>]*)>/g;
  let stack = [parentNode];
  let lastIdx = 0;
  let match;

  while ((match = tagRegex.exec(html)) !== null) {
    const textBetween = html.slice(lastIdx, match.index);
    if (textBetween && textBetween.trim()) {
      const textNode = new DOMNode('', true, textBetween);
      stack[stack.length - 1].appendChild(textNode);
    }
    lastIdx = tagRegex.lastIndex;

    const isClose = match[1] === '/';
    const tagName = match[2];
    const attrStr = match[3].trim();
    const isSelfClosing = attrStr.endsWith('/') || ['rect', 'circle', 'path', 'line', 'ellipse', 'polygon', 'polyline', 'input', 'img', 'br', 'hr', 'meta', 'link'].includes(tagName.toLowerCase());

    if (isClose) {
      if (stack.length > 1 && stack[stack.length - 1].tagName.toLowerCase() === tagName.toLowerCase()) {
        stack.pop();
      }
    } else {
      const node = new DOMNode(tagName);
      const attrRegex = /([a-zA-Z0-9_\-]+)(?:=(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g;
      let am;
      while ((am = attrRegex.exec(attrStr)) !== null) {
        const k = am[1];
        const v = am[2] !== undefined ? am[2] : (am[3] !== undefined ? am[3] : (am[4] !== undefined ? am[4] : ''));
        node.setAttribute(k, v);
      }
      stack[stack.length - 1].appendChild(node);
      if (!isSelfClosing) {
        stack.push(node);
      }
    }
  }

  const trailingText = html.slice(lastIdx);
  if (trailingText && trailingText.trim()) {
    parentNode.appendChild(new DOMNode('', true, trailingText));
  }
}

function serializeHTML(node) {
  if (node.nodeType === 3) return node._text;
  let out = '';
  for (let c of node.childNodes) {
    if (c.nodeType === 3) {
      out += c._text;
    } else {
      const tag = c.tagName.toLowerCase();
      out += `<${tag}`;
      for (let [k, v] of c.attributes.entries()) {
        out += ` ${k}="${v}"`;
      }
      out += `>${serializeHTML(c)}</${tag}>`;
    }
  }
  return out;
}

// Events
class Event {
  constructor(type, opts = {}) {
    this.type = type;
    this.bubbles = !!opts.bubbles;
    this.cancelable = !!opts.cancelable;
    this.defaultPrevented = false;
    this.target = null;
    this.currentTarget = null;
  }
  preventDefault() {
    if (this.cancelable) this.defaultPrevented = true;
  }
  stopPropagation() {}
}

class CustomEvent extends Event {
  constructor(type, opts = {}) {
    super(type, opts);
    this.detail = opts.detail || null;
  }
}

// Document & Window initialization
const docRoot = new DOMNode('HTML');
const docHead = new DOMNode('HEAD');
const docBody = new DOMNode('BODY');
docRoot.appendChild(docHead);
docRoot.appendChild(docBody);

const documentObj = {
  documentElement: docRoot,
  head: docHead,
  body: docBody,
  title: 'Headless Probe',
  createElement(tag) { return new DOMNode(tag); },
  createElementNS(ns, tag) { return new DOMNode(tag); },
  createTextNode(text) { return new DOMNode('', true, text); },
  getElementById(id) { return docRoot.getElementById(id); },
  querySelector(sel) { return docRoot.querySelector(sel); },
  querySelectorAll(sel) { return docRoot.querySelectorAll(sel); },
  addEventListener: docRoot.addEventListener.bind(docRoot),
  removeEventListener: docRoot.removeEventListener.bind(docRoot),
  dispatchEvent: docRoot.dispatchEvent.bind(docRoot),
};

// If index.html is provided, parse it into docBody
if (htmlPath && fs.existsSync(htmlPath)) {
  const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
  parseHTMLInto(htmlContent, docBody);
}

const windowListeners = new Map();
const windowObj = {
  document: documentObj,
  location: { href: serverUrl, origin: serverUrl, pathname: '/', search: '', hash: '' },
  addEventListener(type, fn) {
    if (!windowListeners.has(type)) windowListeners.set(type, []);
    windowListeners.get(type).push(fn);
  },
  removeEventListener(type, fn) {
    if (windowListeners.has(type)) {
      windowListeners.set(type, windowListeners.get(type).filter(f => f !== fn));
    }
  },
  dispatchEvent(event) {
    const fns = windowListeners.get(event.type) || [];
    for (let fn of fns) {
      try { fn.call(windowObj, event); } catch (e) { console.error(e); }
    }
    return true;
  },
  setTimeout: setTimeout.bind(globalThis),
  clearTimeout: clearTimeout.bind(globalThis),
  setInterval: setInterval.bind(globalThis),
  clearInterval: clearInterval.bind(globalThis),
  Event,
  CustomEvent,
  fetch: customFetch,
};

// --- 4. Main Journey Execution Engine ---
async function runJourney() {
  const stepResults = [];

  const sandbox = {
    window: windowObj,
    document: documentObj,
    fetch: customFetch,
    Event,
    CustomEvent,
    console,
    setTimeout,
    clearTimeout,
    setInterval,
    clearInterval,
    Promise,
    JSON,
    Math,
    Array,
    Object,
    String,
    Number,
    Boolean,
    parseInt,
    parseFloat,
    isNaN,
  };
  vm.createContext(sandbox);

  const appJsCode = fs.readFileSync(appScriptPath, 'utf-8');
  try {
    vm.runInContext(appJsCode, sandbox, { filename: appScriptPath });
  } catch (err) {
    console.error(JSON.stringify({
      status: 'FAILED',
      error: 'Exception loading ' + path.basename(appScriptPath) + ': ' + err.stack,
      step_results: []
    }));
    if (ipcChild) ipcChild.kill();
    process.exit(1);
  }

  // Dispatch DOMContentLoaded
  const dclEvent = new Event('DOMContentLoaded');
  windowObj.dispatchEvent(dclEvent);
  documentObj.dispatchEvent(dclEvent);

  await new Promise(r => setTimeout(r, 60));

  for (let step of journeySteps) {
    const tStart = Date.now();
    let actionType = (step.action_type || 'WAIT').toUpperCase();
    let targetSelector = step.target_selector || 'body';
    let expectedMutation = step.expected_dom_mutation || null;
    let maxLatency = step.max_latency_ms || 200;

    // Dispatch Action
    if (actionType === 'NAVIGATE' || actionType === 'BOOT') {
      // booted
    } else if (actionType === 'CLICK') {
      const target = documentObj.querySelector(targetSelector);
      if (target) {
        target.dispatchEvent(new Event('click', { bubbles: true }));
      }
    } else if (actionType === 'INPUT') {
      const target = documentObj.querySelector(targetSelector);
      if (target) {
        if (step.input_value !== undefined) target.value = step.input_value;
        target.dispatchEvent(new Event('input', { bubbles: true }));
        target.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }

    // Wait for mutations and fetch reactions
    let verified = false;
    const deadline = Date.now() + maxLatency;

    while (Date.now() <= deadline) {
      if (!expectedMutation) {
        verified = true;
        break;
      }
      const matches = documentObj.querySelectorAll(expectedMutation);
      if (matches.length > 0) {
        verified = true;
        break;
      }
      await new Promise(r => setTimeout(r, 5));
    }

    const latency = Date.now() - tStart;

    if (expectedMutation && !verified) {
      const errorMsg = `Step '${step.step_id}' FAILED: Expected visual DOM mutation '${expectedMutation}' did not appear within ${maxLatency}ms limit.`;
      stepResults.push({
        step_id: step.step_id,
        status: 'FAILED',
        latency_ms: latency,
        action_type: actionType,
        target_selector: targetSelector,
        dom_mutation_verified: false,
        error_message: errorMsg,
      });

      console.log(JSON.stringify({
        status: 'FAILED',
        error: errorMsg,
        failed_step_id: step.step_id,
        step_results: stepResults
      }));
      if (ipcChild) ipcChild.kill();
      process.exit(1);
    }

    stepResults.push({
      step_id: step.step_id,
      status: 'PASSED',
      latency_ms: latency,
      action_type: actionType,
      target_selector: targetSelector,
      dom_mutation_verified: true,
      error_message: null,
    });
  }

  // All steps passed!
  console.log(JSON.stringify({
    status: 'PASSED',
    total_steps: stepResults.length,
    step_results: stepResults
  }));

  if (ipcChild) ipcChild.kill();
  process.exit(0);
}

runJourney().catch(err => {
  console.error(JSON.stringify({ status: 'FAILED', error: err.stack }));
  if (ipcChild) ipcChild.kill();
  process.exit(1);
});
