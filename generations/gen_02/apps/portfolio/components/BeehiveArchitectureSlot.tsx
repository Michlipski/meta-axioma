"use client";

import React, { useState } from "react";

interface SystemNode {
  id: string;
  name: string;
  category: "api" | "pipeline" | "db" | "ai" | "client" | "external";
  isDirectOwnership: boolean;
  isPrimaryHighlight?: boolean;
  technology: string;
  role: string;
  description: string;
  connections: {
    upstream: string[];
    downstream: string[];
  };
  metrics?: string[];
}

const NODES: Record<string, SystemNode> = {
  user: {
    id: "user",
    name: "End User (Customer)",
    category: "client",
    isDirectOwnership: false,
    technology: "Web / Mobile",
    role: "External Customer Traffic",
    description: "Enterprise SaaS customers interacting with the customer-facing analytics and insights platform.",
    connections: {
      upstream: [],
      downstream: ["dashboard"],
    },
  },
  internal_user: {
    id: "internal_user",
    name: "Internal Operators & Admins",
    category: "client",
    isDirectOwnership: false,
    technology: "Internal Staff",
    role: "Internal Governance & Operations",
    description: "Support engineers, operations specialists, and administrators managing customer tenants and data quality.",
    connections: {
      upstream: [],
      downstream: ["admin_tool", "data_ops_dashboard"],
    },
  },
  providers: {
    id: "providers",
    name: "Real-Time Data Providers",
    category: "external",
    isDirectOwnership: false,
    technology: "External Webhooks / REST APIs",
    role: "Third-Party Data Egress",
    description: "Customer CRM integrations, support ticket streams, and real-time enterprise event sources firing webhooks.",
    connections: {
      upstream: [],
      downstream: ["webhook_service"],
    },
  },
  cronjobs: {
    id: "cronjobs",
    name: "Data Provider Sync Cronjobs",
    category: "pipeline",
    isDirectOwnership: true,
    technology: "K8s CronJobs / Go Runners",
    role: "Scheduled Ingestion Dispatcher",
    description: "Scheduled recurring synchronization runners querying third-party provider APIs and pushing raw batches into the pipeline.",
    connections: {
      upstream: [],
      downstream: ["etl_extract"],
    },
  },
  dashboard: {
    id: "dashboard",
    name: "Customer Dashboard",
    category: "client",
    isDirectOwnership: true,
    technology: "React / TypeScript",
    role: "User Interface Layer",
    description: "High-performance reactive frontend delivering real-time customer data exploration and analytics.",
    connections: {
      upstream: ["user"],
      downstream: ["dashboard_api"],
    },
  },
  admin_tool: {
    id: "admin_tool",
    name: "Administration Tool",
    category: "api",
    isDirectOwnership: true,
    isPrimaryHighlight: true,
    technology: "React / Go Internal Service",
    role: "Administrative Platform",
    description: "Internal tooling for tenant orchestration, debugging, state inspection, and manual override workflows.",
    connections: {
      upstream: ["internal_user"],
      downstream: ["db", "ai_interactive", "ai_models"],
    },
  },
  data_ops_dashboard: {
    id: "data_ops_dashboard",
    name: "Data Ops Dashboard",
    category: "client",
    isDirectOwnership: true,
    technology: "React / TypeScript",
    role: "Data Operations UI",
    description: "Operational interface for pipeline health monitoring, ingestion retry oversight, and data schema migrations.",
    connections: {
      upstream: ["internal_user"],
      downstream: ["data_ops_api"],
    },
  },
  dashboard_api: {
    id: "dashboard_api",
    name: "Dashboard API",
    category: "api",
    isDirectOwnership: true,
    isPrimaryHighlight: true,
    technology: "Go (Golang) Microservice",
    role: "Core Customer Application API",
    description: "High-throughput customer-facing backend API handling low-latency reads, mutations, on-demand ETL triggers, and AI interactions.",
    connections: {
      upstream: ["dashboard"],
      downstream: ["db", "ai_interactive", "etl_extract"],
    },
    metrics: ["Sub-50ms read latency", "Stateless horizontal scaling", "Connection pooling"],
  },
  data_ops_api: {
    id: "data_ops_api",
    name: "Data Ops API",
    category: "api",
    isDirectOwnership: true,
    isPrimaryHighlight: true,
    technology: "Go / Microservices",
    role: "Operational Ingestion Management API",
    description: "Dedicated operational API handling ingestion auditing, quarantine reprocessing, and direct database maintenance tasks.",
    connections: {
      upstream: ["data_ops_dashboard"],
      downstream: ["db"],
    },
  },
  webhook_service: {
    id: "webhook_service",
    name: "Webhook Ingestion Service",
    category: "pipeline",
    isDirectOwnership: true,
    isPrimaryHighlight: true,
    technology: "Go / High-Concurrency HTTP Ingress",
    role: "Real-Time Ingress Gate",
    description: "High-throughput ingress buffer placed between real-time data providers and the pipeline. Rapidly authenticates, validates, and absorbs webhook bursts with backpressure.",
    connections: {
      upstream: ["providers"],
      downstream: ["etl_extract"],
    },
    metrics: ["Sub-15ms HTTP 200 response", "Bursty volume absorption", "Token bucket rate limiting"],
  },
  etl_extract: {
    id: "etl_extract",
    name: "ETL: Ingress Buffer & Queue",
    category: "pipeline",
    isDirectOwnership: true,
    isPrimaryHighlight: true,
    technology: "RabbitMQ / AMQP Message Broker",
    role: "Pipeline Extraction & Buffering Layer",
    description: "Durable asynchronous message queues decoupling high-volume ingress surges from downstream processing. Buffers webhook events and cronjob sync payloads.",
    connections: {
      upstream: ["webhook_service", "cronjobs", "dashboard_api"],
      downstream: ["etl_transform"],
    },
    metrics: ["Durable per-tenant queues", "Zero payload loss under burst", "Dead-letter exchange (DLX) retries"],
  },
  etl_transform: {
    id: "etl_transform",
    name: "ETL: Go Normalization Mesh",
    category: "pipeline",
    isDirectOwnership: true,
    isPrimaryHighlight: true,
    technology: "Go Worker Mesh / Goroutine Pools",
    role: "Transformation & Deduplication Engine",
    description: "Concurrent Go worker pools performing payload deduplication, schema validation, tenant formatting, and coordinating enrichment with AI Model Microservices.",
    connections: {
      upstream: ["etl_extract", "ai_models"],
      downstream: ["ai_models", "etl_load"],
    },
    metrics: ["Goroutine worker pools", "SHA-256 deduplication cache", "Graceful backpressure"],
  },
  etl_load: {
    id: "etl_load",
    name: "ETL: Batched Bulk DB Loader",
    category: "pipeline",
    isDirectOwnership: true,
    isPrimaryHighlight: true,
    technology: "Go / Batched pg_copy Transactions",
    role: "Persistence & Bulk Write Engine",
    description: "High-volume bulk loader writing normalized, enriched data into partitioned PostgreSQL tables using optimized transactional batching.",
    connections: {
      upstream: ["etl_transform"],
      downstream: ["db"],
    },
    metrics: ["Scaled >10M records", "High-efficiency batch inserts", "Zero lock contention"],
  },
  ai_interactive: {
    id: "ai_interactive",
    name: "Interactive AI Microservices",
    category: "ai",
    isDirectOwnership: true,
    isPrimaryHighlight: true,
    technology: "Go / Python Serving Runtime",
    role: "Real-Time AI Inference Gateway",
    description: "Low-latency microservices serving real-time AI capabilities directly to the Customer Dashboard API and Administration Tool.",
    connections: {
      upstream: ["dashboard_api", "admin_tool"],
      downstream: [],
    },
    metrics: ["Real-time response SLA", "Fault-tolerant fallbacks", "Circuit-broken endpoints"],
  },
  ai_models: {
    id: "ai_models",
    name: "AI Model Microservices (ML Team)",
    category: "ai",
    isDirectOwnership: false,
    technology: "Python / PyTorch / GPU Microservices",
    role: "Specialized Deep Learning & NLP Enrichment",
    description: "Batch embedding, extraction, and classification models trained and operated by the dedicated ML/Data Science team. Enriches payloads processed by the ETL pipeline.",
    connections: {
      upstream: ["etl_transform", "admin_tool"],
      downstream: ["etl_transform", "db"],
    },
  },
  db: {
    id: "db",
    name: "Primary Database (PostgreSQL)",
    category: "db",
    isDirectOwnership: true,
    isPrimaryHighlight: true,
    technology: "PostgreSQL / Partition Matrix",
    role: "Single Source of Truth",
    description: "Centrally architected relational data plane scaled to 10M+ enterprise customer records. Employs tenant partitioning, GIN/B-tree indexes, and connection pooling for sub-50ms queries.",
    connections: {
      upstream: ["dashboard_api", "data_ops_api", "admin_tool", "etl_load", "ai_models"],
      downstream: [],
    },
    metrics: ["10M+ customer records", "Sub-50ms query latency", "Tenant table partitioning"],
  },
};

export default function BeehiveArchitectureSlot() {
  const [selectedNodeId, setSelectedNodeId] = useState<string>("etl_transform");
  const [activeFilter, setActiveFilter] = useState<"all" | "ownership" | "pipeline">("ownership");
  const [viewMode, setViewMode] = useState<"visual" | "mermaid">("visual");

  const selectedNode = NODES[selectedNodeId] || NODES["etl_transform"];

  const mermaidSource = `flowchart TD
    %% Access Plane
    U[User] --> A[Dashboard]
    I[Internal User] --> H[Administration Tool]
    I --> D[Data_Ops_Dashboard]

    %% Application & Ingress Services (Michael's Domain)
    A --> B(Dashboard API)
    D --> E[Data_ops_API]
    R[Real-Time Data Providers] --> W[Webhook Ingestion Service]
    N[Sync Cronjobs] --> F_EXTRACT[ETL: RabbitMQ Queue Buffer]

    %% Webhook to ETL Ingress
    W --> F_EXTRACT

    %% APIs to Persistence & ETL
    B --> C[(PostgreSQL DB - 10M+ Records)]
    B --> J[Interactive AI Microservices]
    B --> F_EXTRACT
    E --> C
    H --> C
    H --> J
    H --> G[AI Model Microservices - ML Team]

    %% Exploded ETL Pipeline (Michael's Domain)
    subgraph ETL_Pipeline ["ETL Pipeline Engine (Overseen by Michael)"]
        F_EXTRACT --> F_TRANSFORM[ETL: Go Normalization Mesh]
        F_TRANSFORM --> F_LOAD[ETL: Batched DB Loader]
    end

    %% ML Team Enrichment Boundary
    F_TRANSFORM <--> G
    G --> C

    %% Pipeline Load to Database
    F_LOAD --> C

    %% Styling
    classDef owned fill:#18181b,stroke:#10b981,stroke-width:2px,color:#f4f4f5;
    classDef external fill:#09090b,stroke:#52525b,stroke-width:1px,stroke-dasharray: 4 4,color:#a1a1aa;
    class B,E,H,W,F_EXTRACT,F_TRANSFORM,F_LOAD,J,C owned;
    class G,R,U,I external;`;

  return (
    <section id="beehive-architecture" className="py-14 border-b border-zinc-800/80 bg-zinc-950/40">
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
          Full-system architectural map of Beehive AI. Everything highlighted in emerald represents Michael Lipski&apos;s direct domain of ownership—specifically architecting the high-throughput Go APIs, the exploded ETL ingestion pipeline, real-time webhook ingress, interactive AI microservices, and the PostgreSQL partition matrix scaling past 10 million records.
        </p>

        {/* Controls Bar: Filters & Visual/Mermaid Tabs */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-6 p-2 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="text-zinc-500 mr-1.5 uppercase text-[11px]">Filter:</span>
            <button
              onClick={() => setActiveFilter("ownership")}
              className={`px-3 py-1 rounded transition-colors ${
                activeFilter === "ownership"
                  ? "bg-zinc-800 text-emerald-300 border border-emerald-800/60"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              ★ Michael&apos;s Direct Scope
            </button>
            <button
              onClick={() => setActiveFilter("pipeline")}
              className={`px-3 py-1 rounded transition-colors ${
                activeFilter === "pipeline"
                  ? "bg-zinc-800 text-zinc-200 border border-zinc-700"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              ETL Ingestion Deep-Dive
            </button>
            <button
              onClick={() => setActiveFilter("all")}
              className={`px-3 py-1 rounded transition-colors ${
                activeFilter === "all"
                  ? "bg-zinc-800 text-zinc-200 border border-zinc-700"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              All Systems
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

        {/* Main Interactive Container */}
        <div className="p-6 rounded-lg bg-zinc-950 border border-zinc-800 relative overflow-hidden">
          {/* Subtle grid pattern overlay */}
          <div className="absolute inset-0 tech-grid opacity-20 pointer-events-none"></div>

          {viewMode === "mermaid" ? (
            /* Mermaid Source View */
            <div className="relative z-10 space-y-4 font-mono text-xs">
              <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
                <span className="text-zinc-400 uppercase tracking-wider">
                  Raw Mermaid Architecture Specification
                </span>
                <span className="text-zinc-500 text-[11px]">
                  Compatible with GitHub, Notion & Mermaid Live Editor
                </span>
              </div>
              <pre className="p-4 rounded bg-zinc-900/90 text-zinc-300 border border-zinc-800 overflow-x-auto leading-relaxed">
                {mermaidSource}
              </pre>
            </div>
          ) : (
            /* Interactive Visual Flow */
            <div className="relative z-10 space-y-8">
              {/* Architecture Blueprint Grid */}
              <div className="space-y-6">
                {/* 1. Client & Ingress Plane */}
                <div>
                  <div className="text-[10px] font-mono uppercase tracking-widest text-zinc-500 mb-2 flex items-center gap-2">
                    <span>Tier 1 // Access, Ingress & Scheduled Triggers</span>
                    <span className="h-px flex-1 bg-zinc-800/80"></span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {[
                      NODES.user,
                      NODES.internal_user,
                      NODES.providers,
                      NODES.cronjobs,
                    ].map((node) => {
                      const isSelected = selectedNodeId === node.id;
                      const isDimmed = activeFilter === "ownership" && !node.isDirectOwnership;
                      return (
                        <button
                          key={node.id}
                          onClick={() => setSelectedNodeId(node.id)}
                          className={`text-left p-3 rounded transition-all border ${
                            isSelected
                              ? "ring-1 ring-emerald-500 border-emerald-500 bg-zinc-900"
                              : node.isDirectOwnership
                              ? "border-emerald-800/60 bg-zinc-900/40 hover:border-emerald-600"
                              : "border-zinc-800 bg-zinc-900/20 hover:border-zinc-700"
                          } ${isDimmed ? "opacity-40" : "opacity-100"}`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-[10px] font-mono text-zinc-500 uppercase">
                              {node.category}
                            </span>
                            {node.isDirectOwnership && (
                              <span className="text-[8px] font-mono text-emerald-400 bg-emerald-950/80 px-1 rounded border border-emerald-800/60">
                                OWNED
                              </span>
                            )}
                          </div>
                          <p className="text-xs font-bold text-zinc-200 font-sans truncate">
                            {node.name}
                          </p>
                          <p className="text-[10px] font-mono text-zinc-400 truncate mt-0.5">
                            {node.technology}
                          </p>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* 2. Application Frontends & Ingress Webhooks */}
                <div>
                  <div className="text-[10px] font-mono uppercase tracking-widest text-zinc-500 mb-2 flex items-center gap-2">
                    <span>Tier 2 // User Interfaces & Ingress Gateway</span>
                    <span className="h-px flex-1 bg-zinc-800/80"></span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {[
                      NODES.dashboard,
                      NODES.data_ops_dashboard,
                      NODES.admin_tool,
                      NODES.webhook_service,
                    ].map((node) => {
                      const isSelected = selectedNodeId === node.id;
                      const isDimmed = activeFilter === "ownership" && !node.isDirectOwnership;
                      return (
                        <button
                          key={node.id}
                          onClick={() => setSelectedNodeId(node.id)}
                          className={`text-left p-3 rounded transition-all border ${
                            isSelected
                              ? "ring-1 ring-emerald-500 border-emerald-500 bg-zinc-900"
                              : node.isDirectOwnership
                              ? "border-emerald-800/60 bg-zinc-900/50 hover:border-emerald-500"
                              : "border-zinc-800 bg-zinc-900/20"
                          } ${isDimmed ? "opacity-40" : "opacity-100"}`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-[10px] font-mono text-zinc-500 uppercase">
                              {node.category}
                            </span>
                            {node.isDirectOwnership && (
                              <span className="text-[8px] font-mono text-emerald-400 bg-emerald-950/80 px-1 rounded border border-emerald-800/60">
                                OWNED
                              </span>
                            )}
                          </div>
                          <p className="text-xs font-bold text-zinc-100 font-sans truncate">
                            {node.name}
                          </p>
                          <p className="text-[10px] font-mono text-emerald-400/90 truncate mt-0.5">
                            {node.technology}
                          </p>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* 3. Core Go APIs & Interactive AI Microservices */}
                <div>
                  <div className="text-[10px] font-mono uppercase tracking-widest text-zinc-500 mb-2 flex items-center gap-2">
                    <span>Tier 3 // Core Go APIs & Real-Time AI Services (Primary Oversight)</span>
                    <span className="h-px flex-1 bg-zinc-800/80"></span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    {[
                      NODES.dashboard_api,
                      NODES.data_ops_api,
                      NODES.ai_interactive,
                    ].map((node) => {
                      const isSelected = selectedNodeId === node.id;
                      return (
                        <button
                          key={node.id}
                          onClick={() => setSelectedNodeId(node.id)}
                          className={`text-left p-3.5 rounded transition-all border ${
                            isSelected
                              ? "ring-2 ring-emerald-500 border-emerald-500 bg-zinc-900"
                              : "border-emerald-700/80 bg-zinc-900/60 hover:border-emerald-400"
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-[10px] font-mono text-emerald-400 uppercase font-semibold">
                              ★ CORE MICROSERVICE
                            </span>
                            <span className="text-[8px] font-mono text-emerald-400 bg-emerald-950/80 px-1.5 py-0.5 rounded border border-emerald-800/60">
                              DIRECT OWNERSHIP
                            </span>
                          </div>
                          <p className="text-sm font-bold text-zinc-100 font-sans">
                            {node.name}
                          </p>
                          <p className="text-xs font-mono text-zinc-300 mt-1">
                            {node.technology}
                          </p>
                          <p className="text-[11px] text-zinc-400 font-sans mt-1 line-clamp-2">
                            {node.role}
                          </p>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* 4. Exploded High-Throughput ETL Pipeline */}
                <div className="p-4 rounded-lg bg-zinc-900/40 border border-emerald-900/70">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                      <span className="text-xs font-mono uppercase tracking-wider text-emerald-300 font-bold">
                        ETL Ingestion Engine (Exploded Subsystem)
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-zinc-400">
                      Throughput: Scaling to 10M+ Enterprise Records
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {[
                      NODES.etl_extract,
                      NODES.etl_transform,
                      NODES.etl_load,
                    ].map((node) => {
                      const isSelected = selectedNodeId === node.id;
                      return (
                        <button
                          key={node.id}
                          onClick={() => setSelectedNodeId(node.id)}
                          className={`text-left p-3.5 rounded transition-all border ${
                            isSelected
                              ? "ring-2 ring-emerald-500 border-emerald-500 bg-zinc-900"
                              : "border-zinc-700/80 bg-zinc-950/90 hover:border-emerald-500"
                          }`}
                        >
                          <span className="text-[10px] font-mono text-emerald-400 block mb-1">
                            {node.role}
                          </span>
                          <p className="text-xs font-bold text-zinc-100 font-sans">
                            {node.name}
                          </p>
                          <p className="text-[11px] font-mono text-zinc-300 mt-0.5">
                            {node.technology}
                          </p>
                        </button>
                      );
                    })}
                  </div>

                  {/* ML Team Model Microservices Hand-off indicator */}
                  <div className="mt-3 pt-3 border-t border-zinc-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono">
                    <span className="text-zinc-400 flex items-center gap-1.5">
                      <span className="text-zinc-600">⇄</span>
                      <span>Enrichment Hand-off:</span>
                      <button
                        onClick={() => setSelectedNodeId("ai_models")}
                        className="text-amber-300 hover:underline inline-flex items-center gap-1"
                      >
                        AI Model Microservices (ML Team Domain)
                        <span className="text-[10px] text-zinc-500">[Inspect]</span>
                      </button>
                    </span>
                    <span className="text-[11px] text-zinc-500">
                      Extract (RabbitMQ) ➔ Transform (Go Mesh) ➔ Load (Bulk PostgreSQL)
                    </span>
                  </div>
                </div>

                {/* 5. Database Layer (PostgreSQL) */}
                <div>
                  <div className="text-[10px] font-mono uppercase tracking-widest text-zinc-500 mb-2 flex items-center gap-2">
                    <span>Tier 5 // Storage Plane (Single Source of Truth)</span>
                    <span className="h-px flex-1 bg-zinc-800/80"></span>
                  </div>
                  <button
                    onClick={() => setSelectedNodeId("db")}
                    className={`w-full text-left p-4 rounded-lg transition-all border ${
                      selectedNodeId === "db"
                        ? "ring-2 ring-emerald-500 border-emerald-500 bg-zinc-900"
                        : "border-emerald-700/80 bg-zinc-900/60 hover:border-emerald-400"
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 mb-2 border-b border-zinc-800 gap-2">
                      <div className="flex items-center gap-2">
                        <span className="text-emerald-400 font-mono text-sm">[( DB )]</span>
                        <h4 className="text-sm font-bold text-zinc-100 font-sans">
                          {NODES.db.name}
                        </h4>
                        <span className="text-xs font-mono text-zinc-400">
                          // {NODES.db.technology}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/60 self-start sm:self-auto">
                        DIRECT OWNERSHIP · 10M+ RECORDS
                      </span>
                    </div>
                    <p className="text-xs text-zinc-300 font-sans leading-relaxed">
                      {NODES.db.description}
                    </p>
                  </button>
                </div>
              </div>

              {/* Node Inspector Drawer */}
              <div className="p-5 rounded-lg bg-zinc-900/90 border border-zinc-800 shadow-lg">
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
                      ? "★ In Michael's Direct Domain"
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
