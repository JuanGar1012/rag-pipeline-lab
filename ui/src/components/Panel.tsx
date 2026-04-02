import type { PropsWithChildren, ReactNode } from "react";

interface PanelProps extends PropsWithChildren {
  title: string;
  eyebrow?: string;
  action?: ReactNode;
  className?: string;
}

export function Panel({ title, eyebrow, action, className = "", children }: PanelProps) {
  return (
    <section className={`rounded-[28px] border border-black/10 bg-white/75 p-6 shadow-panel backdrop-blur ${className}`}>
      <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
        <div>
          {eyebrow ? <p className="text-xs uppercase tracking-[0.3em] text-coral">{eyebrow}</p> : null}
          <h2 className="mt-2 text-xl font-semibold">{title}</h2>
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}
