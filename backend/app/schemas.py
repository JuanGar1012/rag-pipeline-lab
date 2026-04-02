from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ChunkStrategy(str, Enum):
    FIXED = "fixed"
    OVERLAP = "overlap"
    SEMANTIC = "semantic"


class PipelineConfig(BaseModel):
    chunk_strategy: ChunkStrategy = ChunkStrategy.OVERLAP
    chunk_size: int = Field(default=220, ge=80, le=1200)
    overlap: int = Field(default=40, ge=0, le=400)
    top_k: int = Field(default=5, ge=1, le=12)
    embedding_model: str | None = None
    generation_model: str | None = None
    rerank_enabled: bool = True


class DocumentRecord(BaseModel):
    id: str
    filename: str
    content_type: str
    file_path: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class DocumentDetail(DocumentRecord):
    raw_text: str


class ChunkRecord(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    chunk_index: int
    text: str
    token_count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievedChunk(ChunkRecord):
    rank: int
    citation: str
    vector_score: float
    rerank_score: float | None = None


class EvaluationResult(BaseModel):
    groundedness: float
    answer_relevance: float
    context_coverage: float
    hallucination_flags: list[str] = Field(default_factory=list)
    summary: str


class GenerationResult(BaseModel):
    prompt: str
    answer: str
    citations: list[str] = Field(default_factory=list)


class ExperimentResult(BaseModel):
    id: str
    label: str | None = None
    question: str
    config: PipelineConfig
    retrieved_chunks: list[RetrievedChunk]
    generation: GenerationResult
    evaluation: EvaluationResult
    created_at: str


class ExperimentRunRequest(BaseModel):
    label: str | None = None
    question: str = Field(min_length=4)
    document_ids: list[str] = Field(default_factory=list)
    config: PipelineConfig = Field(default_factory=PipelineConfig)


class ComparisonRunRequest(BaseModel):
    label: str | None = None
    question: str = Field(min_length=4)
    document_ids: list[str] = Field(default_factory=list)
    left: PipelineConfig
    right: PipelineConfig


class ComparisonResult(BaseModel):
    left: ExperimentResult
    right: ExperimentResult


class ConfigOptions(BaseModel):
    embedding_models: list[str]
    generation_models: list[str]
    chunk_strategies: list[ChunkStrategy]


class HealthResponse(BaseModel):
    status: str
