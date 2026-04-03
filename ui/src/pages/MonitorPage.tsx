import { useEffect, useState } from "react";

import { Panel } from "../components/Panel";
import { api } from "../lib/api";
import { formatTimestamp } from "../lib/format";
import type { DriftMonitorResponse, DriftStatus } from "../types";

const statusStyles: Record<DriftStatus, string> = {
  healthy: "bg-teal/10 text-teal",
  watch: "bg-yellow-100 text-yellow-700",
  alert: "bg-coral/10 text-coral"
};

export function MonitorPage() {
  const [monitor, setMonitor] = useState<DriftMonitorResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        setMonitor(await api.getDriftMonitor());
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load drift monitor.");
      }
    })();
  }, []);

  return (
    <div className="grid gap-6">
      <Panel eyebrow="Recommendation" title="Monitor semantic drift, not just raw log volume">
        <p className="max-w-4xl text-sm leading-7 text-ink/75">
          {monitor?.recommendation ??
            "Track semantic drift against a rolling baseline per experiment family and combine it with grounding stability metrics before trusting a prompt or model change."}
        </p>
        {error ? <p className="mt-4 text-sm text-coral">{error}</p> : null}
      </Panel>

      {!monitor?.reports.length ? (
        <Panel eyebrow="Status" title="No drift series yet">
          <p className="text-sm text-ink/70">
            Run at least two experiments with the same label to build a monitoring baseline.
          </p>
        </Panel>
      ) : null}

      {monitor?.reports.map((report) => (
        <Panel
          key={report.family}
          eyebrow="Concept Drift"
          title={report.family}
          action={
            <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${statusStyles[report.status]}`}>
              {report.status}
            </span>
          }
        >
          <div className="grid gap-3 text-sm text-ink/75 md:grid-cols-3">
            <p>Runs: {report.run_count}</p>
            <p>Latest: {formatTimestamp(report.latest_created_at)}</p>
            <p>Question: {report.latest_question}</p>
          </div>
          <p className="mt-4 rounded-2xl bg-sand p-4 text-sm leading-7">{report.summary}</p>
          {report.alerts.length ? (
            <div className="mt-4 rounded-2xl border border-coral/20 bg-coral/5 p-4 text-sm">
              <p className="font-semibold">Current alerts</p>
              <ul className="mt-2 space-y-2">
                {report.alerts.map((alert) => (
                  <li key={alert}>{alert}</li>
                ))}
              </ul>
            </div>
          ) : null}
          <div className="mt-5 overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="text-ink/55">
                <tr>
                  <th className="pb-3">Timestamp</th>
                  <th className="pb-3">Drift</th>
                  <th className="pb-3">Alignment</th>
                  <th className="pb-3">Grounding Drop</th>
                  <th className="pb-3">Citation Density</th>
                  <th className="pb-3">Retrieval Overlap</th>
                  <th className="pb-3">Flags</th>
                </tr>
              </thead>
              <tbody>
                {report.series.map((point) => (
                  <tr key={point.experiment_id} className="border-t border-black/10">
                    <td className="py-3">{formatTimestamp(point.created_at)}</td>
                    <td className="py-3">{point.semantic_drift}</td>
                    <td className="py-3">{point.question_alignment}</td>
                    <td className="py-3">{point.grounding_drop}</td>
                    <td className="py-3">{point.citation_density}</td>
                    <td className="py-3">{point.retrieval_overlap}</td>
                    <td className="py-3">{point.hallucination_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      ))}
    </div>
  );
}
