"use client";

import React, { useState } from "react";

interface NodeItem {
  id: string;
  name: string;
  shortLabel: string;
  category: "client" | "api" | "pipeline" | "ai" | "db" | "external";
  isDirectOwnership: boolean;
  x: number;
  y: number;
  w: number;
  h: number;
  technology: string;
  role: string;
  description: string;
  metrics?: string[];
  connections: {
    upstream: string[];
    downstream: string[];
  };
}

interface EdgeItem {
  id: string;
  from: string;
  to: string;
  label?: string;
  pathD: string;
  isBidirectional?: boolean;
}

const NODES: Record<string, NodeItem> = {
  user: {
    id: "user",
    name: "End User (Customer)",
    shortLabel: "Customer",
    category: "client",
    isDirectOwnership: false,
    x: 35,
    y: 45,
    w: 145,
    h: 54,
    technology: "Web / Mobile Client",
    role: "External Traffic Ingress",
    description: "Enterprise SaaS customers interacting with the analytics platform.",
    connections: { upstream: [], downstream: ["dashboard"] },
  },
  dashboard: {
    id: "dashboard",
    name: "Customer Dashboard",
    shortLabel: "Dashboard UI",
    category: "client",
    isDirectOwnership: true,
    x: 235,
    y: 45,
    w: 155,
    h: 54,
    technology: "React / TypeScript",
    role: "Client Interface",
    description: "Reactive customer frontend for data exploration and reporting.",
    connections: { upstream: ["user"], downstream: ["dashboard_api"] },
  },
  dashboard_api: {
    id: "dashboard_api",
    name: "Dashboard API",
    shortLabel: "Dashboard API",
    category: "api",
    isDirectOwnership: true,
    x: 445,
    y: 45,
    w: 160,
    h: 54,
    technology: "Go (Golang) Microservice",
    role: "Core Application Gateway",
    description: "High-throughput API serving sub-50ms reads, mutations, and AI orchestrations.",
    metrics: ["Sub-50ms read latency", "Stateless horizontal scaling", "Connection pooling"],
    connections: { upstream: ["dashboard"], downstream: ["db", "ai_interactive", "etl_extract"] },
  },
  ai_interactive: {
    id: "ai_interactive",
    name: "Interactive AI Microservices",
    shortLabel: "Real-Time AI",
    category: "ai",
    isDirectOwnership: true,
    x: 445,
    y: 135,
    w: 160,
    h: 54,
    technology: "Go / Python Runtime",
    role: "Online AI Serving Engine",
    description: "Low-latency microservices powering customer queries and administrative AI features.",
    metrics: ["Real-time response SLA", "Circuit-broken endpoints"],
    connections: { upstream: ["dashboard_api", "admin_tool"], downstream: [] },
  },
  internal_user: {
    id: "internal_user",
    name: "Internal Operators & Admins",
    shortLabel: "Internal Ops",
    category: "client",
    isDirectOwnership: false,
    x: 35,
    y: 195,
    w: 145,
    h: 54,
    technology: "Internal Staff",
    role: "Operations & Governance",
    description: "Internal operations engineers, support specialists, and data admins.",
    connections: { upstream: [], downstream: ["admin_tool", "data_ops_dashboard"] },
  },
  admin_tool: {
    id: "admin_tool",
    name: "Administration Tool",
    shortLabel: "Admin Console",
    category: "api",
    isDirectOwnership: true,
    x: 235,
    y: 135,
    w: 155,
    h: 54,
    technology: "React / Go Internal Tool",
    role: "Tenant & System Governance",
    description: "Administrative console for tenant management, state overrides, and AI triage.",
    connections: { upstream: ["internal_user"], downstream: ["db", "ai_interactive", "ai_models"] },
  },
  data_ops_dashboard: {
    id: "data_ops_dashboard",
    name: "Data Ops Dashboard",
    shortLabel: "Data Ops UI",
    category: "client",
    isDirectOwnership: true,
    x: 235,
    y: 225,
    w: 155,
    h: 54,
    technology: "React / TypeScript",
    role: "Ingestion Monitoring",
    description: "Operator interface for ingestion health, failure queues, and schema auditing.",
    connections: { upstream: ["internal_user"], downstream: ["data_ops_api"] },
  },
  data_ops_api: {
    id: "data_ops_api",
    name: "Data Ops API",
    shortLabel: "Data Ops API",
    category: "api",
    isDirectOwnership: true,
    x: 445,
    y: 225,
    w: 160,
    h: 54,
    technology: "Go Microservice",
    role: "Data Governance API",
    description: "Operational backend managing pipeline reprocessing, quarantine, and migrations.",
    connections: { upstream: ["data_ops_dashboard"], downstream: ["db"] },
  },
  db: {
    id: "db",
    name: "Primary Database (PostgreSQL)",
    shortLabel: "PostgreSQL DB",
    category: "db",
    isDirectOwnership: true,
    x: 825,
    y: 100,
    w: 165,
    h: 75,
    technology: "PostgreSQL / Partition Matrix",
    role: "Central Relational Data Plane",
    description: "Scaled across 10M+ customer records with tenant partitioning and sub-50ms query times.",
    metrics: ["10M+ customer records", "Sub-50ms query latency", "Tenant table partitioning"],
    connections: { upstream: ["dashboard_api", "data_ops_api", "admin_tool", "etl_load", "ai_models"], downstream: [] },
  },
  ai_models: {
    id: "ai_models",
    name: "AI Model Microservices (ML Team)",
    shortLabel: "ML Model Services",
    category: "ai",
    isDirectOwnership: false,
    x: 665,
    y: 225,
    w: 160,
    h: 54,
    technology: "PyTorch / GPU Services",
    role: "Batch AI Extraction & Embeddings",
    description: "Deep learning models owned by the ML team, enriching data dispatched from the Go ETL mesh.",
    connections: { upstream: ["etl_transform", "admin_tool"], downstream: ["etl_transform", "db"] },
  },
  providers: {
    id: "providers",
    name: "Real-Time Data Providers",
    shortLabel: "Data Providers",
    category: "external",
    isDirectOwnership: false,
    x: 35,
    y: 395,
    w: 145,
    h: 54,
    technology: "External Webhooks / REST APIs",
    role: "Real-Time Stream Egress",
    description: "Third-party customer event streams, CRMs, and support systems firing webhooks.",
    connections: { upstream: [], downstream: ["webhook_service"] },
  },
  webhook_service: {
    id: "webhook_service",
    name: "Webhook Ingestion Service",
    shortLabel: "Webhook Ingest",
    category: "pipeline",
    isDirectOwnership: true,
    x: 235,
    y: 395,
    w: 155,
    h: 54,
    technology: "Go / High-Concurrency HTTP Ingress",
    role: "Real-Time Ingress Buffer",
    description: "Absorbs incoming bursty webhook traffic with token-bucket backpressure and sub-15ms acks.",
    metrics: ["Sub-15ms HTTP 200 acks", "Bursty spike absorption", "Token bucket rate limiting"],
    connections: { upstream: ["providers"], downstream: ["etl_extract"] },
  },
  cronjobs: {
    id: "cronjobs",
    name: "Data Provider Sync Cronjobs",
    shortLabel: "Sync Cronjobs",
    category: "pipeline",
    isDirectOwnership: true,
    x: 35,
    y: 495,
    w: 145,
    h: 54,
    technology: "K8s CronJobs / Go Runners",
    role: "Scheduled Batch Dispatcher",
    description: "Recurring batch pollers syncing external provider data into the pipeline.",
    connections: { upstream: [], downstream: ["etl_extract"] },
  },
  etl_extract: {
    id: "etl_extract",
    name: "ETL: Ingress Buffer & Queue",
    shortLabel: "RabbitMQ Buffer",
    category: "pipeline",
    isDirectOwnership: true,
    x: 445,
    y: 445,
    w: 160,
    h: 56,
    technology: "RabbitMQ / AMQP Broker",
    role: "Durable Ingestion Buffer",
    description: "Asynchronous durable message queues isolating storage from bursty ingestion spikes.",
    metrics: ["Durable tenant queues", "Zero payload loss under burst", "Dead-letter exchange (DLX) retries"],
    connections: { upstream: ["webhook_service", "cronjobs", "dashboard_api"], downstream: ["etl_transform"] },
  },
  etl_transform: {
    id: "etl_transform",
    name: "ETL: Go Normalization Mesh",
    shortLabel: "Go Worker Mesh",
    category: "pipeline",
    isDirectOwnership: true,
    x: 665,
    y: 445,
    w: 160,
    h: 56,
    technology: "Go Goroutine Pools",
    role: "Transformation & Dedup Core",
    description: "Concurrent worker pools performing schema validation, deduplication, and ML enrichment dispatch.",
    metrics: ["Goroutine worker pools", "Deduplication & validation", "Graceful backpressure"],
    connections: { upstream: ["etl_extract", "ai_models"], downstream: ["ai_models", "etl_load"] },
  },
  etl_load: {
    id: "etl_load",
    name: "ETL: Batched DB Loader",
    shortLabel: "Bulk DB Loader",
    category: "pipeline",
    isDirectOwnership: true,
    x: 855,
    y: 445,
    w: 140,
    h: 56,
    technology: "Go / Batch Transactions",
    role: "Bulk Persistence Engine",
    description: "High-throughput loader executing transactional batch writes to PostgreSQL partitions.",
    metrics: ["Scaled >10M records", "High-efficiency batch inserts", "Zero lock contention"],
    connections: { upstream: ["etl_transform"], downstream: ["db"] },
  },
};

const EDGES: EdgeItem[] = [
  { id: "e_user_dash", from: "user", to: "dashboard", label: "HTTPS", pathD: "M 180 72 L 235 72" },
  { id: "e_dash_api", from: "dashboard", to: "dashboard_api", label: "REST", pathD: "M 390 72 L 445 72" },
  { id: "e_api_ai", from: "dashboard_api", to: "ai_interactive", label: "gRPC", pathD: "M 525 99 L 525 135" },
  { id: "e_api_db", from: "dashboard_api", to: "db", label: "SQL Read/Write", pathD: "M 605 60 C 715 60, 750 120, 825 120" },
  { id: "e_api_queue", from: "dashboard_api", to: "etl_extract", label: "On-demand Sync", pathD: "M 525 99 C 525 220, 480 340, 480 445" },

  { id: "e_iuser_admin", from: "internal_user", to: "admin_tool", label: "Auth HTTPS", pathD: "M 180 210 C 205 210, 205 162, 235 162" },
  { id: "e_iuser_dataops", from: "internal_user", to: "data_ops_dashboard", label: "Auth HTTPS", pathD: "M 180 230 C 205 230, 205 252, 235 252" },

  { id: "e_admin_db", from: "admin_tool", to: "db", label: "Admin SQL", pathD: "M 390 150 C 550 150, 700 135, 825 135" },
  { id: "e_admin_ai", from: "admin_tool", to: "ai_interactive", label: "Prompt Eval", pathD: "M 390 162 L 445 162" },
  { id: "e_admin_ml", from: "admin_tool", to: "ai_models", label: "Model Triage", pathD: "M 390 175 C 500 175, 580 240, 665 240" },

  { id: "e_dataops_api", from: "data_ops_dashboard", to: "data_ops_api", label: "Internal REST", pathD: "M 390 252 L 445 252" },
  { id: "e_dataops_db", from: "data_ops_api", to: "db", label: "Maintenance SQL", pathD: "M 605 252 C 720 252, 750 160, 825 160" },

  { id: "e_prov_wh", from: "providers", to: "webhook_service", label: "Webhook Events", pathD: "M 180 422 L 235 422" },
  { id: "e_wh_queue", from: "webhook_service", to: "etl_extract", label: "AMQP Publish", pathD: "M 390 422 C 415 422, 415 460, 445 460" },
  { id: "e_cron_queue", from: "cronjobs", to: "etl_extract", label: "Batch Ingest", pathD: "M 180 522 C 310 522, 370 480, 445 480" },

  { id: "e_q_trans", from: "etl_extract", to: "etl_transform", label: "Worker Pull", pathD: "M 605 473 L 665 473" },
  { id: "e_trans_ml", from: "etl_transform", to: "ai_models", label: "Enrichment RPC", pathD: "M 745 445 L 745 279", isBidirectional: true },
  { id: "e_ml_db", from: "ai_models", to: "db", label: "Async Vectors", pathD: "M 825 240 C 860 240, 860 190, 860 175" },
  { id: "e_trans_load", from: "etl_transform", to: "etl_load", label: "Normalized Batches", pathD: "M 825 473 L 855 473" },
  { id: "e_load_db", from: "etl_load", to: "db", label: "Bulk Writes (10M+)", pathD: "M 925 445 C 925 350, 925 230, 925 175" },
];

export default function BeehiveArchitectureSlot() {
  const [selectedNodeId, setSelectedNodeId] = useState<string>("etl_transform");
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [activePreset, setActivePreset] = useState<"all" | "ingest" | "customer" | "ops">("all");
  const [viewMode, setViewMode] = useState<"visual" | "mermaid">("visual");

  const activeFocusId = hoveredNodeId || selectedNodeId;
  const selectedNode = NODES[activeFocusId] || NODES["etl_transform"];

  // Compute connected nodes and edges for high-visibility active trace
  const activeEdges = EDGES.filter((e) => {
    if (activePreset === "ingest") {
      return ["e_prov_wh", "e_wh_queue", "e_cron_queue", "e_q_trans", "e_trans_ml", "e_trans_load", "e_load_db"].includes(e.id);
    }
    if (activePreset === "customer") {
      return ["e_user_dash", "e_dash_api", "e_api_ai", "e_api_db"].includes(e.id);
    }
    if (activePreset === "ops") {
      return ["e_iuser_admin", "e_iuser_dataops", "e_admin_db", "e_admin_ai", "e_admin_ml", "e_dataops_api", "e_dataops_db"].includes(e.id);
    }
    return e.from === activeFocusId || e.to === activeFocusId;
  });

  const activeEdgeIds = new Set(activeEdges.map((e) => e.id));
  const connectedNodeIds = new Set<string>();

  if (activePreset !== "all") {
    activeEdges.forEach((e) => {
      connectedNodeIds.add(e.from);
      connectedNodeIds.add(e.to);
    });
  } else if (activeFocusId) {
    connectedNodeIds.add(activeFocusId);
    activeEdges.forEach((e) => {
      connectedNodeIds.add(e.from);
      connectedNodeIds.add(e.to);
    });
  }

  const mermaidSource = `flowchart TD
    %% 1. Access Plane
    U[End User / Customer] --> A[Dashboard - React]
    I[Internal User / Ops] --> H[Administration Tool]
    I --> D[Data Ops Dashboard]

    %% 2. Ingress & Triggers (Direct Ownership)
    R[Real-Time Data Providers] --> W[Webhook Ingestion Service]
    N[Data Sync Cronjobs] --> F_EXTRACT[ETL: RabbitMQ Queue Buffer]
    W --> F_EXTRACT

    %% 3. Core APIs & Real-Time AI (Direct Ownership)
    A --> B(Dashboard API - Go)
    D --> E[Data Ops API - Go]
    B --> J[Interactive AI Microservices]
    H --> J
    B --> F_EXTRACT

    %% 4. Exploded High-Throughput ETL Pipeline (Direct Ownership)
    subgraph ETL_Engine ["ETL Ingestion Pipeline (10M+ Records)"]
        F_EXTRACT --> F_TRANSFORM[ETL: Go Normalization Mesh]
        F_TRANSFORM --> F_LOAD[ETL: Batched Bulk DB Loader]
    end

    %% 5. Partner ML Team Boundary
    F_TRANSFORM <-->|Enrichment Handoff| G[AI Model Microservices - ML Team]
    H --> G

    %% 6. Central Database Layer (Direct Ownership)
    C[(PostgreSQL DB - 10M+ Records)]
    B --> C
    E --> C
    H --> C
    F_LOAD --> C
    G --> C

    classDef owned fill:#18181b,stroke:#10b981,stroke-width:2px,color:#f4f4f5;
    classDef external fill:#09090b,stroke:#71717a,stroke-width:1px,stroke-dasharray: 4 4,color:#a1a1aa;
    class B,E,H,W,F_EXTRACT,F_TRANSFORM,F_LOAD,J,C owned;
    class G,R,U,I external;`;

  return (
    <section id="beehive-architecture" className="py-14 border-b border-zinc-800/80 bg-zinc-950/60">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 mb-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">
              04 //
            </span>
            <h2 className="text-xl font-bold tracking-tight text-zinc-100 font-sans">
              Beehive AI: Overseen Systems Architecture
            </h2>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-emerald-950/60 border border-emerald-800/80 text-emerald-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              CORE SCOPE HIGHLIGHTED
            </span>
          </div>
        </div>

        <p className="text-sm text-zinc-400 mb-6 max-w-3xl font-sans leading-relaxed">
          Interactive architectural graph of the high-throughput platform at Beehive AI. Everything highlighted in emerald represents the direct domain of ownership—specifically architecting the high-throughput Go APIs, the exploded ETL ingestion pipeline, real-time webhook ingress, interactive AI microservices, and the PostgreSQL partition matrix scaling past 10 million records.
        </p>

        {/* Guided Flow Presets & View Controls */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4 p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs font-mono">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-zinc-500 mr-1 text-[11px] uppercase">Trace Flow:</span>
            <button
              onClick={() => { setActivePreset("all"); }}
              className={`px-2.5 py-1 rounded transition-colors ${
                activePreset === "all"
                  ? "bg-zinc-800 text-zinc-100 border border-zinc-700"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Interactive Hover
            </button>
            <button
              onClick={() => { setActivePreset("ingest"); setSelectedNodeId("etl_transform"); }}
              className={`px-2.5 py-1 rounded transition-colors ${
                activePreset === "ingest"
                  ? "bg-emerald-950/80 text-emerald-300 border border-emerald-700"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              ★ 10M+ ETL Ingestion Flow
            </button>
            <button
              onClick={() => { setActivePreset("customer"); setSelectedNodeId("dashboard_api"); }}
              className={`px-2.5 py-1 rounded transition-colors ${
                activePreset === "customer"
                  ? "bg-emerald-950/80 text-emerald-300 border border-emerald-700"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Customer Query Path
            </button>
            <button
              onClick={() => { setActivePreset("ops"); setSelectedNodeId("admin_tool"); }}
              className={`px-2.5 py-1 rounded transition-colors ${
                activePreset === "ops"
                  ? "bg-emerald-950/80 text-emerald-300 border border-emerald-700"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Ops & Governance Mesh
            </button>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setViewMode("visual")}
              className={`px-2.5 py-1 rounded transition-colors ${
                viewMode === "visual"
                  ? "bg-zinc-800 text-zinc-100 font-semibold"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              Interactive Map
            </button>
            <button
              onClick={() => setViewMode("mermaid")}
              className={`px-2.5 py-1 rounded transition-colors ${
                viewMode === "mermaid"
                  ? "bg-zinc-800 text-zinc-100 font-semibold"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              Mermaid Source
            </button>
          </div>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-4 px-3 py-2 mb-4 rounded bg-zinc-950 border border-zinc-800/80 text-[11px] font-mono text-zinc-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
            <span className="text-zinc-200 font-medium">Direct Domain of Ownership</span>
          </span>
          <span className="text-zinc-700">|</span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-amber-500/80 border border-amber-400/80"></span>
            <span className="text-zinc-300">Partner ML Team Domain</span>
          </span>
          <span className="text-zinc-700">|</span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-zinc-700 border border-dashed border-zinc-500"></span>
            <span className="text-zinc-400">Client / External Ingress</span>
          </span>
          <span className="text-zinc-500 ml-auto hidden md:inline">
            💡 Hover/Click nodes to trace live data vectors
          </span>
        </div>

        {/* Graph Container */}
        <div className="rounded-lg bg-zinc-950 border border-zinc-800 relative overflow-hidden shadow-2xl">
          {viewMode === "mermaid" ? (
            <div className="p-6 font-mono text-xs space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
                <span className="text-zinc-400 uppercase tracking-wider">
                  Raw Mermaid Architecture Specification
                </span>
                <span className="text-zinc-500 text-[11px]">
                  Renders in GitHub, Notion & Mermaid Live
                </span>
              </div>
              <pre className="p-4 rounded bg-zinc-900/90 text-zinc-300 border border-zinc-800 overflow-x-auto leading-relaxed">
                {mermaidSource}
              </pre>
            </div>
          ) : (
            <div className="p-3 sm:p-5 relative">
              {/* Subtle background tech grid */}
              <div className="absolute inset-0 tech-grid opacity-15 pointer-events-none"></div>

              {/* The SVG Architectural Canvas */}
              <div className="overflow-x-auto">
                <svg
                  viewBox="0 0 1020 620"
                  className="w-full min-w-[780px] h-auto select-none"
                  style={{ maxHeight: "680px" }}
                >
                  <defs>
                    {/* Normal Arrow Marker */}
                    <marker
                      id="arrow"
                      viewBox="0 0 10 10"
                      refX="8"
                      refY="5"
                      markerWidth="6"
                      markerHeight="6"
                      orient="auto-start-reverse"
                    >
                      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#52525b" />
                    </marker>

                    {/* Active Glowing Emerald Arrow Marker */}
                    <marker
                      id="arrow-active"
                      viewBox="0 0 10 10"
                      refX="8"
                      refY="5"
                      markerWidth="6"
                      markerHeight="6"
                      orient="auto-start-reverse"
                    >
                      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#10b981" />
                    </marker>

                    {/* Active Amber Marker */}
                    <marker
                      id="arrow-amber"
                      viewBox="0 0 10 10"
                      refX="8"
                      refY="5"
                      markerWidth="6"
                      markerHeight="6"
                      orient="auto-start-reverse"
                    >
                      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#f59e0b" />
                    </marker>

                    {/* Glowing Filter */}
                    <filter id="emerald-glow" x="-20%" y="-20%" width="140%" height="140%">
                      <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#10b981" floodOpacity="0.6" />
                    </filter>
                  </defs>

                  {/* Subgraph Boundary Enclosures */}
                  {/* 1. Core Go APIs Subgraph Enclosure */}
                  <g className="subgraph-apis">
                    <rect
                      x="430"
                      y="20"
                      width="190"
                      height="275"
                      rx="8"
                      fill="rgba(24, 24, 27, 0.4)"
                      stroke="#27272a"
                      strokeDasharray="4 4"
                    />
                    <text x="440" y="36" fill="#71717a" fontSize="10" fontFamily="monospace" fontWeight="600">
                      CORE GO APIS & REAL-TIME AI
                    </text>
                  </g>

                  {/* 2. High-Throughput ETL Ingestion Engine Subgraph */}
                  <g className="subgraph-etl">
                    <rect
                      x="220"
                      y="370"
                      width="785"
                      height="180"
                      rx="8"
                      fill="rgba(16, 185, 129, 0.03)"
                      stroke="rgba(16, 185, 129, 0.3)"
                      strokeDasharray="4 4"
                    />
                    <text x="232" y="386" fill="#10b981" fontSize="10" fontFamily="monospace" fontWeight="bold">
                      ★ HIGH-THROUGHPUT ETL INGESTION ENGINE (SCALED TO 10M+ RECORDS)
                    </text>
                  </g>

                  {/* 3. Partner ML Team Enclosure */}
                  <g className="subgraph-ml">
                    <rect
                      x="650"
                      y="205"
                      width="190"
                      height="90"
                      rx="8"
                      fill="rgba(245, 158, 11, 0.02)"
                      stroke="rgba(245, 158, 11, 0.3)"
                      strokeDasharray="3 3"
                    />
                    <text x="660" y="220" fill="#f59e0b" fontSize="9" fontFamily="monospace" fontWeight="600">
                      PARTNER DOMAIN: ML TEAM
                    </text>
                  </g>

                  {/* 4. Central Storage Enclosure */}
                  <g className="subgraph-storage">
                    <rect
                      x="810"
                      y="75"
                      width="195"
                      height="115"
                      rx="8"
                      fill="rgba(16, 185, 129, 0.03)"
                      stroke="rgba(16, 185, 129, 0.35)"
                    />
                    <text x="822" y="92" fill="#34d399" fontSize="10" fontFamily="monospace" fontWeight="bold">
                      CENTRAL STORAGE PLANE
                    </text>
                  </g>

                  {/* SVG Edges / Connector Paths */}
                  <g className="edges-layer">
                    {EDGES.map((edge) => {
                      const isActive = activeEdgeIds.has(edge.id);
                      const isDimmed = activeEdges.length > 0 && !isActive;

                      return (
                        <g key={edge.id} className="cursor-pointer">
                          {/* Wider invisible hit area */}
                          <path
                            d={edge.pathD}
                            fill="none"
                            stroke="transparent"
                            strokeWidth="12"
                            onMouseEnter={() => {
                              setSelectedNodeId(edge.from);
                            }}
                          />
                          {/* Visible Edge */}
                          <path
                            d={edge.pathD}
                            fill="none"
                            stroke={isActive ? "#10b981" : "#3f3f46"}
                            strokeWidth={isActive ? "2.5" : "1.25"}
                            strokeOpacity={isDimmed ? 0.15 : isActive ? 1 : 0.6}
                            markerEnd={isActive ? "url(#arrow-active)" : "url(#arrow)"}
                            className={isActive ? "active-flow-line transition-all duration-200" : "transition-all duration-200"}
                          />
                        </g>
                      );
                    })}
                  </g>

                  {/* SVG Nodes */}
                  <g className="nodes-layer">
                    {Object.values(NODES).map((node) => {
                      const isSelected = activeFocusId === node.id;
                      const isConnected = connectedNodeIds.has(node.id);
                      const isDimmed = activeEdges.length > 0 && !isConnected;

                      let borderColor = "#3f3f46";
                      let fillColor = "#18181b";
                      let textColor = "#e4e4e7";

                      if (node.isDirectOwnership) {
                        borderColor = isSelected ? "#34d399" : "#10b981";
                        fillColor = isSelected ? "#064e3b" : "#121b18";
                      } else if (node.category === "ai") {
                        borderColor = isSelected ? "#fbbf24" : "#f59e0b";
                        fillColor = isSelected ? "#451a03" : "#1a1510";
                      }

                      return (
                        <g
                          key={node.id}
                          transform={`translate(${node.x}, ${node.y})`}
                          onClick={() => setSelectedNodeId(node.id)}
                          onMouseEnter={() => setHoveredNodeId(node.id)}
                          onMouseLeave={() => setHoveredNodeId(null)}
                          className="cursor-pointer transition-all duration-150"
                          style={{ opacity: isDimmed ? 0.35 : 1 }}
                        >
                          {/* Node Box */}
                          <rect
                            width={node.w}
                            height={node.h}
                            rx="6"
                            fill={fillColor}
                            stroke={borderColor}
                            strokeWidth={isSelected ? "2" : node.isDirectOwnership ? "1.5" : "1"}
                            strokeDasharray={!node.isDirectOwnership ? "3 3" : undefined}
                            filter={isSelected ? "url(#emerald-glow)" : undefined}
                          />

                          {/* Node Header Pill */}
                          <rect
                            x="6"
                            y="6"
                            width={node.w - 12}
                            height="16"
                            rx="3"
                            fill={node.isDirectOwnership ? "rgba(16, 185, 129, 0.15)" : "rgba(63, 63, 70, 0.3)"}
                          />

                          {/* Category Tag */}
                          <text
                            x="10"
                            y="17"
                            fill={node.isDirectOwnership ? "#34d399" : "#a1a1aa"}
                            fontSize="8"
                            fontFamily="monospace"
                            fontWeight="bold"
                          >
                            {node.category.toUpperCase()}
                            {node.isDirectOwnership ? " [OWNED]" : ""}
                          </text>

                          {/* Node Title */}
                          <text
                            x="10"
                            y="36"
                            fill={textColor}
                            fontSize="11"
                            fontFamily="system-ui, sans-serif"
                            fontWeight="bold"
                          >
                            {node.shortLabel}
                          </text>

                          {/* Technology Subtitle */}
                          <text
                            x="10"
                            y="48"
                            fill={node.isDirectOwnership ? "#a7f3d0" : "#71717a"}
                            fontSize="9"
                            fontFamily="monospace"
                          >
                            {node.technology.split("/")[0].trim()}
                          </text>
                        </g>
                      );
                    })}
                  </g>
                </svg>
              </div>

              {/* Real-Time Live Inspector Drawer */}
              <div className="mt-5 p-5 rounded-lg bg-zinc-900/95 border border-zinc-800 shadow-xl">
                <div className="flex flex-col sm:flex-row sm:items-baseline justify-between pb-3 mb-3 border-b border-zinc-800 gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono uppercase px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
                        {selectedNode.category.toUpperCase()}
                      </span>
                      <h4 className="text-base font-bold text-zinc-100 font-sans">
                        {selectedNode.name}
                      </h4>
                    </div>
                    <p className="text-xs font-mono text-zinc-400 mt-1">
                      Role: {selectedNode.role} | Tech: {selectedNode.technology}
                    </p>
                  </div>

                  <span
                    className={`text-xs font-mono px-2.5 py-1 rounded border self-start sm:self-auto ${
                      selectedNode.isDirectOwnership
                        ? "bg-emerald-950/80 text-emerald-300 border-emerald-800/80"
                        : "bg-zinc-800 text-zinc-400 border-zinc-700"
                    }`}
                  >
                    {selectedNode.isDirectOwnership
                      ? "★ Direct Domain of Ownership"
                      : "Adjacent / Partner ML Team"}
                  </span>
                </div>

                <p className="text-sm text-zinc-300 font-sans leading-relaxed mb-4">
                  {selectedNode.description}
                </p>

                {selectedNode.metrics && (
                  <div className="flex flex-wrap items-center gap-2 mb-4">
                    <span className="text-xs font-mono text-zinc-500 uppercase mr-1">
                      Key Impact Metrics:
                    </span>
                    {selectedNode.metrics.map((m) => (
                      <span
                        key={m}
                        className="text-xs font-mono px-2.5 py-0.5 rounded bg-zinc-800/90 border border-zinc-700 text-emerald-300"
                      >
                        {m}
                      </span>
                    ))}
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 border-t border-zinc-800/80 text-xs font-mono">
                  <div>
                    <span className="text-[10px] text-zinc-500 uppercase block mb-1">
                      Upstream Sources:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedNode.connections.upstream.length > 0 ? (
                        selectedNode.connections.upstream.map((up) => (
                          <button
                            key={up}
                            onClick={() => setSelectedNodeId(up)}
                            className="px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
                          >
                            ← {NODES[up]?.name || up}
                          </button>
                        ))
                      ) : (
                        <span className="text-zinc-600">None (Ingress Origin)</span>
                      )}
                    </div>
                  </div>

                  <div>
                    <span className="text-[10px] text-zinc-500 uppercase block mb-1">
                      Downstream Consumers:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedNode.connections.downstream.length > 0 ? (
                        selectedNode.connections.downstream.map((down) => (
                          <button
                            key={down}
                            onClick={() => setSelectedNodeId(down)}
                            className="px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
                          >
                            → {NODES[down]?.name || down}
                          </button>
                        ))
                      ) : (
                        <span className="text-zinc-600">None (Terminal Storage / Sink)</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
