import React from "react";
import Link from "next/link";
import { PROJECTS } from "@/data/portfolioData";

export default function ProjectsSection() {
  return (
    <section id="projects" className="py-12 border-b border-zinc-800/80">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2 mb-6">
          <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">
            02 //
          </span>
          <h2 className="text-xl font-bold tracking-tight text-zinc-100 font-sans">
            R&D & Systems Architecture
          </h2>
        </div>

        <p className="text-sm text-zinc-400 mb-8 max-w-2xl font-sans">
          Exploratory research systems formalizing non-deterministic LLM execution into deterministic state automata and recursive axiomatic compilers.
        </p>

        <div className="space-y-6">
          {PROJECTS.map((project) => (
            <div
              key={project.id}
              className="p-6 rounded-lg bg-zinc-900/40 border border-zinc-800/80 hover:border-zinc-700 transition-colors"
            >
              <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 mb-3">
                <div className="flex items-baseline gap-3">
                  <h3 className="text-lg font-bold text-zinc-100 font-sans">
                    {project.title}
                  </h3>
                  <span className="text-xs font-mono text-zinc-400">
                    // {project.subtitle}
                  </span>
                </div>

                {project.demoUrl && (
                  <Link
                    href={project.demoUrl}
                    className="inline-flex items-center gap-1 text-xs font-mono px-3 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 hover:text-white border border-zinc-700 transition-colors self-start sm:self-auto"
                  >
                    <span>{project.demoLabel || "Live Demo"}</span>
                    <span>↗</span>
                  </Link>
                )}
              </div>

              <p className="text-sm text-zinc-300 leading-relaxed mb-4 font-sans">
                {project.description}
              </p>

              {/* Systems Architectural Metrics Grid */}
              {project.metrics && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 mb-5 p-3 rounded bg-zinc-950/60 border border-zinc-800/60 font-mono text-xs">
                  {project.metrics.map((m) => (
                    <div key={m.label} className="flex flex-col">
                      <span className="text-[10px] text-zinc-500 uppercase tracking-wider">
                        {m.label}
                      </span>
                      <span className="text-zinc-300 font-medium">{m.value}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Technologies Badges */}
              <div className="flex flex-wrap items-center gap-2">
                {project.tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-xs font-mono px-2 py-0.5 rounded bg-zinc-800/60 border border-zinc-700/60 text-zinc-300"
                  >
                    {tag}
                  </span>
                ))}

                {project.id === "axioma" && (
                  <span className="text-[11px] font-mono text-zinc-500 ml-auto hidden sm:inline">
                    Multi-Zone Route: /axioma/:path*
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
