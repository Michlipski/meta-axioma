import React from "react";
import Navigation from "@/components/Navigation";
import HeroSection from "@/components/HeroSection";
import CompetenciesSection from "@/components/CompetenciesSection";
import ProjectsSection from "@/components/ProjectsSection";
import ExperienceSection from "@/components/ExperienceSection";
import BeehiveArchitectureSlot from "@/components/BeehiveArchitectureSlot";
import FooterSection from "@/components/FooterSection";

export default function HomePage() {
  return (
    <>
      <Navigation />
      <main className="flex-1">
        <HeroSection />
        <CompetenciesSection />
        <ProjectsSection />
        <ExperienceSection />
        <BeehiveArchitectureSlot />
      </main>
      <FooterSection />
    </>
  );
}
