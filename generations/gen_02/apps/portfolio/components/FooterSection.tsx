import React from "react";
import Link from "next/link";
import { HERO_DATA } from "@/data/portfolioData";

export default function FooterSection() {
  return (
    <footer className="py-12 bg-zinc-950 text-xs font-mono text-zinc-500 border-t border-zinc-800/80">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-zinc-800/60">
          <div className="space-y-1">
            <p className="text-zinc-300 font-semibold font-sans">
              Michael Lipski — Systems Engineering & Architecture
            </p>
            <p className="text-[11px] text-zinc-500">
              Compiled under Meta-Axioma Generation 2 (Autonomous Domain Compiler)
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-xs">
            <Link
              href="/axioma"
              className="text-zinc-400 hover:text-zinc-200 transition-colors"
            >
              /axioma (Demo Proxy)
            </Link>
            <a
              href={HERO_DATA.links.github}
              target="_blank"
              rel="noopener noreferrer"
              className="text-zinc-400 hover:text-zinc-200 transition-colors"
            >
              GitHub
            </a>
            <a
              href={HERO_DATA.links.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="text-zinc-400 hover:text-zinc-200 transition-colors"
            >
              LinkedIn
            </a>
            <a
              href={HERO_DATA.links.email}
              className="text-zinc-400 hover:text-zinc-200 transition-colors"
            >
              Contact
            </a>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px] text-zinc-600">
          <p>
            Architecture: Next.js App Router (Static Export) · Tailwind CSS · Vercel Multi-Zone Rewrites
          </p>
          <p>
            Invariants: [L1-G2-001] Substrate Preservation · [L1-G2-005] Intent Grounded
          </p>
        </div>
      </div>
    </footer>
  );
}
