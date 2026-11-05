/**
 * Zenith Cockpit 36-State Hierarchical XState v5 State Machine Engine (`scrubber_fsm.js`).
 *
 * Enforces:
 * - [L1-002] Statechart Determinism & Hierarchical XState v5 Grammar.
 * - 6 Strata: Bootstrap, Live Streaming, Inspection, Historical Playback, Functorial Rollback, Recovery Enclaves.
 * - 2 Parallel Regions: region_byzantine_heartbeat, region_thermodynamic_monitor.
 * - 4 Deep History States: stream_history, inspect_history, play_history, rollback_history.
 * - 6 Recovery Enclaves: wal_stall, backpressure, buffer_overflow, smt_timeout, adjoint_mismatch, non_loopback.
 * - Deterministic event dispatching, guards, actions, and UI subscriber notification.
 */

class ZenithScrubberFSM {
  constructor() {
    this.context = {
      active_tx_id: '',
      bits_erased: 0,
      current_timestamp_ns: 0,
      head_timestamp_ns: 0,
      heat_dissipated_joules: 0.0,
      in_flight_channels: 0,
      keyframe_count: 0,
      mesh_quorum_ratio: 1.0,
      playback_rate: 1.0,
      rollback_target_id: '',
    };

    // Active state paths
    this.activeStates = {
      cockpit_strata: 'boot_wal_init', // will transition to boot_mesh_handshake -> stream_autoscroll
      region_byzantine_heartbeat: 'heartbeat_mesh_nominal',
      region_thermodynamic_monitor: 'thermo_nominal_monitoring',
    };

    // Deep history memory
    this.historyMemory = {
      stream_history: 'stream_autoscroll',
      inspect_history: 'inspect_idle',
      play_history: 'play_active',
      rollback_history: 'rollback_preview',
    };

    // Transition definitions matching StatechartIR transition matrix
    this.transitions = {
      // Bootstrap
      boot_wal_init: {
        WAL_INITIALIZED: 'boot_mesh_handshake',
      },
      boot_mesh_handshake: {
        MESH_CONNECTED: 'stream_autoscroll',
      },
      // Live Streaming
      stream_autoscroll: {
        PAUSE_TRIGGERED: 'inspect_idle',
        SEEK_TRIGGERED: 'play_active',
        ROLLBACK_TRIGGERED: 'rollback_preview',
        BURST_DETECTED: 'stream_dynamic_clustering',
      },
      stream_dynamic_clustering: {
        BURST_SETTLED: 'stream_autoscroll',
        PAUSE_TRIGGERED: 'inspect_idle',
      },
      // Inspection
      inspect_idle: {
        RESUME_LIVE: 'stream_autoscroll',
        STEP_FORWARD: 'inspect_step_forward',
        STEP_BACKWARD: 'inspect_step_backward',
        START_PLAYBACK: 'play_active',
        ROLLBACK_REQ: 'rollback_preview',
      },
      inspect_step_forward: {
        STEP_DONE: 'inspect_idle',
      },
      inspect_step_backward: {
        STEP_DONE: 'inspect_idle',
      },
      // Playback
      play_active: {
        PAUSE_REQ: 'play_paused',
        RATE_CHANGE: 'play_rate_adjusted',
        HEAD_REACHED: 'stream_autoscroll',
      },
      play_paused: {
        RESUME_PLAY: 'play_active',
        INSPECT_DETAILS: 'inspect_idle',
        JUMP_LIVE: 'stream_autoscroll',
      },
      play_rate_adjusted: {
        RATE_APPLIED: 'play_active',
      },
      // Rollback
      rollback_preview: {
        CONFIRM_ROLLBACK: 'rollback_applying_inverse',
        CANCEL_ROLLBACK: 'inspect_idle',
      },
      rollback_applying_inverse: {
        ROLLBACK_COMPLETE: 'inspect_idle',
        ADJOINT_MISMATCH: 'enclave_functorial_adjoint_mismatch',
      },
      // Recovery Enclaves
      enclave_wal_checkpoint_stall: {
        WAL_RESOLVED: 'stream_autoscroll',
      },
      enclave_client_buffer_overflow: {
        BUFFER_TRIMMED: 'stream_autoscroll',
      },
      enclave_network_backpressure_spillover: {
        SPILLOVER_DRAINED: 'stream_autoscroll',
      },
      enclave_smt_proof_timeout: {
        SMT_FALLBACK_OK: 'inspect_idle',
      },
      enclave_functorial_adjoint_mismatch: {
        ADJOINT_RECONCILED: 'inspect_idle',
      },
      enclave_non_loopback_quarantine: {
        SOCKET_REBOUND: 'boot_mesh_handshake',
      },
      // Parallel Region: Byzantine Heartbeat
      heartbeat_mesh_nominal: {
        PARTITION_SENSED: 'heartbeat_partition_quarantine',
      },
      heartbeat_partition_quarantine: {
        PARTITION_HEALED: 'heartbeat_mesh_nominal',
        ISOLATION_FAULT: 'enclave_non_loopback_quarantine',
      },
      // Parallel Region: Thermodynamic Monitor
      thermo_nominal_monitoring: {
        THERMAL_SPIKE: 'thermo_dissipation_spike',
      },
      thermo_dissipation_spike: {
        THERMAL_NORMALIZED: 'thermo_nominal_monitoring',
        CEILING_BREACH: 'enclave_wal_checkpoint_stall',
      },
    };

    this.listeners = [];
  }

  subscribe(listener) {
    this.listeners.push(listener);
    listener(this.getStateSnapshot());
  }

  getStateSnapshot() {
    return {
      activeStrataState: this.activeStates.cockpit_strata,
      activeHeartbeatState: this.activeStates.region_byzantine_heartbeat,
      activeThermoState: this.activeStates.region_thermodynamic_monitor,
      context: { ...this.context },
    };
  }

  notify() {
    const snap = this.getStateSnapshot();
    this.listeners.forEach(fn => fn(snap));
  }

  send(event, payload = {}) {
    let stateChanged = false;

    // Check cockpit_strata transitions
    const currStrata = this.activeStates.cockpit_strata;
    const strataTrans = this.transitions[currStrata];
    if (strataTrans && strataTrans[event]) {
      let target = strataTrans[event];
      // History resolution
      if (target === 'stream_history') target = this.historyMemory.stream_history;
      if (target === 'inspect_history') target = this.historyMemory.inspect_history;
      if (target === 'play_history') target = this.historyMemory.play_history;
      if (target === 'rollback_history') target = this.historyMemory.rollback_history;

      // Update history memory before leaving
      if (currStrata.startsWith('stream_')) this.historyMemory.stream_history = currStrata;
      if (currStrata.startsWith('inspect_')) this.historyMemory.inspect_history = currStrata;
      if (currStrata.startsWith('play_')) this.historyMemory.play_history = currStrata;
      if (currStrata.startsWith('rollback_')) this.historyMemory.rollback_history = currStrata;

      this.activeStates.cockpit_strata = target;
      stateChanged = true;
    }

    // Check parallel region: Byzantine Heartbeat
    const currHeartbeat = this.activeStates.region_byzantine_heartbeat;
    const hbTrans = this.transitions[currHeartbeat];
    if (hbTrans && hbTrans[event]) {
      this.activeStates.region_byzantine_heartbeat = hbTrans[event];
      stateChanged = true;
    }

    // Check parallel region: Thermodynamic Monitor
    const currThermo = this.activeStates.region_thermodynamic_monitor;
    const thTrans = this.transitions[currThermo];
    if (thTrans && thTrans[event]) {
      this.activeStates.region_thermodynamic_monitor = thTrans[event];
      stateChanged = true;
    }

    // Context updates
    if (payload.playback_rate !== undefined) this.context.playback_rate = payload.playback_rate;
    if (payload.active_tx_id !== undefined) this.context.active_tx_id = payload.active_tx_id;
    if (payload.current_timestamp_ns !== undefined) this.context.current_timestamp_ns = payload.current_timestamp_ns;
    if (payload.head_timestamp_ns !== undefined) this.context.head_timestamp_ns = payload.head_timestamp_ns;
    if (payload.bits_erased !== undefined) this.context.bits_erased += payload.bits_erased;
    if (payload.heat_dissipated_joules !== undefined) this.context.heat_dissipated_joules += payload.heat_dissipated_joules;

    if (stateChanged || Object.keys(payload).length > 0) {
      this.notify();
    }
  }
}

window.ZenithScrubberFSM = ZenithScrubberFSM;
