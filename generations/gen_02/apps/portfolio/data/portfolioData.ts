export interface Project {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  tags: string[];
  demoUrl?: string;
  sourceUrl?: string;
  demoLabel?: string;
  metrics?: { label: string; value: string }[];
}

export interface Experience {
  company: string;
  role: string;
  period?: string;
  summary: string;
  achievements: string[];
  technologies: string[];
  hasArchitectureDiagram?: boolean;
}

export interface CompetencyGroup {
  category: string;
  items: string[];
}

export const HERO_DATA = {
  name: "Michael Lipski",
  title: "Full Stack Software Engineer",
  headline:
    "I'm a backend-focused engineer who loves untangling complex distributed systems. I have a proven track record scaling enterprise platforms and a deep curiosity for how we can better architect emerging AI infrastructure.",
  subHeadline:
    "When I'm not explicitly designing systems, I'm usually ice dancing, playing piano, or digging into a good fantasy novel — exploring non-technical systems to draw inspiration from.",
  status: "Available for high-leverage systems & AI engineering",
  location: "Vancouver, Canada / Remote",
  links: {
    github: "https://github.com/michlipski",
    linkedin: "https://www.linkedin.com/in/michlipski",
    email: "mailto:michlipski@gmail.com",
    demo: "/axioma",
  },
};

export const COMPETENCIES: CompetencyGroup[] = [
  {
    category: "Languages",
    items: ["Go", "Python", "TypeScript / JavaScript", "SQL"],
  },
  {
    category: "Infrastructure",
    items: [
      "Kubernetes (GKE)",
      "Docker",
      "CI/CD",
      "RabbitMQ",
      "PostgreSQL",
    ],
  },
  {
    category: "Domains",
    items: [
      "Distributed Systems",
      "API Design",
      "Systems Modeling",
      "AI Evaluation Context",
    ],
  },
];

export const PROJECTS: Project[] = [
  {
    id: "axioma",
    title: "Axioma",
    subtitle: "Dual-FSM Zero-Trust Governance Kernel",
    description:
      "A zero-trust LLM governance architecture utilizing dual finite state machine boundaries to enforce secure, constrained agentic execution. Built with Next.js and TypeScript.",
    tags: ["Next.js", "TypeScript", "Finite State Machines", "Zero-Trust", "LLM Security"],
    demoUrl: "/axioma",
    demoLabel: "Launch Interactive Demo (/axioma)",
    metrics: [
      { label: "State Isolation", value: "Dual FSM Enclaves" },
      { label: "Deterministic Halt", value: "0 Clock Cycles" },
      { label: "Substrate", value: "Next.js / TypeScript" },
    ],
  },
  {
    id: "meta-axioma",
    title: "Meta-Axioma",
    subtitle: "Recursive Axiomatic Compiler & Rule Registry",
    description:
      "A Python-based evaluation engine for researching and constructing self-assembling software axioms, featuring strict human-in-the-loop oversight and persistent rule registries.",
    tags: ["Python 3.14", "AsyncIO", "Category Theory", "HITL Oracles", "Rule Registries"],
    metrics: [
      { label: "Axiom Registry", value: "16 Formal Invariants" },
      { label: "Decay Model", value: "Thermodynamic Landauer" },
      { label: "Verification Gate", value: "Anti-Hubris Enclave" },
    ],
  },
];

export const EXPERIENCES: Experience[] = [
  {
    company: "Beehive AI",
    role: "Software Engineer",
    summary:
      "Early engineer at a venture-backed AI SaaS startup. Architected high-throughput microservices and enterprise integrations across Go, React, and PostgreSQL, scaling backend ingestion pipelines to support over 10 million customer records.",
    achievements: [
      "Architected backend ingestion pipelines from scratch in Go, scaling throughput to handle >10M customer records with sub-second ingestion latency.",
      "Designed resilient asynchronous event streaming and processing queues to isolate high-volume ingest spikes from downstream indexing services.",
      "Engineered full-stack enterprise integrations combining high-reliability Go microservices with reactive React interfaces and PostgreSQL relational schemas.",
    ],
    technologies: ["Go", "React", "PostgreSQL", "RabbitMQ", "Microservices", "Docker"],
    hasArchitectureDiagram: true,
  },
  {
    company: "Globality, Inc.",
    role: "Software Engineer II",
    summary:
      "Designed customer-facing full-stack features using React, GraphQL, and Python microservices deployed across AWS ECS/EKS.",
    achievements: [
      "Engineered customer-facing full-stack features across modern React client applications and schema-first GraphQL API gateways.",
      "Developed containerized Python microservices deployed across AWS ECS and EKS with strict uptime and resilience SLAs.",
      "Collaborated with cross-functional product and systems teams to model complex procurement and enterprise data entities.",
    ],
    technologies: ["React", "GraphQL", "Python", "AWS ECS", "AWS EKS", "Docker"],
  },
];
