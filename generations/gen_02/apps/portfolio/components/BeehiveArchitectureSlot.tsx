import React from "react";

export default function BeehiveArchitectureSlot() {
  return (
    <section id="beehive-architecture" className="py-12 border-b border-zinc-800/80">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">
              04 //
            </span>
            <h2 className="text-xl font-bold tracking-tight text-zinc-100 font-sans">
              Beehive AI: Overseen Systems Stack
            </h2>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-amber-950/40 border border-amber-800/60 text-amber-300">
            [RESERVED ARCHITECTURE SLOT]
          </span>
        </div>

        <p className="text-sm text-zinc-400 mb-6 max-w-2xl font-sans">
          Detailed architectural breakdown highlighting the high-throughput ingestion pipelines and microservices infrastructure directly architected and scaled by Michael Lipski.
        </p>

        {/* Structural Blueprint Card */}
        <div className="p-6 rounded-lg bg-zinc-950 border border-zinc-800 relative overflow-hidden">
          {/* Subtle grid pattern overlay */}
          <div className="absolute inset-0 tech-grid opacity-20 pointer-events-none"></div>

          <div className="relative z-10 space-y-6">
            {/* Architectural Scope Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-zinc-800/80 gap-2">
              <div className="space-y-0.5">
                <span className="text-xs font-mono uppercase tracking-wider text-zinc-300 font-semibold">
                  Scope of Direct Ownership
                </span>
                <p className="text-xs text-zinc-500 font-mono">
                  Scale: 10M+ Enterprise Records | Target: Sub-Second Ingestion & Resilient Buffering
                </p>
              </div>
              <div className="flex items-center gap-2 text-xs font-mono">
                <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                  Runtime: Go (Golang)
                </span>
                <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                  Broker: RabbitMQ
                </span>
                <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                  Store: PostgreSQL
                </span>
              </div>
            </div>

            {/* High-Level Subsystem Flow Preview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-3.5 rounded bg-zinc-900/70 border border-zinc-800">
                <span className="text-[10px] text-zinc-500 uppercase block mb-1">
                  Tier 1: Ingress
                </span>
                <p className="font-semibold text-zinc-200 mb-1">Enterprise Ingestion Gate</p>
                <p className="text-[11px] text-zinc-400 font-sans">
                  Multi-tenant webhooks & batch endpoints handling bursty API payloads with backpressure.
                </p>
              </div>

              <div className="p-3.5 rounded bg-zinc-900/70 border border-zinc-700/80 bg-zinc-900/90 shadow-sm ring-1 ring-zinc-700/50">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] text-zinc-400 uppercase">
                    Tier 2: Core Stack ★
                  </span>
                  <span className="text-[9px] text-emerald-400 bg-emerald-950/60 px-1 rounded border border-emerald-800/60">
                    Oversight
                  </span>
                </div>
                <p className="font-semibold text-zinc-100 mb-1">Go Microservices Worker Mesh</p>
                <p className="text-[11px] text-zinc-300 font-sans">
                  Goroutine worker pools executing validation, deduplication, and schema normalization.
                </p>
              </div>

              <div className="p-3.5 rounded bg-zinc-900/70 border border-zinc-800">
                <span className="text-[10px] text-zinc-500 uppercase block mb-1">
                  Tier 3: Stream
                </span>
                <p className="font-semibold text-zinc-200 mb-1">RabbitMQ Buffer Queues</p>
                <p className="text-[11px] text-zinc-400 font-sans">
                  Asynchronous durable queues decoupling ingestion spikes from downstream ML indexing.
                </p>
              </div>

              <div className="p-3.5 rounded bg-zinc-900/70 border border-zinc-800">
                <span className="text-[10px] text-zinc-500 uppercase block mb-1">
                  Tier 4: Storage
                </span>
                <p className="font-semibold text-zinc-200 mb-1">PostgreSQL Partition Matrix</p>
                <p className="text-[11px] text-zinc-400 font-sans">
                  Partitioned customer tables maintaining sub-50ms query latency across 10M+ rows.
                </p>
              </div>
            </div>

            {/* Q&A Follow-up Dock Banner */}
            <div className="p-4 rounded bg-zinc-900/40 border border-dashed border-zinc-700/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-3">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse flex-shrink-0"></span>
                <p className="text-zinc-300 font-sans">
                  <span className="font-mono font-semibold text-zinc-200">Interactive Follow-Up Slot:</span>{" "}
                  This architecture module will be populated with a complete interactive systems diagram reflecting our follow-up collaborative architectural Q&A.
                </p>
              </div>
              <span className="text-[11px] font-mono text-zinc-400 whitespace-nowrap px-2.5 py-1 rounded bg-zinc-800 border border-zinc-700">
                STATUS: READY_FOR_QA
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
