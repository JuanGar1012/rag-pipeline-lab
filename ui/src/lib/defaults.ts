import type { PipelineConfig } from "../types";

export const defaultConfig = (): PipelineConfig => ({
  chunk_strategy: "overlap",
  chunk_size: 220,
  overlap: 40,
  top_k: 5,
  embedding_model: "nomic-embed-text",
  generation_model: "llama3.1",
  rerank_enabled: true
});
