import type { ConfigOptions, PipelineConfig } from "../types";

interface ConfigPanelProps {
  config: PipelineConfig;
  options: ConfigOptions | null;
  onChange: (next: PipelineConfig) => void;
  title: string;
}

export function ConfigPanel({ config, options, onChange, title }: ConfigPanelProps) {
  const setField = <K extends keyof PipelineConfig>(key: K, value: PipelineConfig[K]) => {
    onChange({ ...config, [key]: value });
  };

  const inputClassName =
    "rounded-2xl border border-black/10 bg-sand px-4 py-3 text-sm outline-none transition focus:border-coral";

  return (
    <div className="rounded-[24px] border border-black/10 bg-white/60 p-5">
      <h3 className="text-lg font-semibold">{title}</h3>
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <label className="grid gap-2 text-sm">
          Chunk strategy
          <select
            className={inputClassName}
            value={config.chunk_strategy}
            onChange={(event) => setField("chunk_strategy", event.target.value as PipelineConfig["chunk_strategy"])}
          >
            {(options?.chunk_strategies ?? ["fixed", "overlap", "semantic"]).map((strategy) => (
              <option key={strategy} value={strategy}>
                {strategy}
              </option>
            ))}
          </select>
        </label>
        <label className="grid gap-2 text-sm">
          Top-K
          <input
            className={inputClassName}
            type="number"
            min={1}
            max={12}
            value={config.top_k}
            onChange={(event) => setField("top_k", Number(event.target.value))}
          />
        </label>
        <label className="grid gap-2 text-sm">
          Chunk size
          <input
            className={inputClassName}
            type="number"
            min={80}
            max={1200}
            value={config.chunk_size}
            onChange={(event) => setField("chunk_size", Number(event.target.value))}
          />
        </label>
        <label className="grid gap-2 text-sm">
          Overlap
          <input
            className={inputClassName}
            type="number"
            min={0}
            max={400}
            value={config.overlap}
            onChange={(event) => setField("overlap", Number(event.target.value))}
          />
        </label>
        <label className="grid gap-2 text-sm">
          Embedding model
          <select
            className={inputClassName}
            value={config.embedding_model ?? ""}
            onChange={(event) => setField("embedding_model", event.target.value)}
          >
            {(options?.embedding_models ?? ["nomic-embed-text"]).map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </label>
        <label className="grid gap-2 text-sm">
          Generation model
          <select
            className={inputClassName}
            value={config.generation_model ?? ""}
            onChange={(event) => setField("generation_model", event.target.value)}
          >
            {(options?.generation_models ?? ["llama3.1"]).map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label className="mt-4 flex items-center gap-3 text-sm">
        <input
          type="checkbox"
          checked={config.rerank_enabled}
          onChange={(event) => setField("rerank_enabled", event.target.checked)}
        />
        Enable lexical reranking pass
      </label>
    </div>
  );
}
