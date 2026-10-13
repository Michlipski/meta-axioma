import React from "react";
import { COMPETENCIES } from "@/data/portfolioData";

export default function CompetenciesSection() {
  return (
    <section id="competencies" className="py-12 border-b border-zinc-800/80">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2 mb-6">
          <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">
            01 //
          </span>
          <h2 className="text-xl font-bold tracking-tight text-zinc-100 font-sans">
            Core Competencies & Technical Matrix
          </h2>
        </div>

        <p className="text-sm text-zinc-400 mb-8 max-w-2xl font-sans">
          A targeted operational surface focused on high-throughput backend services, fault-tolerant infrastructure, and zero-trust runtime boundaries.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {COMPETENCIES.map((group) => (
            <div
              key={group.category}
              className="p-5 rounded-lg bg-zinc-900/40 border border-zinc-800/80 hover:border-zinc-700/80 transition-colors"
            >
              <div className="flex items-center justify-between pb-3 mb-4 border-b border-zinc-800/60">
                <h3 className="text-xs font-mono uppercase tracking-wider text-zinc-300 font-semibold">
                  {group.category}
                </h3>
                <span className="text-[10px] font-mono text-zinc-500">
                  [{group.items.length} ACTIVE]
                </span>
              </div>

              <ul className="space-y-2">
                {group.items.map((item) => (
                  <li
                    key={item}
                    className="flex items-center text-sm font-mono text-zinc-300"
                  >
                    <span className="text-zinc-600 mr-2 text-xs">▹</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
