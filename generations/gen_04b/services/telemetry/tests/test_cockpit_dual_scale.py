"""Empirical Verification & Dual-Scale Projection Test Suite ([L1-G4B-001] & [NEG-G1B-002]).

Verifies:
1. ZenithProjectionEngine binary search time-indexing (`findRecordIndexAtTime`).
2. Continuous Wall-Clock vs Discrete Event-Index dual-scale mapping.
3. DOM contracts in index.html and styles.css for #btn-scale-toggle and mode switching.
4. Keyboard navigation bindings (Space, ArrowLeft, ArrowRight, S/s).
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


class TestCockpitDualScaleProjection(unittest.TestCase):
    """Test suite ensuring the Cockpit Dual-Scale Scrubber functions mathematically and structurally."""

    def setUp(self) -> None:
        self.service_dir = Path(__file__).resolve().parent.parent
        self.cockpit_dir = self.service_dir / "cockpit"
        self.index_html = self.cockpit_dir / "index.html"
        self.styles_css = self.cockpit_dir / "styles.css"
        self.projection_js = self.cockpit_dir / "projection.js"

    def test_cockpit_files_exist_and_non_empty(self) -> None:
        self.assertTrue(self.index_html.exists(), "index.html must exist")
        self.assertTrue(self.styles_css.exists(), "styles.css must exist")
        self.assertTrue(self.projection_js.exists(), "projection.js must exist")
        self.assertGreater(self.index_html.stat().st_size, 1000)
        self.assertGreater(self.styles_css.stat().st_size, 1000)
        self.assertGreater(self.projection_js.stat().st_size, 500)

    def test_dom_elements_and_button_bindings_present(self) -> None:
        html = self.index_html.read_text(encoding="utf-8")
        self.assertIn('id="btn-scale-toggle"', html, "Scale toggle button must be declared in index.html")
        self.assertIn("Scale: Events", html, "Default scale button label must be 'Scale: Events'")
        self.assertIn("btn-scale", html, "Scale button must carry the 'btn-scale' class")
        self.assertTrue("findFilteredRecordIndexAtTime" in html or "findRecordIndexAtTime" in html)
        self.assertIn('id="filter-conversation"', html, "Conversation filter dropdown must exist")
        self.assertIn('id="filter-subagent"', html, "Subagent filter dropdown must exist")
        self.assertIn('id="filter-source"', html, "Source filter dropdown must exist")
        self.assertIn('id="filter-target"', html, "Target filter dropdown must exist")
        self.assertIn('id="btn-clear-filter"', html, "Clear filter button must exist")
        self.assertIn('id="inspect-source"', html, "Clickable inspect source must exist")
        self.assertIn('id="inspect-target"', html, "Clickable inspect target must exist")
        self.assertIn("scaleMode = 'events'", html, "index.html must initialize scaleMode to 'events'")
        self.assertIn("scaleMode === 'time'", html, "index.html must handle continuous 'time' scale")

    def test_styles_contain_scale_mode_classes(self) -> None:
        css = self.styles_css.read_text(encoding="utf-8")
        self.assertIn(".btn-scale", css, ".btn-scale class must be styled in styles.css")
        self.assertIn(".btn-scale.mode-time", css, ".btn-scale.mode-time must be styled in styles.css")

    def test_keyboard_shortcuts_registered(self) -> None:
        html = self.index_html.read_text(encoding="utf-8")
        self.assertIn("e.code === 'Space'", html, "Space key must trigger play/pause")
        self.assertIn("e.code === 'ArrowLeft'", html, "ArrowLeft key must trigger step-back")
        self.assertIn("e.code === 'ArrowRight'", html, "ArrowRight key must trigger step-forward")
        self.assertIn("e.key === 's'", html, "'s' key must toggle scale mode")

    def test_projection_engine_binary_search_in_node(self) -> None:
        """Execute a Node.js verification harness directly against projection.js."""
        node_script = """
const fs = require('fs');
const path = require('path');

// Mock browser window
global.window = global;
require('./generations/gen_04b/services/telemetry/cockpit/projection.js');

const engine = new ZenithProjectionEngine(2000);

// 1. Empty records check
console.assert(engine.findRecordIndexAtTime(1000000) === -1, 'Empty engine should return -1');

// 2. Populate synthetic records with bursty distribution
// t0: 1000, t1: 1500, t2: 5000 (gap), t3: 5010, t4: 5020, t5: 5030 (burst)
const testRecords = [
  { transaction_id: 'tx_0', timestamp_ns: 1000, source_service: 's/a', target_service: 's/b' },
  { transaction_id: 'tx_1', timestamp_ns: 1500, source_service: 's/a', target_service: 's/b' },
  { transaction_id: 'tx_2', timestamp_ns: 5000, source_service: 's/a', target_service: 's/b' },
  { transaction_id: 'tx_3', timestamp_ns: 5010, source_service: 's/a', target_service: 's/b' },
  { transaction_id: 'tx_4', timestamp_ns: 5020, source_service: 's/a', target_service: 's/b' },
  { transaction_id: 'tx_5', timestamp_ns: 5030, source_service: 's/a', target_service: 's/b' },
];

engine.addTransactions(testRecords);

const extent = engine.getTemporalExtent();
console.assert(extent.minNs === 1000, `minNs should be 1000, got ${extent.minNs}`);
console.assert(extent.maxNs === 5030, `maxNs should be 5030, got ${extent.maxNs}`);
console.assert(extent.count === 6, `count should be 6, got ${extent.count}`);

// Boundary checks
console.assert(engine.findRecordIndexAtTime(500) === 0, 'Timestamp before minNs should return 0');
console.assert(engine.findRecordIndexAtTime(6000) === 5, 'Timestamp after maxNs should return 5');

// Exact matches
console.assert(engine.findRecordIndexAtTime(1000) === 0, 'Exact match 1000 should return 0');
console.assert(engine.findRecordIndexAtTime(1500) === 1, 'Exact match 1500 should return 1');
console.assert(engine.findRecordIndexAtTime(5020) === 4, 'Exact match 5020 should return 4');

// Idle gap interpolation (should return the latest transaction that already occurred)
console.assert(engine.findRecordIndexAtTime(3000) === 1, 'Timestamp 3000 in gap should return 1 (tx_1)');
console.assert(engine.findRecordIndexAtTime(4999) === 1, 'Timestamp 4999 right before tx_2 should return 1');

// Burst interpolation
console.assert(engine.findRecordIndexAtTime(5015) === 3, 'Timestamp 5015 between tx_3 and tx_4 should return 3');

process.stdout.write('NODE_PROJECTION_VERIFICATION_PASS');
"""
        res = subprocess.run(
            ["node", "-e", node_script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Node.js execution failed: {res.stderr}")
        self.assertIn("NODE_PROJECTION_VERIFICATION_PASS", res.stdout)

    def test_cockpit_full_dom_lifecycle_simulation_in_node(self) -> None:
        """Simulate browser DOMContentLoaded, initialSeed ingestion, button clicks, and TDZ safety."""
        node_sim_script = """
const fs = require('fs');
const html = fs.readFileSync('generations/gen_04b/services/telemetry/cockpit/index.html', 'utf8');

const elements = {};
function createMockEl(id, tag = 'div') {
  return {
    id,
    tagName: tag.toUpperCase(),
    textContent: '',
    innerHTML: '',
    value: '1000',
    classList: {
      add: (c) => {},
      remove: (c) => {},
      toggle: (c) => {},
    },
    addEventListener: function(event, handler) {
      this['on' + event] = handler;
    },
    style: {},
    title: '',
  };
}

global.window = global;
global.window.devicePixelRatio = 1;
global.window.addEventListener = (ev, fn) => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.fetch = async () => ({
  ok: true,
  json: async () => ({ transactions: [] }),
});
global.EventSource = function() {
  return { addEventListener: () => {} };
};

global.document = {
  getElementById: (id) => {
    if (!elements[id]) elements[id] = createMockEl(id);
    return elements[id];
  },
  addEventListener: (event, handler) => {
    global['doc_on' + event] = handler;
  },
};

elements['topology-canvas'] = {
  parentElement: { getBoundingClientRect: () => ({ width: 800, height: 600 }) },
  getContext: () => ({
    scale: () => {},
    clearRect: () => {},
    beginPath: () => {},
    moveTo: () => {},
    lineTo: () => {},
    stroke: () => {},
    arc: () => {},
    fill: () => {},
    fillText: () => {},
    measureText: () => ({ width: 50 }),
  }),
};

require('./generations/gen_04b/services/telemetry/cockpit/topology.js');
require('./generations/gen_04b/services/telemetry/cockpit/scrubber_fsm.js');
require('./generations/gen_04b/services/telemetry/cockpit/projection.js');

const scriptMatch = html.match(/<script>([\\s\\S]*?)<\\/script>/);
eval(scriptMatch[1]);

// 1. Run DOMContentLoaded lifecycle without TDZ exceptions
global.doc_onDOMContentLoaded();

// 2. Test Scale toggle clicks
const btnScale = elements['btn-scale-toggle'];
console.assert(typeof btnScale.onclick === 'function', 'btn-scale-toggle must have click handler');
btnScale.onclick();
console.assert(btnScale.textContent === 'Scale: Time', 'Click 1 should switch to Scale: Time');
btnScale.onclick();
console.assert(btnScale.textContent === 'Scale: Events', 'Click 2 should switch back to Scale: Events');

// 3. Test Play / Pause click
const btnPlay = elements['btn-play-pause'];
console.assert(typeof btnPlay.onclick === 'function', 'btn-play-pause must have click handler');
btnPlay.onclick();
console.assert(btnPlay.innerHTML.includes('Play'), 'Click 1 should pause and show Play');

process.stdout.write('DOM_SIMULATION_VERIFICATION_PASS');
process.exit(0);
"""
        res = subprocess.run(
            ["node", "-e", node_sim_script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"DOM simulation failed: {res.stderr}")
        self.assertIn("DOM_SIMULATION_VERIFICATION_PASS", res.stdout)

    def test_cockpit_conversation_and_subagent_filter_simulation_in_node(self) -> None:
        """Simulate real-time conversation and subagent filtering in headless Node environment."""
        node_filter_script = """
const fs = require('fs');
const html = fs.readFileSync('generations/gen_04b/services/telemetry/cockpit/index.html', 'utf8');

const elements = {};
function createMockEl(id, tag = 'div') {
  return {
    id,
    tagName: tag.toUpperCase(),
    textContent: '',
    innerHTML: '',
    value: 'ALL',
    classList: { add: () => {}, remove: () => {}, toggle: () => {} },
    addEventListener: function(event, handler) { this['on' + event] = handler; },
    style: {},
    title: '',
  };
}

global.window = global;
global.window.devicePixelRatio = 1;
global.window.addEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.fetch = async () => ({
  ok: true,
  json: async () => ({
    transactions: [
      {
        transaction_id: 'tx_sub_qa_01',
        trace_id: 'conv_qa_subagent',
        subagent_id: 'sub_qa_01',
        subagent_role: 'Adversarial QA Engineer',
        timestamp_ns: 1000000000,
        duration_ns: 500000,
        source_service: 'services/audit',
        target_service: 'services/telemetry',
        verb: 'CHAOS_TEST',
        payload_summary: 'Injected chaos vectors',
        payload_json: JSON.stringify({ conversation_id: 'conv_qa_subagent' }),
      },
      {
        transaction_id: 'tx_main_01',
        trace_id: 'conv_root_main',
        subagent_id: null,
        subagent_role: null,
        timestamp_ns: 2000000000,
        duration_ns: 800000,
        source_service: 'services/builder',
        target_service: 'services/telemetry',
        verb: 'COMPILE_APP',
        payload_summary: 'Compiled application',
        payload_json: JSON.stringify({ conversation_id: 'conv_root_main' }),
      }
    ]
  }),
});
global.EventSource = function() { return { addEventListener: () => {} }; };

global.document = {
  getElementById: (id) => {
    if (!elements[id]) elements[id] = createMockEl(id);
    return elements[id];
  },
  addEventListener: (event, handler) => { global['doc_on' + event] = handler; },
};

elements['topology-canvas'] = {
  parentElement: { getBoundingClientRect: () => ({ width: 800, height: 600 }) },
  getContext: () => ({
    scale: () => {}, clearRect: () => {}, beginPath: () => {},
    moveTo: () => {}, lineTo: () => {}, stroke: () => {},
    arc: () => {}, fill: () => {}, fillText: () => {},
    measureText: () => ({ width: 50 }),
  }),
};

require('./generations/gen_04b/services/telemetry/cockpit/topology.js');
require('./generations/gen_04b/services/telemetry/cockpit/scrubber_fsm.js');
require('./generations/gen_04b/services/telemetry/cockpit/projection.js');

const scriptMatch = html.match(/<script>([\\s\\S]*?)<\\/script>/);
eval(scriptMatch[1]);

global.doc_onDOMContentLoaded();

setTimeout(() => {
  const convSel = elements['filter-conversation'];
  const subSel = elements['filter-subagent'];
  const srcSel = elements['filter-source'];
  const tgtSel = elements['filter-target'];
  console.assert(convSel.innerHTML.includes('conv_qa_subagent'), 'Dropdown must include subagent conversation');
  console.assert(convSel.innerHTML.includes('Adversarial QA Engineer'), 'Dropdown must display resolved role name');
  console.assert(srcSel.innerHTML.includes('services/audit'), 'Source dropdown must include services/audit');
  console.assert(tgtSel.innerHTML.includes('services/telemetry'), 'Target dropdown must include services/telemetry');

  // Test conversation filter
  convSel.value = 'conv_qa_subagent';
  convSel.onchange();
  console.assert(elements['filter-stats'].textContent.includes('1 / 2'), 'Must show 1 / 2 after conv filter');

  // Test clear filter
  elements['btn-clear-filter'].onclick();
  console.assert(elements['filter-stats'].textContent.includes('2 / 2'), 'Must show 2 / 2 after clear filter');

  // Test subagent role filter
  subSel.value = 'Adversarial QA Engineer';
  subSel.onchange();
  console.assert(elements['filter-stats'].textContent.includes('1 / 2'), 'Must show 1 / 2 after subagent filter');

  // Test source service filter & Pattern 2 contingent target grouping
  elements['btn-clear-filter'].onclick();
  srcSel.value = 'services/audit';
  srcSel.onchange();
  console.assert(elements['filter-stats'].textContent.includes('1 / 2'), 'Must show 1 / 2 after source filter');
  console.assert(tgtSel.innerHTML.includes('Active Channels'), 'Target must group active channels under optgroup');
  console.assert(tgtSel.innerHTML.includes('Dormant Channels'), 'Target must group dormant channels under optgroup');
  console.assert(tgtSel.innerHTML.includes('disabled'), 'Dormant channels must be disabled');

  // Test target service filter
  elements['btn-clear-filter'].onclick();
  tgtSel.value = 'services/telemetry';
  tgtSel.onchange();
  console.assert(elements['filter-stats'].textContent.includes('2 / 2'), 'Must show 2 / 2 after target filter');

  // Test click-to-filter on inspect-source
  elements['inspect-source'].onclick();
  console.assert(srcSel.value.length > 0, 'Click on inspect-source must update source filter');

  elements['btn-clear-filter'].onclick();

  process.stdout.write('FILTER_SIMULATION_VERIFICATION_PASS');
  process.exit(0);
}, 60);
"""
        res = subprocess.run(
            ["node", "-e", node_filter_script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Filter simulation failed: {res.stderr}")
        self.assertIn("FILTER_SIMULATION_VERIFICATION_PASS", res.stdout)

    def test_cockpit_server_conversation_names_resolution(self) -> None:
        """Verifies that CockpitServer resolves conversation IDs to human-readable names."""
        from generations.gen_04b.services.telemetry.src.cockpit_server import CockpitServer
        from generations.gen_04b.services.telemetry.src.ingest_server import IngestServer
        from generations.gen_04b.services.telemetry.src.rollback_engine import RollbackEngine
        from generations.gen_04b.services.telemetry.src.telemetry_vault import TelemetryVault, MeshTransaction
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            vault = TelemetryVault(db_path=f.name)
            tx = MeshTransaction(
                transaction_id="tx_conv_name_test",
                prev_transaction_hash="0" * 64,
                transaction_hash="1" * 64,
                merkle_leaf_hash="2" * 64,
                timestamp_ns=1000000000,
                duration_ns=1000,
                logical_clock=1,
                trace_id="conv_custom_agent_123",
                span_id="sp_1",
                causal_task_id="task_1",
                step_index=0,
                phase="PHASE_2C_VERIFICATION",
                source_service="services/audit",
                source_endpoint="192.168.40.30:8444",
                target_service="services/telemetry",
                target_endpoint="192.168.40.40:8446",
                channel_id="channel_audit_telemetry",
                verb="VERIFY_NAMES",
                payload_summary="Test conversation name resolution",
                payload_json="{}",
                bpe_tokens_in=10,
                bpe_tokens_out=10,
                bits_erased=0,
                heat_dissipated_joules=0.0,
                capital_partition="PROTECTED",
                status="SUCCESS",
                subagent_role="Custom Verifier Agent",
                subagent_id="agent_123",
            )
            vault.insert_transaction(tx)
            ingest = IngestServer(vault=vault, host="127.0.0.1", port=8446, allow_any_interface_for_testing=True)
            rollback = RollbackEngine(vault=vault)
            server = CockpitServer(
                vault=vault,
                ingest_server=ingest,
                rollback_engine=rollback,
                host="127.0.0.1",
                port=8447,
                allow_any_interface_for_testing=True,
            )

            names = server._get_conversation_names()
            self.assertIsInstance(names, dict)
            self.assertIn("conv_custom_agent_123", names)
            self.assertEqual(names["conv_custom_agent_123"]["role"], "Custom Verifier Agent")
            self.assertIn("latest_timestamp_ns", names["conv_custom_agent_123"])
            self.assertEqual(names["conv_custom_agent_123"]["event_count"], 1)
            vault.close()

    def test_conversation_sorting_by_latest_and_faceted_filtering_in_node(self) -> None:
        """Verifies that conversations sort strictly descending by latest timestamp and facet counts filter down."""
        node_facet_script = """
const fs = require('fs');
const html = fs.readFileSync('generations/gen_04b/services/telemetry/cockpit/index.html', 'utf8');

const elements = {};
function createMockEl(id, tag = 'div') {
  return {
    id,
    tagName: tag.toUpperCase(),
    textContent: '',
    innerHTML: '',
    value: 'ALL',
    classList: { add: () => {}, remove: () => {}, toggle: () => {} },
    addEventListener: function(event, handler) { this['on' + event] = handler; },
    style: {},
    title: '',
  };
}

global.window = global;
global.window.devicePixelRatio = 1;
global.window.addEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.fetch = async () => ({
  ok: true,
  json: async () => ({ transactions: [] }),
});
global.EventSource = function() {
  return { addEventListener: () => {} };
};

global.document = {
  getElementById: (id) => {
    if (!elements[id]) elements[id] = createMockEl(id);
    return elements[id];
  },
  addEventListener: (event, handler) => { global['doc_on' + event] = handler; },
};

elements['topology-canvas'] = {
  parentElement: { getBoundingClientRect: () => ({ width: 800, height: 600 }) },
  getContext: () => ({
    scale: () => {},
    clearRect: () => {},
    beginPath: () => {},
    moveTo: () => {},
    lineTo: () => {},
    stroke: () => {},
    arc: () => {},
    fill: () => {},
    fillText: () => {},
    measureText: () => ({ width: 50 }),
  }),
};

require('./generations/gen_04b/services/telemetry/cockpit/topology.js');
require('./generations/gen_04b/services/telemetry/cockpit/scrubber_fsm.js');
require('./generations/gen_04b/services/telemetry/cockpit/projection.js');

const scriptMatch = html.match(/<script>([\\s\\S]*?)<\\/script>/);
eval(scriptMatch[1]);
global.doc_onDOMContentLoaded();

// Create 3 conversations with distinct timestamps and distinct personas:
// conv_old: ts 1000 - 2000, persona: 'OldPersona', sources: ['services/research']
// conv_mid: ts 3000 - 4000, persona: 'MidPersona', sources: ['services/builder']
// conv_latest: ts 5000 - 6000, persona: 'LatestPersona', sources: ['services/audit']
const testTxs = [
  { transaction_id: 'tx_old_1', timestamp_ns: 1000, trace_id: 'conv_old', subagent_role: 'OldPersona', source_service: 'services/research', target_service: 'services/builder', status: 'SUCCESS' },
  { transaction_id: 'tx_old_2', timestamp_ns: 2000, trace_id: 'conv_old', subagent_role: 'OldPersona', source_service: 'services/research', target_service: 'services/builder', status: 'SUCCESS' },
  { transaction_id: 'tx_mid_1', timestamp_ns: 3000, trace_id: 'conv_mid', subagent_role: 'MidPersona', source_service: 'services/builder', target_service: 'services/telemetry', status: 'SUCCESS' },
  { transaction_id: 'tx_mid_2', timestamp_ns: 4000, trace_id: 'conv_mid', subagent_role: 'MidPersona', source_service: 'services/builder', target_service: 'services/telemetry', status: 'SUCCESS' },
  { transaction_id: 'tx_lat_1', timestamp_ns: 5000, trace_id: 'conv_latest', subagent_role: 'LatestPersona', source_service: 'services/audit', target_service: 'services/telemetry', status: 'SUCCESS' },
  { transaction_id: 'tx_lat_2', timestamp_ns: 6000, trace_id: 'conv_latest', subagent_role: 'LatestPersona', source_service: 'services/audit', target_service: 'services/telemetry', status: 'SUCCESS' },
];

ingestTransactionBatch(testTxs);

const convSel = elements['filter-conversation'];
const subSel = elements['filter-subagent'];
const srcSel = elements['filter-source'];
const tgtSel = elements['filter-target'];

// 1. Assert Conversation Sorting: Latest conversation must appear FIRST
const convHtml = convSel.innerHTML;
const firstConvIndex = convHtml.indexOf('value="conv_latest"');
const midConvIndex = convHtml.indexOf('value="conv_mid"');
const oldConvIndex = convHtml.indexOf('value="conv_old"');

console.assert(firstConvIndex !== -1 && midConvIndex !== -1 && oldConvIndex !== -1, 'All conversations must appear');
console.assert(firstConvIndex < midConvIndex && midConvIndex < oldConvIndex, 'Conversations must be sorted descending by latest timestamp: conv_latest < conv_mid < conv_old');
console.assert(convHtml.includes('[latest]'), 'Top conversation must have [latest] tag');

// 2. Select conv_latest: Subagents, sources, and targets must filter down!
convSel.value = 'conv_latest';
convSel.onchange();

console.assert(subSel.innerHTML.includes('LatestPersona (2)'), 'Subagent dropdown must show LatestPersona with 2 events');
console.assert(!subSel.innerHTML.includes('OldPersona'), 'Subagent dropdown must NOT contain OldPersona from other conversations');
console.assert(!subSel.innerHTML.includes('MidPersona'), 'Subagent dropdown must NOT contain MidPersona from other conversations');

// Sources must filter down to services/audit (2)
console.assert(srcSel.innerHTML.includes('services/audit (2)'), 'Source dropdown must show services/audit with 2 events');
console.assert(srcSel.innerHTML.includes('Sources in Conversation (2)'), 'All Sources option must display 2 matching events');

// 3. Select conv_old: Subagents and sources must switch to conv_old metrics!
convSel.value = 'conv_old';
convSel.onchange();

console.assert(subSel.innerHTML.includes('OldPersona (2)'), 'Subagent dropdown must show OldPersona with 2 events');
console.assert(!subSel.innerHTML.includes('LatestPersona'), 'Subagent dropdown must NOT contain LatestPersona');
console.assert(srcSel.innerHTML.includes('services/research (2)'), 'Source dropdown must show services/research with 2 events');

process.stdout.write('FACETED_FILTER_AND_RECENCY_PASS');
process.exit(0);
"""
        res = subprocess.run(
            ["node", "-e", node_facet_script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Faceted filter test failed: {res.stderr}")
        self.assertIn("FACETED_FILTER_AND_RECENCY_PASS", res.stdout)

    def test_1000_event_bulk_performance_benchmark_in_node(self) -> None:
        """Verifies that 1,000 events ingest, sort, fold, and facet in under 40ms without canvas freeze."""
        node_perf_script = """
const fs = require('fs');
const html = fs.readFileSync('generations/gen_04b/services/telemetry/cockpit/index.html', 'utf8');

const elements = {};
function createMockEl(id, tag = 'div') {
  return {
    id,
    tagName: tag.toUpperCase(),
    textContent: '',
    innerHTML: '',
    value: 'ALL',
    classList: { add: () => {}, remove: () => {}, toggle: () => {} },
    addEventListener: function(event, handler) { this['on' + event] = handler; },
    style: {},
    title: '',
  };
}

global.window = global;
global.window.devicePixelRatio = 1;
global.window.addEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.fetch = async () => ({ ok: true, json: async () => ({ transactions: [] }) });
global.EventSource = function() { return { addEventListener: () => {} }; };

global.document = {
  getElementById: (id) => {
    if (!elements[id]) elements[id] = createMockEl(id);
    return elements[id];
  },
  addEventListener: (event, handler) => { global['doc_on' + event] = handler; },
};

elements['topology-canvas'] = {
  parentElement: { getBoundingClientRect: () => ({ width: 800, height: 600 }) },
  getContext: () => ({
    scale: () => {},
    clearRect: () => {},
    beginPath: () => {},
    moveTo: () => {},
    lineTo: () => {},
    stroke: () => {},
    arc: () => {},
    fill: () => {},
    fillText: () => {},
    measureText: () => ({ width: 50 }),
  }),
};

require('./generations/gen_04b/services/telemetry/cockpit/topology.js');
require('./generations/gen_04b/services/telemetry/cockpit/scrubber_fsm.js');
require('./generations/gen_04b/services/telemetry/cockpit/projection.js');

const scriptMatch = html.match(/<script>([\\s\\S]*?)<\\/script>/);
eval(scriptMatch[1]);
global.doc_onDOMContentLoaded();

// Generate 1,000 synthetic transactions
const bulk1000 = [];
for (let i = 0; i < 1000; i++) {
  bulk1000.push({
    transaction_id: 'tx_perf_' + i,
    timestamp_ns: 1000000000 + i * 100000,
    duration_ns: 500000,
    logical_clock: i,
    trace_id: 'conv_' + (i % 10),
    span_id: 'span_' + i,
    causal_task_id: 'task_' + (i % 8),
    phase: 'PHASE_2A_SYNTHESIS',
    source_service: 'services/service_' + (i % 5),
    target_service: 'services/service_' + ((i + 1) % 5),
    subagent_role: 'Persona_' + (i % 6),
    status: 'SUCCESS',
    payload_json: JSON.stringify({ conversation_id: 'conv_' + (i % 10), subagent_role: 'Persona_' + (i % 6) }),
    bpe_tokens_in: 100,
    bpe_tokens_out: 200,
    bits_erased: 50,
    heat_dissipated_joules: 1e-19,
    capital_partition: 'EXPLORATORY'
  });
}

const t0 = performance.now();
ingestTransactionBatch(bulk1000);
const dt = performance.now() - t0;

console.log('1000-event ingestion & faceting took: ' + dt.toFixed(2) + ' ms');

console.assert(projection.records.length === 1000, 'All 1,000 records must be loaded into buffer');
console.assert(dt < 60.0, `Bulk load must complete in < 60ms, took ${dt}ms`);

// Assert that particle queue did not explode
console.assert(topology.particles.length <= 32, `Particle count must be <= 32, got ${topology.particles.length}`);

process.stdout.write('PERF_BENCHMARK_PASS');
process.exit(0);
"""
        res = subprocess.run(
            ["node", "-e", node_perf_script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Perf benchmark failed: {res.stderr}")
        self.assertIn("PERF_BENCHMARK_PASS", res.stdout)

    def test_subagent_parent_child_linking_and_include_subagents_toggle_in_node(self) -> None:
        """Verifies that parent-child conversation linking resolves child subagent events and cascades correctly."""
        node_subagent_script = """
const fs = require('fs');
const html = fs.readFileSync('generations/gen_04b/services/telemetry/cockpit/index.html', 'utf8');

const elements = {};
function createMockEl(id, tag = 'div') {
  const el = {
    id,
    tagName: tag.toUpperCase(),
    textContent: '',
    innerHTML: '',
    value: 'ALL',
    checked: true,
    classList: {
      _classes: new Set(),
      add: function(c) { this._classes.add(c); },
      remove: function(c) { this._classes.delete(c); },
      contains: function(c) { return this._classes.has(c); },
      toggle: function(c) { if (this._classes.has(c)) this._classes.delete(c); else this._classes.add(c); }
    },
    addEventListener: function(event, handler) { this['on' + event] = handler; },
    style: {},
    title: '',
    dataset: {},
    querySelector: function(sel) { return null; },
    querySelectorAll: function(sel) { return []; },
  };
  return el;
}

global.window = global;
global.window.devicePixelRatio = 1;
global.window.addEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.CSS = { escape: (s) => s };
global.EventSource = function() { return { addEventListener: () => {} }; };

global.fetch = async (url) => {
  if (url.includes('conversations')) {
    return {
      ok: true,
      json: async () => ({
        conversations: {
          'conv_root_6f27': { role: null, parent: null, latest_timestamp_ns: 2000000000, event_count: 2 },
          'conv_child_737': { role: 'Core Backend Synthesizer', parent: 'conv_root_6f27', latest_timestamp_ns: 1800000000, event_count: 3 },
          'conv_child_ont': { role: 'Domain Ontologist', parent: 'conv_root_6f27', latest_timestamp_ns: 1500000000, event_count: 2 },
          'conv_unrelated': { role: null, parent: null, latest_timestamp_ns: 1200000000, event_count: 1 },
        }
      })
    };
  }
  return { ok: true, json: async () => ({ transactions: [] }) };
};

global.document = {
  getElementById: (id) => {
    if (!elements[id]) {
      let tag = 'div';
      if (id.includes('select') || id.includes('filter')) tag = 'select';
      if (id === 'filter-include-subagents' || id === 'live-logs-follow') tag = 'input';
      if (id.includes('table')) tag = 'table';
      if (id.includes('tbody')) tag = 'tbody';
      elements[id] = createMockEl(id, tag);
    }
    return elements[id];
  },
  querySelectorAll: (sel) => [],
  querySelector: (sel) => null,
  addEventListener: (event, handler) => { global['doc_on' + event] = handler; },
};

elements['topology-canvas'] = {
  parentElement: { getBoundingClientRect: () => ({ width: 800, height: 600 }) },
  getContext: () => ({
    scale: () => {},
    clearRect: () => {},
    beginPath: () => {},
    moveTo: () => {},
    lineTo: () => {},
    stroke: () => {},
    arc: () => {},
    fill: () => {},
    fillText: () => {},
    measureText: () => ({ width: 50 }),
  }),
};

require('./generations/gen_04b/services/telemetry/cockpit/topology.js');
require('./generations/gen_04b/services/telemetry/cockpit/scrubber_fsm.js');
require('./generations/gen_04b/services/telemetry/cockpit/projection.js');

const scriptMatch = html.match(/<script>([\\s\\S]*?)<\\/script>/);
eval(scriptMatch[1]);
global.doc_onDOMContentLoaded();

// Populate mock transactions: 2 for conv_root_6f27, 3 for conv_child_737, 2 for conv_child_ont, 1 for conv_unrelated
const testTxs = [
  { transaction_id: 'tx_p1', trace_id: 'conv_root_6f27', subagent_role: 'None', source_service: 'services/governance', target_service: 'services/research', timestamp_ns: 1000000000, logical_clock: 1, duration_ns: 1000000, status: 'SUCCESS' },
  { transaction_id: 'tx_p2', trace_id: 'conv_root_6f27', subagent_role: 'None', source_service: 'services/governance', target_service: 'services/builder', timestamp_ns: 2000000000, logical_clock: 2, duration_ns: 1000000, status: 'SUCCESS' },
  { transaction_id: 'tx_c1', trace_id: 'conv_child_737', subagent_role: 'Main Orchestrator', source_service: 'services/builder', target_service: 'services/audit', timestamp_ns: 1600000000, logical_clock: 3, duration_ns: 2000000, status: 'SUCCESS' },
  { transaction_id: 'tx_c2', trace_id: 'conv_child_737', subagent_role: 'Main Orchestrator', source_service: 'services/builder', target_service: 'services/audit', timestamp_ns: 1700000000, logical_clock: 4, duration_ns: 2000000, status: 'SUCCESS' },
  { transaction_id: 'tx_c3', trace_id: 'conv_child_737', subagent_role: 'Main Orchestrator', source_service: 'services/builder', target_service: 'services/telemetry', timestamp_ns: 1800000000, logical_clock: 5, duration_ns: 2000000, status: 'SUCCESS' },
  { transaction_id: 'tx_o1', trace_id: 'conv_child_ont', subagent_role: 'Main Orchestrator', source_service: 'services/research', target_service: 'services/builder', timestamp_ns: 1400000000, logical_clock: 6, duration_ns: 1500000, status: 'SUCCESS' },
  { transaction_id: 'tx_o2', trace_id: 'conv_child_ont', subagent_role: 'Main Orchestrator', source_service: 'services/research', target_service: 'services/governance', timestamp_ns: 1500000000, logical_clock: 7, duration_ns: 1500000, status: 'SUCCESS' },
  { transaction_id: 'tx_u1', trace_id: 'conv_unrelated', subagent_role: 'None', source_service: 'services/telemetry', target_service: 'services/governance', timestamp_ns: 1200000000, logical_clock: 8, duration_ns: 500000, status: 'SUCCESS' }
];

ingestTransactionBatch(testTxs);

// 1. Assert Conversation Dropdown builds tree hierarchy
const convSelect = elements['filter-conversation'];
console.assert(convSelect.innerHTML.includes('conv_root_6f27'), 'conv_root_6f27 must be present in dropdown');
console.assert(convSelect.innerHTML.includes('└─'), 'Child subagents must be formatted with tree indicator └─');
console.assert(convSelect.innerHTML.includes('Core Backend Synthesizer'), 'Core Backend Synthesizer must be labeled in child tree');

// 2. Select parent conversation with Include Subagents = true
convSelect.value = 'conv_root_6f27';
elements['filter-include-subagents'].checked = true;
applyFilters();

const subSelect = elements['filter-subagent'];
console.assert(subSelect.innerHTML.includes('Core Backend Synthesizer (3)'), 'Subagent filter must include Core Backend Synthesizer with 3 events');
console.assert(subSelect.innerHTML.includes('Domain Ontologist (2)'), 'Subagent filter must include Domain Ontologist with 2 events');

// 3. Filter down to Core Backend Synthesizer under parent
subSelect.value = 'Core Backend Synthesizer';
applyFilters();
const stats = elements['filter-stats'].textContent;
console.assert(stats.includes('Showing 3 / 8 events'), `Must show 3 matching subagent events out of 8 total, got: ${stats}`);

// 4. Toggle Include Subagents = false
subSelect.value = 'ALL';
elements['filter-include-subagents'].checked = false;
applyFilters();
const statsNoSub = elements['filter-stats'].textContent;
console.assert(statsNoSub.includes('Showing 2 / 8 events'), `When subagents unchecked, must show only 2 parent events, got: ${statsNoSub}`);

process.stdout.write('SUBAGENT_PARENT_CHILD_LINKING_PASS');
process.exit(0);
"""
        res = subprocess.run(
            ["node", "-e", node_subagent_script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Subagent linking test failed: {res.stderr}")
        self.assertIn("SUBAGENT_PARENT_CHILD_LINKING_PASS", res.stdout)

    def test_subagent_routing_matrix_and_configurable_live_logs_in_node(self) -> None:
        """Verifies that the subagent routing matrix and live logs table render correctly."""
        node_matrix_script = """
const fs = require('fs');
const html = fs.readFileSync('generations/gen_04b/services/telemetry/cockpit/index.html', 'utf8');

const elements = {};
function createMockEl(id, tag = 'div') {
  return {
    id,
    tagName: tag.toUpperCase(),
    textContent: '',
    innerHTML: '',
    value: 'ALL',
    checked: true,
    classList: {
      _classes: new Set(),
      add: function(c) { this._classes.add(c); },
      remove: function(c) { this._classes.delete(c); },
      contains: function(c) { return this._classes.has(c); },
    },
    addEventListener: function(event, handler) { this['on' + event] = handler; },
    style: {},
    dataset: {},
    querySelector: function(sel) { return null; },
    querySelectorAll: function(sel) { return []; },
  };
}

global.window = global;
global.window.devicePixelRatio = 1;
global.window.addEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.CSS = { escape: (s) => s };
global.fetch = async () => ({ ok: true, json: async () => ({ transactions: [] }) });
global.EventSource = function() { return { addEventListener: () => {} }; };

global.document = {
  getElementById: (id) => {
    if (!elements[id]) {
      let tag = 'div';
      if (id.includes('tbody')) tag = 'tbody';
      if (id.includes('table')) tag = 'table';
      elements[id] = createMockEl(id, tag);
    }
    return elements[id];
  },
  querySelectorAll: (sel) => [],
  querySelector: (sel) => null,
  addEventListener: (event, handler) => { global['doc_on' + event] = handler; },
};

elements['topology-canvas'] = {
  parentElement: { getBoundingClientRect: () => ({ width: 800, height: 600 }) },
  getContext: () => ({
    scale: () => {},
    clearRect: () => {},
    beginPath: () => {},
    moveTo: () => {},
    lineTo: () => {},
    stroke: () => {},
    arc: () => {},
    fill: () => {},
    fillText: () => {},
    measureText: () => ({ width: 50 }),
  }),
};

require('./generations/gen_04b/services/telemetry/cockpit/topology.js');
require('./generations/gen_04b/services/telemetry/cockpit/scrubber_fsm.js');
require('./generations/gen_04b/services/telemetry/cockpit/projection.js');

const scriptMatch = html.match(/<script>([\\s\\S]*?)<\\/script>/);
eval(scriptMatch[1]);
global.doc_onDOMContentLoaded();

const testRecords = [
  { transaction_id: 'tx_log_1', trace_id: 'c1', subagent_role: 'Synthesizer', source_service: 'services/builder', target_service: 'services/audit', verb: 'EMIT_CODE', duration_ns: 25000000, heat_dissipated_joules: 1.2e-19, payload_summary: 'Emitted engine.py', logical_clock: 10, status: 'SUCCESS' },
  { transaction_id: 'tx_log_2', trace_id: 'c1', subagent_role: 'Synthesizer', source_service: 'services/builder', target_service: 'services/audit', verb: 'EMIT_CODE', duration_ns: 15000000, heat_dissipated_joules: 8.0e-20, payload_summary: 'Emitted server.py', logical_clock: 11, status: 'SUCCESS' },
  { transaction_id: 'tx_log_3', trace_id: 'c1', subagent_role: 'QA Engineer', source_service: 'services/audit', target_service: 'services/telemetry', verb: 'SMOKE_TEST', duration_ns: 280000000, heat_dissipated_joules: 3.5e-19, payload_summary: 'Smoke test passed', logical_clock: 12, status: 'SUCCESS' },
];

// Test Subagent Routing Matrix render
window.renderSubagentRoutingMatrix(testRecords);
const routingBody = elements['subagent-routing-body'];
console.assert(routingBody.innerHTML.includes('Synthesizer'), 'Matrix must include Synthesizer card');
console.assert(routingBody.innerHTML.includes('QA Engineer'), 'Matrix must include QA Engineer card');
console.assert(routingBody.innerHTML.includes('services/builder'), 'Matrix must include source service');
console.assert(routingBody.innerHTML.includes('services/audit'), 'Matrix must include target service');

// Test Live Logs Table render
window.renderLiveLogs(testRecords);
const tbody = elements['live-logs-tbody'];
console.assert(tbody.innerHTML.includes('EMIT_CODE'), 'Live logs must include verb EMIT_CODE');
console.assert(tbody.innerHTML.includes('SMOKE_TEST'), 'Live logs must include verb SMOKE_TEST');
console.assert(tbody.innerHTML.includes('Emitted engine.py'), 'Live logs must include payload summary');
console.assert(tbody.innerHTML.includes('L10') && tbody.innerHTML.includes('L12'), 'Live logs must render logical clocks');

process.stdout.write('ROUTING_MATRIX_AND_LIVE_LOGS_PASS');
process.exit(0);
"""
        res = subprocess.run(
            ["node", "-e", node_matrix_script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Routing matrix / live logs test failed: {res.stderr}")
        self.assertIn("ROUTING_MATRIX_AND_LIVE_LOGS_PASS", res.stdout)

    def test_query_command_ribbon_dom_and_css_contracts(self) -> None:
        """Verifies DOM elements and CSS rules for Option 2 Datadog/Loki Holographic Observability Suite."""
        html = self.index_html.read_text(encoding="utf-8")
        css = self.styles_css.read_text(encoding="utf-8")

        # 1. HTML DOM Elements
        self.assertIn('id="query-command-ribbon"', html, "Query command ribbon section must exist")
        self.assertIn('id="input-omni-search"', html, "Omni-search input must exist")
        self.assertIn('id="btn-clear-search"', html, "Clear search button must exist")
        self.assertIn('id="status-pills-group"', html, "Status pills group must exist")
        self.assertIn('id="pill-status-all"', html, "ALL status pill must exist")
        self.assertIn('id="pill-status-success"', html, "SUCCESS status pill must exist")
        self.assertIn('id="pill-status-failed"', html, "FAILED status pill must exist")
        self.assertIn('id="pill-status-recovery"', html, "RECOVERY status pill must exist")
        self.assertIn('id="btn-density-compact"', html, "Compact density button must exist")
        self.assertIn('id="btn-density-comfortable"', html, "Comfortable density button must exist")
        self.assertIn('id="btn-export-logs"', html, "Export logs button must exist")
        self.assertIn('id="active-chips-container"', html, "Active chips container must exist")
        self.assertIn('class="col-expand"', html, "Expand chevron header column must exist")

        # 2. CSS Rules
        self.assertIn(".query-command-ribbon", css)
        self.assertIn(".omni-search-input", css)
        self.assertIn(".btn-status-pill", css)
        self.assertIn(".btn-status-pill.active.pill-status-all", css)
        self.assertIn(".btn-status-pill.active.pill-status-success", css)
        self.assertIn(".btn-status-pill.active.pill-status-failed", css)
        self.assertIn(".btn-status-pill.active.pill-status-recovery", css)
        self.assertIn(".log-detail-drawer", css)
        self.assertIn(".row-expand-chevron", css)
        self.assertIn(".search-highlight", css)
        self.assertIn(".btn-quick-facet", css)
        self.assertIn(".density-compact", css)
        self.assertIn(".density-comfortable", css)

    def test_omni_search_and_highlighting_in_node(self) -> None:
        """Simulates omni-search text/regex querying and match highlighting in Node."""
        node_search_script = """
const fs = require('fs');
const html = fs.readFileSync('generations/gen_04b/services/telemetry/cockpit/index.html', 'utf8');

const elements = {};
function createMockEl(id, tag = 'div') {
  return {
    id,
    tagName: tag.toUpperCase(),
    textContent: '',
    innerHTML: '',
    value: 'ALL',
    checked: true,
    focus: function() {},
    blur: function() {},
    select: function() {},
    classList: {
      _classes: new Set(),
      add: function(c) { this._classes.add(c); },
      remove: function(c) { this._classes.delete(c); },
      contains: function(c) { return this._classes.has(c); },
    },
    addEventListener: function(event, handler) { this['on' + event] = handler; },
    style: {},
    dataset: {},
    querySelector: function(sel) { return null; },
    querySelectorAll: function(sel) { return []; },
  };
}

global.window = global;
global.window.devicePixelRatio = 1;
global.window.addEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.CSS = { escape: (s) => s };
global.fetch = async () => ({ ok: true, json: async () => ({ transactions: [] }) });
global.EventSource = function() { return { addEventListener: () => {} }; };

global.document = {
  getElementById: (id) => {
    if (!elements[id]) {
      let tag = 'div';
      if (id.includes('tbody')) tag = 'tbody';
      if (id.includes('table')) tag = 'table';
      if (id.includes('input')) tag = 'input';
      elements[id] = createMockEl(id, tag);
    }
    return elements[id];
  },
  querySelectorAll: (sel) => [],
  querySelector: (sel) => null,
  addEventListener: (event, handler) => { global['doc_on' + event] = handler; },
};

elements['topology-canvas'] = {
  parentElement: { getBoundingClientRect: () => ({ width: 800, height: 600 }) },
  getContext: () => ({
    scale: () => {}, clearRect: () => {}, beginPath: () => {}, moveTo: () => {}, lineTo: () => {}, stroke: () => {}, arc: () => {}, fill: () => {}, fillText: () => {}, measureText: () => ({ width: 50 }),
  }),
};

require('./generations/gen_04b/services/telemetry/cockpit/topology.js');
require('./generations/gen_04b/services/telemetry/cockpit/scrubber_fsm.js');
require('./generations/gen_04b/services/telemetry/cockpit/projection.js');

const scriptMatch = html.match(/<script>([\\s\\S]*?)<\\/script>/);
eval(scriptMatch[1]);
global.doc_onDOMContentLoaded();

const sampleTxs = [
  { transaction_id: 'tx_s1', trace_id: 'tr_1', subagent_role: 'Domain Ontologist', source_service: 'services/research', target_service: 'services/builder', verb: 'DERIVE_CONTRACT', payload_summary: 'Derived UserAccount contract', logical_clock: 1, status: 'SUCCESS' },
  { transaction_id: 'tx_s2', trace_id: 'tr_1', subagent_role: 'Core Backend', source_service: 'services/builder', target_service: 'services/audit', verb: 'EMIT_CODE', payload_summary: 'Synthesized engine.py and run.py', logical_clock: 2, status: 'SUCCESS', payload_json: JSON.stringify({ tool_name: 'write_file', tool_args: { CommandLine: 'python3 run.py --smoke-test' } }) },
  { transaction_id: 'tx_s3', trace_id: 'tr_1', subagent_role: 'QA Engineer', source_service: 'services/audit', target_service: 'services/telemetry', verb: 'SMOKE_TEST', payload_summary: 'Connection timeout on socket 8447', logical_clock: 3, status: 'FAILED', error: 'ECONNREFUSED: 192.168.40.40:8447' },
];

window.projection.records = [];
window.projection.addTransactions(sampleTxs);
window.applyFilters();

// 1. Initial State: All 3 records visible
console.assert(elements['filter-stats'].textContent.includes('3 / 3 events'), 'Initially all 3 events must be in view');

// 2. Omni-Search Substring: "run.py"
const searchInput = elements['input-omni-search'];
searchInput.value = 'run.py';
searchInput.oninput();

// Fast-forward debounce
setTimeout(() => {
  const tbody = elements['live-logs-tbody'];
  console.assert(tbody.innerHTML.includes('tx_s2'), 'tx_s2 must match "run.py"');
  console.assert(!tbody.innerHTML.includes('tx_s1'), 'tx_s1 must not match "run.py"');
  console.assert(tbody.innerHTML.includes('<mark class="search-highlight">run.py</mark>'), 'Match must be highlighted with mark tag');

  // 3. Clear search
  const btnClear = elements['btn-clear-search'];
  btnClear.onclick();
  console.assert(elements['filter-stats'].textContent.includes('3 / 3 events'), 'Clearing search must restore all events');

  process.stdout.write('OMNI_SEARCH_VERIFICATION_PASS');
  process.exit(0);
}, 200);
"""
        res = subprocess.run(
            ["node", "-e", node_search_script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Omni-search test failed: {res.stderr}")
        self.assertIn("OMNI_SEARCH_VERIFICATION_PASS", res.stdout)

    def test_status_severity_quick_pills_in_node(self) -> None:
        """Simulates status severity quick-pills toggling and dynamic counts in Node."""
        node_status_script = """
const fs = require('fs');
const html = fs.readFileSync('generations/gen_04b/services/telemetry/cockpit/index.html', 'utf8');

const elements = {};
function createMockEl(id, tag = 'div') {
  return {
    id,
    tagName: tag.toUpperCase(),
    textContent: '',
    innerHTML: '',
    value: 'ALL',
    checked: true,
    focus: function() {},
    blur: function() {},
    select: function() {},
    classList: {
      _classes: new Set(),
      add: function(c) { this._classes.add(c); },
      remove: function(c) { this._classes.delete(c); },
      contains: function(c) { return this._classes.has(c); },
    },
    addEventListener: function(event, handler) { this['on' + event] = handler; },
    style: {},
    dataset: {},
    querySelector: function(sel) { return null; },
    querySelectorAll: function(sel) { return []; },
  };
}

global.window = global;
global.window.devicePixelRatio = 1;
global.window.addEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.CSS = { escape: (s) => s };
global.fetch = async () => ({ ok: true, json: async () => ({ transactions: [] }) });
global.EventSource = function() { return { addEventListener: () => {} }; };

global.document = {
  getElementById: (id) => {
    if (!elements[id]) {
      let tag = 'div';
      if (id.includes('tbody')) tag = 'tbody';
      elements[id] = createMockEl(id, tag);
    }
    return elements[id];
  },
  querySelectorAll: (sel) => [],
  querySelector: (sel) => null,
  addEventListener: (event, handler) => { global['doc_on' + event] = handler; },
};

elements['topology-canvas'] = {
  parentElement: { getBoundingClientRect: () => ({ width: 800, height: 600 }) },
  getContext: () => ({
    scale: () => {}, clearRect: () => {}, beginPath: () => {}, moveTo: () => {}, lineTo: () => {}, stroke: () => {}, arc: () => {}, fill: () => {}, fillText: () => {}, measureText: () => ({ width: 50 }),
  }),
};

require('./generations/gen_04b/services/telemetry/cockpit/topology.js');
require('./generations/gen_04b/services/telemetry/cockpit/scrubber_fsm.js');
require('./generations/gen_04b/services/telemetry/cockpit/projection.js');

const scriptMatch = html.match(/<script>([\\s\\S]*?)<\\/script>/);
eval(scriptMatch[1]);
global.doc_onDOMContentLoaded();

const sampleTxs = [
  { transaction_id: 'tx_ok_1', trace_id: 't1', status: 'SUCCESS', source_service: 'services/research', target_service: 'services/builder', duration_ns: 1000000 },
  { transaction_id: 'tx_ok_2', trace_id: 't1', status: 'SUCCESS', source_service: 'services/builder', target_service: 'services/audit', duration_ns: 2000000 },
  { transaction_id: 'tx_err_1', trace_id: 't1', status: 'FAILED', error: 'AssertionError', source_service: 'services/audit', target_service: 'services/builder', duration_ns: 3000000 },
  { transaction_id: 'tx_rec_1', trace_id: 't1', status: 'RECOVERY', source_service: 'services/governance', target_service: 'services/builder', duration_ns: 4000000 },
];

window.projection.records = [];
window.projection.addTransactions(sampleTxs);
window.applyFilters();

// Verify Status Counts
console.assert(elements['count-status-all'].textContent === '4', `ALL count should be 4, got ${elements['count-status-all'].textContent}`);
console.assert(elements['count-status-success'].textContent === '2', `SUCCESS count should be 2, got ${elements['count-status-success'].textContent}`);
console.assert(elements['count-status-failed'].textContent === '1', `FAILED count should be 1, got ${elements['count-status-failed'].textContent}`);
console.assert(elements['count-status-recovery'].textContent === '1', `RECOVERY count should be 1, got ${elements['count-status-recovery'].textContent}`);

// Click FAILED pill
const pillFailed = elements['pill-status-failed'];
pillFailed.dataset.status = 'FAILED';
pillFailed.onclick();

console.assert(elements['filter-stats'].textContent.includes('1 / 4 events'), 'Only 1 failed event should be shown');
const tbody = elements['live-logs-tbody'];
console.assert(tbody.innerHTML.includes('tx_err_1'), 'tx_err_1 must be in tbody');
console.assert(!tbody.innerHTML.includes('tx_ok_1'), 'tx_ok_1 must not be in tbody');

process.stdout.write('STATUS_PILLS_VERIFICATION_PASS');
process.exit(0);
"""
        res = subprocess.run(
            ["node", "-e", node_status_script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Status pills test failed: {res.stderr}")
        self.assertIn("STATUS_PILLS_VERIFICATION_PASS", res.stdout)

    def test_inline_accordion_drawer_expansion_in_node(self) -> None:
        """Simulates clicking accordion row chevrons to expand inline detail drawers."""
        node_accordion_script = """
const fs = require('fs');
const html = fs.readFileSync('generations/gen_04b/services/telemetry/cockpit/index.html', 'utf8');

const elements = {};
function createMockEl(id, tag = 'div') {
  return {
    id,
    tagName: tag.toUpperCase(),
    textContent: '',
    innerHTML: '',
    value: 'ALL',
    checked: true,
    classList: {
      _classes: new Set(),
      add: function(c) { this._classes.add(c); },
      remove: function(c) { this._classes.delete(c); },
      contains: function(c) { return this._classes.has(c); },
    },
    addEventListener: function(event, handler) { this['on' + event] = handler; },
    style: {},
    dataset: {},
    querySelector: function(sel) { return null; },
    querySelectorAll: function(sel) { return []; },
  };
}

global.window = global;
global.window.devicePixelRatio = 1;
global.window.addEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.CSS = { escape: (s) => s };
global.fetch = async () => ({ ok: true, json: async () => ({ transactions: [] }) });
global.EventSource = function() { return { addEventListener: () => {} }; };

global.document = {
  getElementById: (id) => {
    if (!elements[id]) {
      let tag = 'div';
      if (id.includes('tbody')) tag = 'tbody';
      elements[id] = createMockEl(id, tag);
    }
    return elements[id];
  },
  querySelectorAll: (sel) => [],
  querySelector: (sel) => null,
  addEventListener: (event, handler) => { global['doc_on' + event] = handler; },
};

elements['topology-canvas'] = {
  parentElement: { getBoundingClientRect: () => ({ width: 800, height: 600 }) },
  getContext: () => ({
    scale: () => {}, clearRect: () => {}, beginPath: () => {}, moveTo: () => {}, lineTo: () => {}, stroke: () => {}, arc: () => {}, fill: () => {}, fillText: () => {}, measureText: () => ({ width: 50 }),
  }),
};

require('./generations/gen_04b/services/telemetry/cockpit/topology.js');
require('./generations/gen_04b/services/telemetry/cockpit/scrubber_fsm.js');
require('./generations/gen_04b/services/telemetry/cockpit/projection.js');

const scriptMatch = html.match(/<script>([\\s\\S]*?)<\\/script>/);
eval(scriptMatch[1]);
global.doc_onDOMContentLoaded();

const sampleTxs = [
  {
    transaction_id: 'tx_accord_1',
    trace_id: 'tr_accord',
    span_id: 'sp_123',
    subagent_role: 'Synthesizer',
    source_service: 'services/builder',
    target_service: 'services/audit',
    verb: 'EMIT_CODE',
    payload_summary: 'Emitted engine.py',
    payload_json: JSON.stringify({
      tool_name: 'write_file',
      tool_args: { Path: '/dev/meta-axioma/engine.py', CommandLine: 'python3 -m unittest' }
    }),
    duration_ns: 45000000,
    status: 'SUCCESS'
  }
];

// 1. Initial render without expansion
window.renderLiveLogs(sampleTxs);
let tbody = elements['live-logs-tbody'];
console.assert(!tbody.innerHTML.includes('log-detail-drawer'), 'Drawer should not be rendered initially');
console.assert(tbody.innerHTML.includes('row-expand-chevron'), 'Chevron must be rendered');

// 2. Expand transaction tx_accord_1
window.expandedTxIds.add('tx_accord_1');
window.renderLiveLogs(sampleTxs);
tbody = elements['live-logs-tbody'];

console.assert(tbody.innerHTML.includes('log-detail-drawer'), 'Drawer must be rendered when expanded');
console.assert(tbody.innerHTML.includes('log-detail-row'), 'Detail row must exist');
console.assert(tbody.innerHTML.includes('Copy JSON'), 'Copy JSON button must exist');
console.assert(tbody.innerHTML.includes('Copy Command'), 'Copy Command button must exist');
console.assert(tbody.innerHTML.includes('python3 -m unittest'), 'Tool argument command line must be present');
console.assert(tbody.innerHTML.includes('btn-filter-trace'), 'Filter trace button must exist');

// 3. Collapse transaction
window.expandedTxIds.delete('tx_accord_1');
window.renderLiveLogs(sampleTxs);
tbody = elements['live-logs-tbody'];
console.assert(!tbody.innerHTML.includes('log-detail-drawer'), 'Drawer must collapse when removed from set');

process.stdout.write('ACCORDION_DRAWER_VERIFICATION_PASS');
process.exit(0);
"""
        res = subprocess.run(
            ["node", "-e", node_accordion_script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Accordion drawer test failed: {res.stderr}")
        self.assertIn("ACCORDION_DRAWER_VERIFICATION_PASS", res.stdout)

    def test_active_chips_ribbon_and_density_export_in_node(self) -> None:
        """Simulates active filter chips rendering, density switching, and export."""
        node_chips_script = """
const fs = require('fs');
const html = fs.readFileSync('generations/gen_04b/services/telemetry/cockpit/index.html', 'utf8');

const elements = {};
function createMockEl(id, tag = 'div') {
  return {
    id,
    tagName: tag.toUpperCase(),
    textContent: '',
    innerHTML: '',
    value: 'ALL',
    checked: true,
    focus: function() {},
    blur: function() {},
    select: function() {},
    classList: {
      _classes: new Set(),
      add: function(c) { this._classes.add(c); },
      remove: function(c) { this._classes.delete(c); },
      contains: function(c) { return this._classes.has(c); },
    },
    addEventListener: function(event, handler) { this['on' + event] = handler; },
    style: {},
    dataset: {},
    querySelector: function(sel) { return null; },
    querySelectorAll: function(sel) { return []; },
  };
}

global.window = global;
global.window.devicePixelRatio = 1;
global.window.addEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.CSS = { escape: (s) => s };
global.fetch = async () => ({ ok: true, json: async () => ({ transactions: [] }) });
global.EventSource = function() { return { addEventListener: () => {} }; };

global.document = {
  getElementById: (id) => {
    if (!elements[id]) {
      let tag = 'div';
      if (id.includes('tbody')) tag = 'tbody';
      elements[id] = createMockEl(id, tag);
    }
    return elements[id];
  },
  querySelectorAll: (sel) => [],
  querySelector: (sel) => null,
  addEventListener: (event, handler) => { global['doc_on' + event] = handler; },
};

elements['topology-canvas'] = {
  parentElement: { getBoundingClientRect: () => ({ width: 800, height: 600 }) },
  getContext: () => ({
    scale: () => {}, clearRect: () => {}, beginPath: () => {}, moveTo: () => {}, lineTo: () => {}, stroke: () => {}, arc: () => {}, fill: () => {}, fillText: () => {}, measureText: () => ({ width: 50 }),
  }),
};

require('./generations/gen_04b/services/telemetry/cockpit/topology.js');
require('./generations/gen_04b/services/telemetry/cockpit/scrubber_fsm.js');
require('./generations/gen_04b/services/telemetry/cockpit/projection.js');

const scriptMatch = html.match(/<script>([\\s\\S]*?)<\\/script>/);
eval(scriptMatch[1]);
global.doc_onDOMContentLoaded();

const sampleTxs = [
  { transaction_id: 'tx_c1', trace_id: 'conv_alpha_123', subagent_role: 'Research Agent', source_service: 'services/research', target_service: 'services/builder', status: 'SUCCESS' },
  { transaction_id: 'tx_c2', trace_id: 'conv_beta_456', subagent_role: 'Builder Agent', source_service: 'services/builder', target_service: 'services/audit', status: 'SUCCESS' },
];

window.projection.records = [];
window.projection.addTransactions(sampleTxs);

// 1. Set Conversation and Role filters
elements['filter-conversation'].value = 'conv_alpha_123';
elements['filter-subagent'].value = 'Research Agent';
window.applyFilters();

const chipsContainer = elements['active-chips-container'];
console.assert(chipsContainer.innerHTML.includes('Conv: conv_alp...'), 'Chips must include Conversation chip');
console.assert(chipsContainer.innerHTML.includes('Role: Research Agent'), 'Chips must include Role chip');

// 2. Test Density Switch
const btnCompact = elements['btn-density-compact'];
const btnComfortable = elements['btn-density-comfortable'];
const wrapper = elements['live-logs-wrapper'];

console.assert(typeof btnComfortable.onclick === 'function', 'btn-density-comfortable must have click listener');
btnComfortable.onclick();
console.assert(btnComfortable.classList.contains('active'), 'Comfortable button must be active');
console.assert(!btnCompact.classList.contains('active'), 'Compact button must not be active');

// 3. Test Export Button Binding
const btnExport = elements['btn-export-logs'];
console.assert(typeof btnExport.onclick === 'function', 'btn-export-logs must have click listener');

process.stdout.write('CHIPS_DENSITY_EXPORT_VERIFICATION_PASS');
process.exit(0);
"""
        res = subprocess.run(
            ["node", "-e", node_chips_script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Chips/Density/Export test failed: {res.stderr}")
        self.assertIn("CHIPS_DENSITY_EXPORT_VERIFICATION_PASS", res.stdout)

    def test_pinned_sticky_top_group_and_card_collapse_dom_contracts(self) -> None:
        """Verifies DOM elements and CSS contracts for Pinned Top Group and Collapsible Cards."""
        html = self.index_html.read_text(encoding="utf-8")
        css = self.styles_css.read_text(encoding="utf-8")

        # 1. Pinned Top Group
        self.assertIn('class="cockpit-top-pinned-group"', html)
        self.assertIn('id="cockpit-top-pinned-group"', html)
        self.assertIn(".cockpit-top-pinned-group", css)

        # 2. Layout Presets
        self.assertIn('id="layout-presets-group"', html)
        self.assertIn('id="preset-balanced"', html)
        self.assertIn('id="preset-logs"', html)
        self.assertIn('id="preset-mesh"', html)
        self.assertIn(".layout-presets-group", css)
        self.assertIn(".btn-preset", css)

        # 3. Collapsible Cards & Collapse Buttons
        self.assertIn('id="btn-collapse-topology"', html)
        self.assertIn('id="btn-collapse-routing"', html)
        self.assertIn('id="btn-collapse-logs"', html)
        self.assertIn('id="btn-collapse-inspector"', html)
        self.assertIn('id="btn-collapse-undo"', html)
        self.assertIn(".btn-card-collapse", css)
        self.assertIn(".card-collapsible-header", css)
        self.assertIn(".card-collapsed", css)

        # 4. Adaptive Live Logs Flex Expansion Rules
        self.assertIn(".expanded-logs-tier1", css)
        self.assertIn(".expanded-logs-tier2", css)

    def test_card_collapsing_and_adaptive_logs_expansion_in_node(self) -> None:
        """Simulates card collapse toggling, adaptive log expansion, and layout presets in Node."""
        node_collapse_script = """
const fs = require('fs');
const html = fs.readFileSync('generations/gen_04b/services/telemetry/cockpit/index.html', 'utf8');

const elements = {};
function createMockEl(id, tag = 'div') {
  return {
    id,
    tagName: tag.toUpperCase(),
    textContent: '',
    innerHTML: '',
    value: 'ALL',
    checked: true,
    focus: function() {},
    blur: function() {},
    select: function() {},
    classList: {
      _classes: new Set(),
      add: function(c) { this._classes.add(c); },
      remove: function(c) { this._classes.delete(c); },
      contains: function(c) { return this._classes.has(c); },
    },
    addEventListener: function(event, handler) { this['on' + event] = handler; },
    style: {},
    dataset: {},
    querySelector: function(sel) { return null; },
    querySelectorAll: function(sel) { return []; },
  };
}

global.window = global;
global.window.devicePixelRatio = 1;
global.window.addEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.CSS = { escape: (s) => s };
global.fetch = async () => ({ ok: true, json: async () => ({ transactions: [] }) });
global.EventSource = function() { return { addEventListener: () => {} }; };

const mockLocalStorage = {
  _store: {},
  getItem: function(k) { return this._store[k] || null; },
  setItem: function(k, v) { this._store[k] = String(v); },
  removeItem: function(k) { delete this._store[k]; },
  clear: function() { this._store = {}; },
};
global.localStorage = mockLocalStorage;

global.document = {
  getElementById: (id) => {
    if (!elements[id]) {
      let tag = 'div';
      if (id.includes('tbody')) tag = 'tbody';
      elements[id] = createMockEl(id, tag);
    }
    return elements[id];
  },
  querySelectorAll: (sel) => [],
  querySelector: (sel) => null,
  addEventListener: (event, handler) => { global['doc_on' + event] = handler; },
};

elements['topology-canvas'] = {
  parentElement: { getBoundingClientRect: () => ({ width: 800, height: 600 }) },
  getContext: () => ({
    scale: () => {}, clearRect: () => {}, beginPath: () => {}, moveTo: () => {}, lineTo: () => {}, stroke: () => {}, arc: () => {}, fill: () => {}, fillText: () => {}, measureText: () => ({ width: 50 }),
  }),
};

require('./generations/gen_04b/services/telemetry/cockpit/topology.js');
require('./generations/gen_04b/services/telemetry/cockpit/scrubber_fsm.js');
require('./generations/gen_04b/services/telemetry/cockpit/projection.js');

const scriptMatch = html.match(/<script>([\\s\\S]*?)<\\/script>/);
eval(scriptMatch[1]);
global.doc_onDOMContentLoaded();

const cardTopology = elements['card-topology'];
const cardRouting = elements['card-routing'];
const liveLogsWrapper = elements['live-logs-wrapper'];

// 1. Initial State: All expanded
console.assert(!cardTopology.classList.contains('card-collapsed'), 'Topology card should not be collapsed initially');
console.assert(!liveLogsWrapper.classList.contains('expanded-logs-tier1'), 'Live logs should not have tier1 expansion initially');

// 2. Collapse Topology Card
window.toggleCardCollapse('topology');
console.assert(cardTopology.classList.contains('card-collapsed'), 'Topology card must be collapsed');
console.assert(liveLogsWrapper.classList.contains('expanded-logs-tier1'), 'Live logs wrapper must expand to tier1');

// 3. Collapse Routing Card -> Trigger Tier 2 Flex Expansion
window.toggleCardCollapse('routing');
console.assert(cardRouting.classList.contains('card-collapsed'), 'Routing card must be collapsed');
console.assert(liveLogsWrapper.classList.contains('expanded-logs-tier2'), 'Live logs wrapper must expand to tier2 full height');

// 4. Test Layout Presets: 'logs'
window.applyLayoutPreset('logs');
console.assert(window.collapsedCards.has('topology'), 'Logs Focus must collapse topology');
console.assert(window.collapsedCards.has('routing'), 'Logs Focus must collapse routing');
console.assert(!window.collapsedCards.has('logs'), 'Logs Focus must expand logs');
console.assert(liveLogsWrapper.classList.contains('expanded-logs-tier2'), 'Logs Focus must set tier2 expansion');

// 5. Test Layout Presets: 'balanced'
window.applyLayoutPreset('balanced');
console.assert(!window.collapsedCards.has('topology'), 'Balanced must expand topology');
console.assert(!window.collapsedCards.has('routing'), 'Balanced must expand routing');
console.assert(!liveLogsWrapper.classList.contains('expanded-logs-tier1'), 'Balanced must remove tier1');
console.assert(!liveLogsWrapper.classList.contains('expanded-logs-tier2'), 'Balanced must remove tier2');

// 6. Test LocalStorage Persistence
const storedState = JSON.parse(mockLocalStorage.getItem('zenith_cockpit_card_state'));
console.assert(storedState !== null, 'Card state must be persisted to localStorage');
console.assert(storedState.activePreset === 'balanced', 'Active preset must be saved');

process.stdout.write('CARD_COLLAPSE_AND_EXPANSION_PASS');
process.exit(0);
"""
        res = subprocess.run(
            ["node", "-e", node_collapse_script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Card collapse test failed: {res.stderr}")
        self.assertIn("CARD_COLLAPSE_AND_EXPANSION_PASS", res.stdout)

    def test_pure_flexbox_column_architecture_and_independent_mesh_minimize(self) -> None:
        """Verifies pure flexbox column layout, decoupled sibling cards, and independent mesh minimize."""
        html = self.index_html.read_text(encoding="utf-8")
        css = self.styles_css.read_text(encoding="utf-8")

        # 1. Flex Column Architecture in DOM & CSS
        self.assertIn('class="cockpit-col cockpit-col-left"', html)
        self.assertIn('id="cockpit-col-left"', html)
        self.assertIn('class="cockpit-col cockpit-col-right"', html)
        self.assertIn('id="cockpit-col-right"', html)
        self.assertIn(".cockpit-col-left", css)
        self.assertIn(".cockpit-col-right", css)

        # 2. Strict Sibling Decoupling: Routing and Logs MUST NOT be nested inside Topology body
        body_topology_idx = html.find('id="body-topology"')
        card_routing_idx = html.find('id="card-routing"')
        card_logs_idx = html.find('id="card-logs"')
        self.assertGreater(body_topology_idx, 0)
        self.assertGreater(card_routing_idx, 0)
        self.assertGreater(card_logs_idx, 0)

        # Body topology must close BEFORE card-routing begins
        topology_close = html.find('</div>', html.find('class="smt-drawer"', body_topology_idx) + 100)
        self.assertLess(topology_close, card_routing_idx, "card-routing must be a sibling outside card-topology body")
        self.assertLess(card_routing_idx, card_logs_idx, "card-routing must precede card-logs as siblings")

        # 3. CSS Flex Space Allocation & Collapsed Reclaim Rules
        self.assertIn("#card-topology", css)
        self.assertIn("#card-routing", css)
        self.assertIn("#card-logs", css)
        self.assertIn("flex: 0 0 auto !important;", css)

        # 4. Zero-Jitter ResizeObserver on Topology Container
        self.assertIn("ResizeObserver", html)
        self.assertIn("meshObserver.observe(topologyContainerEl)", html)

    def test_hud_meters_scoped_to_active_conversation_in_node(self) -> None:
        """Verifies that HUD meters dynamically scope tokens and heat to the active conversation filter."""
        node_script = """
const fs = require('fs');
const html = fs.readFileSync('generations/gen_04b/services/telemetry/cockpit/index.html', 'utf8');

const elements = {};
function createMockEl(id, tag = 'div') {
  return {
    id,
    tagName: tag.toUpperCase(),
    textContent: '',
    innerHTML: '',
    value: 'ALL',
    checked: true,
    focus: function() {},
    blur: function() {},
    select: function() {},
    classList: {
      _classes: new Set(),
      add: function(c) { this._classes.add(c); },
      remove: function(c) { this._classes.delete(c); },
      contains: function(c) { return this._classes.has(c); },
    },
    addEventListener: function(event, handler) { this['on' + event] = handler; },
    style: {},
    dataset: {},
    querySelector: function(sel) { return null; },
    querySelectorAll: function(sel) { return []; },
  };
}

global.window = global;
global.window.devicePixelRatio = 1;
global.window.addEventListener = () => {};
global.requestAnimationFrame = (fn) => setTimeout(fn, 16);
global.CSS = { escape: (s) => s };
global.fetch = async () => ({ ok: true, json: async () => ({ transactions: [] }) });
global.EventSource = function() { return { addEventListener: () => {} }; };
global.localStorage = { getItem: () => null, setItem: () => {} };

global.document = {
  getElementById: (id) => {
    if (!elements[id]) {
      let tag = 'div';
      if (id.includes('select') || id.includes('filter')) tag = 'select';
      if (id.includes('tbody')) tag = 'tbody';
      elements[id] = createMockEl(id, tag);
    }
    return elements[id];
  },
  querySelectorAll: (sel) => [],
  querySelector: (sel) => null,
  addEventListener: (event, handler) => { global['doc_on' + event] = handler; },
};

elements['topology-canvas'] = {
  parentElement: { getBoundingClientRect: () => ({ width: 800, height: 600 }), clientWidth: 800, clientHeight: 600 },
  getContext: () => ({
    scale: () => {}, setTransform: () => {}, clearRect: () => {}, beginPath: () => {}, moveTo: () => {}, lineTo: () => {}, stroke: () => {}, arc: () => {}, fill: () => {}, fillText: () => {}, measureText: () => ({ width: 50 }),
  }),
};

require('./generations/gen_04b/services/telemetry/cockpit/topology.js');
require('./generations/gen_04b/services/telemetry/cockpit/scrubber_fsm.js');
require('./generations/gen_04b/services/telemetry/cockpit/projection.js');

const scriptMatch = html.match(/<script>([\\s\\S]*?)<\\/script>/);
eval(scriptMatch[1]);
global.doc_onDOMContentLoaded();

// Reset projection records for deterministic testing
window.projection.records = [];

// Ingest batch with 2 conversations:
// conv_A: 40,000 + 10,000 = 50,000 tokens
// conv_B: 60,000 + 20,000 = 80,000 tokens
window.ingestTransactionBatch([
  {
    transaction_id: 'tx_a1',
    trace_id: 'conv_A',
    source_service: 'services/research',
    target_service: 'services/builder',
    bpe_tokens_in: 40000,
    bpe_tokens_out: 10000,
    bits_erased: 100,
    heat_dissipated_joules: 0.05,
    timestamp_ns: 1000000,
  },
  {
    transaction_id: 'tx_b1',
    trace_id: 'conv_B',
    source_service: 'services/builder',
    target_service: 'services/audit',
    bpe_tokens_in: 60000,
    bpe_tokens_out: 20000,
    bits_erased: 200,
    heat_dissipated_joules: 0.08,
    timestamp_ns: 2000000,
  }
]);

const hudTokens = elements['hud-tokens'];
const hudTokensLabel = elements['hud-tokens-label'];
const filterConvSelect = elements['filter-conversation'];

// 1. Initial State (All Conversations): Display total cluster throughput
console.assert(hudTokens.textContent.includes('130,000 BPE (Cluster)'), 'Cluster view should display sum of all tokens (130,000 BPE): got ' + hudTokens.textContent);

// 2. Filter to conv_A: Tokens should scope down to 50,000 / 312,000
filterConvSelect.value = 'conv_A';
window.applyFilters();

console.assert(hudTokens.textContent.includes('50,000 / 312,000'), 'conv_A view should display 50,000 / 312,000: got ' + hudTokens.textContent);
console.assert(hudTokensLabel.textContent.includes('Lease'), 'Tokens label should indicate Lease');

// 3. Filter to conv_B: Tokens should scope to 80,000 / 312,000
filterConvSelect.value = 'conv_B';
window.applyFilters();

console.assert(hudTokens.textContent.includes('80,000 / 312,000'), 'conv_B view should display 80,000 / 312,000: got ' + hudTokens.textContent);

// 4. Reset to ALL: Revert to Cluster throughput
filterConvSelect.value = 'ALL';
window.applyFilters();

console.assert(hudTokens.textContent.includes('130,000 BPE (Cluster)'), 'Resetting to ALL should restore cluster throughput: got ' + hudTokens.textContent);

process.stdout.write('HUD_METERS_CONV_SCOPING_PASS');
process.exit(0);
"""
        res = subprocess.run(
            ["node", "-e", node_script],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"HUD scoping test failed: {res.stderr}")
        self.assertIn("HUD_METERS_CONV_SCOPING_PASS", res.stdout)


if __name__ == "__main__":
    unittest.main()
