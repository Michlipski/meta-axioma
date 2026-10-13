import React from "react";
import { HERO_DATA } from "@/data/portfolioData";

export default function HeroSection() {
  return (
    <section id="about" className="pt-16 pb-12 sm:pt-24 sm:pb-16 border-b border-zinc-800/80">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Academic / Documentation Top Meta Tag */}
        <div className="flex flex-wrap items-center gap-3 text-xs font-mono text-zinc-500 mb-6">
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            SYS_STATUS: ACTIVE
          </span>
          <span className="text-zinc-700">|</span>
          <span>DISCIPLINE: DISTRIBUTED SYSTEMS & AI RUNTIME</span>
          <span className="text-zinc-700 hidden sm:inline">|</span>
          <span className="hidden sm:inline">LOC: {HERO_DATA.location}</span>
        </div>

        {/* Name and Title */}
        <div className="space-y-2 mb-6">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight text-zinc-100 font-sans">
            {HERO_DATA.name}
          </h1>
          <p className="text-lg sm:text-xl font-mono text-zinc-400">
            {HERO_DATA.title}
          </p>
        </div>

        {/* Primary Systems Headline */}
        <div className="max-w-3xl mb-6">
          <p className="text-base sm:text-lg leading-relaxed text-zinc-300 font-normal">
            {HERO_DATA.headline}
          </p>
        </div>

        {/* Personal Sub-headline */}
        <div className="max-w-3xl mb-8">
          <p className="text-sm sm:text-base leading-relaxed text-zinc-400 font-sans">
            {HERO_DATA.subHeadline}
          </p>
        </div>

        {/* Action Controls & External Demonstration Link */}
        <div className="flex flex-wrap items-center gap-3 text-xs font-mono">
          <a
            href="#projects"
            className="px-4 py-2 rounded bg-zinc-100 text-zinc-950 font-medium hover:bg-white transition-colors"
          >
            View Systems Architecture ↓
          </a>
          <a
            href="/axioma"
            className="px-4 py-2 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-700/80 transition-colors flex items-center gap-1.5"
          >
            <span>Launch Axioma Governance Demo</span>
            <span className="text-zinc-400">↗</span>
          </a>
          <a
            href={HERO_DATA.links.github}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3.5 py-2 rounded bg-zinc-900/80 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border border-zinc-800 transition-colors"
          >
            GitHub ↗
          </a>
          <a
            href={HERO_DATA.links.linkedin}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3.5 py-2 rounded bg-zinc-900/80 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border border-zinc-800 transition-colors"
          >
            LinkedIn ↗
          </a>
        </div>
      </div>
    </section>
  );
}
