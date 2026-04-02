export type ChunkStrategy = "fixed" | "overlap" | "semantic";

export interface PipelineConfig {
  chunk_strategy: ChunkStrategy;
  chunk_size: number;
  overlap: number;
  top_k: number;
  embedding_model?: string | null;
  generation_model?: string | null;
  rerank_enabled: boolean;
}

export interface DocumentDetail {
  id: string;
  filename: string;
  content_type: string;
  file_path: string;
  raw_text: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface RetrievedChunk {
  chunk_id: string;
  document_id: string;
  document_name: string;
  chunk_index: number;
  text: string;
  token_count: number;
  metadata: Record<string, unknown>;
  rank: number;
  citation: string;
  vector_score: number;
  rerank_score?: number | null;
}

export interface GenerationResult {
  prompt: string;
  answer: string;
  citations: string[];
}

export interface EvaluationResult {
  groundedness: number;
  answer_relevance: number;
  context_coverage: number;
  hallucination_flags: string[];
  summary: string;
}

export interface ExperimentResult {
  id: string;
  label?: string | null;
  question: string;
  config: PipelineConfig;
  retrieved_chunks: RetrievedChunk[];
  generation: GenerationResult;
  evaluation: EvaluationResult;
  created_at: string;
}

export interface ConfigOptions {
  embedding_models: string[];
  generation_models: string[];
  chunk_strategies: ChunkStrategy[];
}

export interface ComparisonResult {
  left: ExperimentResult;
  right: ExperimentResult;
}
