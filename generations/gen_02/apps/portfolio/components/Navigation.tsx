"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";

export default function Navigation() {
  const [scrolled, setScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState("about");

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);

      const sections = ["about", "competencies", "projects", "experience", "beehive-architecture"];
      const scrollPosition = window.scrollY + 120;

      for (const sectionId of sections) {
        const el = document.getElementById(sectionId);
        if (el) {
          const top = el.offsetTop;
          const height = el.offsetHeight;
          if (scrollPosition >= top && scrollPosition < top + height) {
            setActiveSection(sectionId);
            break;
          }
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      className={`sticky top-0 z-50 transition-all duration-200 border-b ${
        scrolled
          ? "bg-zinc-950/90 backdrop-blur-md border-zinc-800 shadow-sm"
          : "bg-zinc-950/60 backdrop-blur-sm border-zinc-800/40"
      }`}
    >
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <Link
          href="#about"
          className="group flex items-center space-x-2 text-zinc-100 font-mono text-sm tracking-tight"
        >
          <span className="font-semibold text-zinc-200 group-hover:text-white transition-colors">
            michael_lipski
          </span>
          <span className="text-zinc-600 hidden sm:inline">::</span>
          <span className="text-zinc-400 text-xs hidden sm:inline font-sans">
            full_stack_engineer
          </span>
        </Link>

        <nav className="flex items-center space-x-1 sm:space-x-3 text-xs font-mono">
          <a
            href="#competencies"
            className={`px-2.5 py-1.5 rounded transition-colors ${
              activeSection === "competencies"
                ? "text-zinc-100 bg-zinc-800/80"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
            }`}
          >
            01.competencies
          </a>
          <a
            href="#projects"
            className={`px-2.5 py-1.5 rounded transition-colors ${
              activeSection === "projects"
                ? "text-zinc-100 bg-zinc-800/80"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
            }`}
          >
            02.projects
          </a>
          <a
            href="#experience"
            className={`px-2.5 py-1.5 rounded transition-colors ${
              activeSection === "experience"
                ? "text-zinc-100 bg-zinc-800/80"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
            }`}
          >
            03.experience
          </a>
          <a
            href="#beehive-architecture"
            className={`hidden md:inline-block px-2.5 py-1.5 rounded transition-colors ${
              activeSection === "beehive-architecture"
                ? "text-zinc-100 bg-zinc-800/80"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
            }`}
          >
            04.beehive_stack
          </a>

          <a
            href="/axioma"
            className="ml-2 inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 hover:text-white border border-zinc-700/80 transition-colors"
            title="Interactive Axioma Demo Proxy (/axioma)"
          >
            <span>/axioma</span>
            <span className="text-zinc-400 text-[10px]">↗</span>
          </a>
        </nav>
      </div>
    </header>
  );
}
