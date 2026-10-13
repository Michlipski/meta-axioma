import type { Metadata, Viewport } from "next";
import "./globals.css";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: "Michael Lipski — Full Stack Software Engineer",
  description:
    "Backend-focused engineer scaling distributed systems, enterprise platforms, and AI infrastructure.",
  keywords: [
    "Michael Lipski",
    "Software Engineer",
    "Full Stack",
    "Distributed Systems",
    "Go",
    "TypeScript",
    "Python",
    "Next.js",
    "Axioma",
  ],
  authors: [{ name: "Michael Lipski" }],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-zinc-950 text-zinc-100 antialiased selection:bg-zinc-800 selection:text-zinc-100">
        <div className="relative min-h-screen flex flex-col">
          {children}
        </div>
      </body>
    </html>
  );
}
