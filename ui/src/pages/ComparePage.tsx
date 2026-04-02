import { useEffect, useState } from "react";

import { ConfigPanel } from "../components/ConfigPanel";
import { DocumentPicker } from "../components/DocumentPicker";
import { Panel } from "../components/Panel";
import { RetrievalInspector } from "../components/RetrievalInspector";
import { api } from "../lib/api";
import { defaultConfig } from "../lib/defaults";
import type { ComparisonResult, ConfigOptions, DocumentDetail, PipelineConfig } from "../types";

export function ComparePage() {
  const [documents, setDocuments] = useState<DocumentDetail[]>([]);
  const [options, setOptions] = useState<ConfigOptions | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [label, setLabel] = useState("Chunking A/B");
  const [question, setQuestion] = useState("What knobs most directly affect retrieval precision in this corpus?");
  const [left, setLeft] = useState<PipelineConfig>(defaultConfig);
  const [right, setRight] = useState<PipelineConfig>({
    ...defaultConfig(),
    chunk_strategy: "semantic",
    chunk_size: 300,
    overlap: 20,
    rerank_enabled: false
  });
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const [docs, configOptions] = await Promise.all([api.listDocuments(), api.getConfigOptions()]);
        setDocuments(docs);
        setOptions(configOptions);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load comparison form.");
      }
    })();
  }, []);

  const runComparison = async () => {
    try {
      setLoading(true);
      setError(null);
      setComparison(
        await api.compareExperiments({
          label,
          question,
          document_ids: selectedIds,
          left,
          right
        })
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Comparison failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-6">
      <Panel eyebrow="Side-by-Side" title="Compare two pipeline configurations">
        <div className="grid gap-4 md:grid-cols-2">
          <label className="grid gap-2 text-sm">
            Comparison label
            <input
              className="rounded-2xl border border-black/10 bg-sand px-4 py-3 outline-none focus:border-coral"
              value={label}
              onChange={(event) => setLabel(event.target.value)}
            />
          </label>
          <label className="grid gap-2 text-sm">
            Shared question
            <input
              className="rounded-2xl border border-black/10 bg-sand px-4 py-3 outline-none focus:border-coral"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />
          </label>
        </div>
        <div className="mt-6">
          <DocumentPicker documents={documents} selectedIds={selectedIds} onChange={setSelectedIds} />
        </div>
        <button
          type="button"
          onClick={runComparison}
          disabled={loading}
          className="mt-6 rounded-2xl bg-ink px-4 py-3 text-sm font-medium text-white disabled:opacity-60"
        >
          {loading ? "Running comparison..." : "Run Comparison"}
        </button>
        {error ? <p className="mt-4 text-sm text-coral">{error}</p> : null}
      </Panel>

      <div className="grid gap-6 xl:grid-cols-2">
        <ConfigPanel config={left} options={options} onChange={setLeft} title="Configuration A" />
        <ConfigPanel config={right} options={options} onChange={setRight} title="Configuration B" />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <RetrievalInspector result={comparison?.left ?? null} title="Configuration A" />
        <RetrievalInspector result={comparison?.right ?? null} title="Configuration B" />
      </div>
    </div>
  );
}
