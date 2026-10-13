# Michael Lipski — Full Stack Software Engineer Portfolio

> **Generation Origin:** Generation 2 ($G_2$ Autonomous Domain Compiler)  
> **Framework:** Next.js (App Router), TypeScript, Tailwind CSS  
> **Deployment Target:** Vercel (Edge Multi-Zone Rewrites + Static Export)

---

## 1. Architectural Highlights

- **Static Export Compatible:** Configured with `output: 'export'` in `next.config.mjs`. Compiles 100% static HTML/CSS/JS into `out/` for instant CDN delivery and zero server cold-start latency.
- **Vercel Multi-Zone Rewrites:** Includes root `vercel.json` with edge rewrites proxying `/axioma/:path*` to the external Axioma showcase deployment seamlessly without breaking the single-domain feel.
- **Design System:** Monochromatic slate/zinc palette (`zinc-950`, `zinc-900`, `zinc-100`, `border-zinc-800`), academic preprint typography, smooth scroll anchor navigation, and zero distracting animations.
- **Modular Beehive Systems Architecture Slot:** Reserved architectural blueprint component ready for follow-up systems deep dive and interactive Q&A.

---

## 2. Getting Started

### Local Development
```bash
npm run dev
```
Visit [http://localhost:3000](http://localhost:3000) to view the portfolio.

### Static Build & Verification
```bash
npm run build
```
Generates production-ready static assets in `out/`.

### Vercel Deployment
Deploy directly to Vercel via Git integration or CLI. Vercel automatically respects:
- `vercel.json` for edge rewrite routing (`/axioma/:path*`).
- `next.config.mjs` for static optimization.
