import { useEffect, useState } from "react";

import { ConfigPanel } from "../components/ConfigPanel";
import { DocumentPicker } from "../components/DocumentPicker";
import { Panel } from "../components/Panel";
import { RetrievalInspector } from "../components/RetrievalInspector";
import { api } from "../lib/api";
import { defaultConfig } from "../lib/defaults";
import type { ConfigOptions, DocumentDetail, ExperimentResult, PipelineConfig } from "../types";

export function ExperimentPage() {
  const [documents, setDocuments] = useState<DocumentDetail[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [options, setOptions] = useState<ConfigOptions | null>(null);
  const [config, setConfig] = useState<PipelineConfig>(defaultConfig);
  const [label, setLabel] = useState("Baseline RAG Run");
  const [question, setQuestion] = useState("How does this RAG pipeline expose retrieval quality to the user?");
  const [result, setResult] = useState<ExperimentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const [docs, configOptions] = await Promise.all([api.listDocuments(), api.getConfigOptions()]);
        setDocuments(docs);
        setOptions(configOptions);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load experiment form.");
      }
    })();
  }, []);

  const runExperiment = async () => {
    try {
      setLoading(true);
      setError(null);
      const next = await api.runExperiment({
        label,
        question,
        document_ids: selectedIds,
        config
      });
      setResult(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Experiment run failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[420px_minmax(0,1fr)]">
      <div className="grid gap-6">
        <Panel eyebrow="New Experiment" title="Configure retrieval and generation">
          <div className="grid gap-4">
            <label className="grid gap-2 text-sm">
              Run label
              <input
                className="rounded-2xl border border-black/10 bg-sand px-4 py-3 outline-none focus:border-coral"
                value={label}
                onChange={(event) => setLabel(event.target.value)}
              />
            </label>
            <label className="grid gap-2 text-sm">
              Question
              <textarea
                className="min-h-28 rounded-2xl border border-black/10 bg-sand px-4 py-3 outline-none focus:border-coral"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
              />
            </label>
          </div>
        </Panel>

        <Panel eyebrow="Scope" title="Select source documents">
          <p className="mb-4 text-sm text-ink/70">Leave all unchecked to search across the full document library.</p>
          <DocumentPicker documents={documents} selectedIds={selectedIds} onChange={setSelectedIds} />
        </Panel>

        <Panel eyebrow="Controls" title="Pipeline configuration">
          <ConfigPanel config={config} options={options} onChange={setConfig} title="Retriever and generator settings" />
          <button
            type="button"
            onClick={runExperiment}
            disabled={loading}
            className="mt-5 w-full rounded-2xl bg-ink px-4 py-3 text-sm font-medium text-white disabled:opacity-60"
          >
            {loading ? "Running pipeline..." : "Run Experiment"}
          </button>
          {error ? <p className="mt-4 text-sm text-coral">{error}</p> : null}
        </Panel>
      </div>

      <RetrievalInspector result={result} />
    </div>
  );
}
