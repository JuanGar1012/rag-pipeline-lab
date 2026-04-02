import { useEffect, useState } from "react";

import { Panel } from "../components/Panel";
import { RetrievalInspector } from "../components/RetrievalInspector";
import { formatTimestamp } from "../lib/format";
import { api } from "../lib/api";
import type { ExperimentResult } from "../types";

export function HistoryPage() {
  const [experiments, setExperiments] = useState<ExperimentResult[]>([]);
  const [selected, setSelected] = useState<ExperimentResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const history = await api.listExperiments();
        setExperiments(history);
        setSelected(history[0] ?? null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load experiment history.");
      }
    })();
  }, []);

  return (
    <div className="grid gap-6 xl:grid-cols-[380px_minmax(0,1fr)]">
      <Panel eyebrow="History" title="Review past experiment runs">
        {error ? <p className="text-sm text-coral">{error}</p> : null}
        <div className="grid gap-3">
          {experiments.map((experiment) => (
            <button
              key={experiment.id}
              type="button"
              onClick={() => setSelected(experiment)}
              className={`rounded-2xl border px-4 py-4 text-left ${
                selected?.id === experiment.id ? "border-ink bg-ink text-white" : "border-black/10 bg-sand"
              }`}
            >
              <p className="font-medium">{experiment.label || experiment.question}</p>
              <p className={`mt-1 text-sm ${selected?.id === experiment.id ? "text-white/70" : "text-ink/60"}`}>
                {formatTimestamp(experiment.created_at)}
              </p>
              <p className={`mt-3 text-xs uppercase tracking-[0.2em] ${selected?.id === experiment.id ? "text-white/70" : "text-ink/50"}`}>
                {experiment.config.chunk_strategy} / top-k {experiment.config.top_k}
              </p>
            </button>
          ))}
        </div>
      </Panel>
      <RetrievalInspector result={selected} title="Run Details" />
    </div>
  );
}
