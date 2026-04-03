import { NavLink } from "react-router-dom";
import type { PropsWithChildren } from "react";

const navItems = [
  { to: "/", label: "Library" },
  { to: "/experiment", label: "Experiment" },
  { to: "/history", label: "History" },
  { to: "/compare", label: "Compare" },
  { to: "/monitor", label: "Monitor" }
];

export function AppShell({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen px-4 py-6 text-ink md:px-8">
      <div className="mx-auto grid max-w-7xl gap-6 md:grid-cols-[260px_minmax(0,1fr)]">
        <aside className="rounded-[28px] border border-black/10 bg-sand/80 p-6 shadow-panel backdrop-blur">
          <div className="mb-8">
            <p className="text-xs uppercase tracking-[0.35em] text-teal">Local-first AI Systems</p>
            <h1 className="mt-3 text-3xl font-semibold leading-tight">RAG Pipeline Lab</h1>
            <p className="mt-3 text-sm text-ink/70">
              Inspect ingestion, retrieval, reranking, grounded generation, and evaluation in one place.
            </p>
          </div>
          <nav className="space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  `block rounded-2xl px-4 py-3 text-sm transition ${
                    isActive ? "bg-ink text-white" : "bg-white/60 text-ink hover:bg-white"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </aside>
        <main>{children}</main>
      </div>
    </div>
  );
}
