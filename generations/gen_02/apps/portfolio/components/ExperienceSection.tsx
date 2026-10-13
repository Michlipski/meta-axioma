import React from "react";
import { EXPERIENCES } from "@/data/portfolioData";

export default function ExperienceSection() {
  return (
    <section id="experience" className="py-12 border-b border-zinc-800/80">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2 mb-6">
          <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">
            03 //
          </span>
          <h2 className="text-xl font-bold tracking-tight text-zinc-100 font-sans">
            Professional Experience (Abridged)
          </h2>
        </div>

        <p className="text-sm text-zinc-400 mb-8 max-w-2xl font-sans">
          Proven history scaling distributed backend microservices, high-volume ingestion queues, and enterprise SaaS customer touchpoints.
        </p>

        <div className="space-y-8">
          {EXPERIENCES.map((exp) => (
            <div
              key={exp.company}
              className="p-6 rounded-lg bg-zinc-900/30 border border-zinc-800/80"
            >
              <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-1 mb-2">
                <div>
                  <h3 className="text-lg font-bold text-zinc-100 font-sans">
                    {exp.company}
                  </h3>
                  <p className="text-xs font-mono text-zinc-400">
                    {exp.role}
                  </p>
                </div>

                {exp.hasArchitectureDiagram && (
                  <a
                    href="#beehive-architecture"
                    className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 hover:text-white border border-zinc-700/70 transition-colors self-start sm:self-auto"
                  >
                    <span>View Overseen Systems Stack ↓</span>
                  </a>
                )}
              </div>

              <p className="text-sm text-zinc-300 leading-relaxed mb-4 font-sans font-medium">
                {exp.summary}
              </p>

              <div className="space-y-2 mb-5">
                {exp.achievements.map((item, idx) => (
                  <div
                    key={idx}
                    className="flex items-start text-xs sm:text-sm text-zinc-400 font-sans"
                  >
                    <span className="text-zinc-600 font-mono mr-2.5 mt-0.5 select-none">
                      —
                    </span>
                    <span className="leading-relaxed">{item}</span>
                  </div>
                ))}
              </div>

              <div className="flex flex-wrap items-center gap-1.5 pt-3 border-t border-zinc-800/60">
                <span className="text-[11px] font-mono text-zinc-500 mr-2 uppercase tracking-wider">
                  Stack:
                </span>
                {exp.technologies.map((tech) => (
                  <span
                    key={tech}
                    className="text-xs font-mono px-2 py-0.5 rounded bg-zinc-800/40 border border-zinc-800 text-zinc-300"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
