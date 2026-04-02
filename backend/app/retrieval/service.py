from __future__ import annotations

import hashlib
import json
import re

from app.chunking.strategies import ChunkingService
from app.embeddings.base import EmbeddingClient
from app.indexing.faiss_store import FaissIndexStore
from app.schemas import DocumentDetail, PipelineConfig, RetrievedChunk


WORD_RE = re.compile(r"\b\w+\b")


def _safe_doc_stem(filename: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9]+", "-", filename.rsplit(".", 1)[0]).strip("-")
    return safe or "doc"


class RetrievalService:
    def __init__(
        self,
        chunking_service: ChunkingService,
        embedding_client: EmbeddingClient,
        index_store: FaissIndexStore,
        default_embedding_model: str,
    ):
        self.chunking_service = chunking_service
        self.embedding_client = embedding_client
        self.index_store = index_store
        self.default_embedding_model = default_embedding_model

    async def retrieve(
        self,
        *,
        question: str,
        documents: list[DocumentDetail],
        config: PipelineConfig,
    ) -> list[RetrievedChunk]:
        chunks = self.chunking_service.chunk_documents(documents, config)
        if not chunks:
            return []

        embedding_model = config.embedding_model or self.default_embedding_model
        index_key = self._index_key(documents, config, embedding_model)
        embeddings = await self.embedding_client.embed_texts([chunk.text for chunk in chunks], embedding_model)
        self.index_store.build(index_key, embeddings, chunks)

        query_embedding = (await self.embedding_client.embed_texts([question], embedding_model))[0]
        candidate_count = config.top_k * 2 if config.rerank_enabled else config.top_k
        matches = self.index_store.search(index_key, query_embedding, candidate_count)
        ranked = self._rerank(question, matches) if config.rerank_enabled else [
            (chunk, score, None) for chunk, score in matches
        ]

        retrieved: list[RetrievedChunk] = []
        for rank, (chunk, vector_score, rerank_score) in enumerate(ranked[: config.top_k], start=1):
            retrieved.append(
                RetrievedChunk(
                    **chunk.model_dump(),
                    rank=rank,
                    citation=f"[{_safe_doc_stem(chunk.document_name)}-c{chunk.chunk_index}]",
                    vector_score=round(vector_score, 4),
                    rerank_score=round(rerank_score, 4) if rerank_score is not None else None,
                )
            )
        return retrieved

    def _index_key(
        self,
        documents: list[DocumentDetail],
        config: PipelineConfig,
        embedding_model: str,
    ) -> str:
        payload = {
            "documents": sorted(document.id for document in documents),
            "strategy": config.chunk_strategy.value,
            "chunk_size": config.chunk_size,
            "overlap": config.overlap,
            "embedding_model": embedding_model,
        }
        return hashlib.sha1(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]

    def _rerank(
        self,
        question: str,
        matches: list[tuple[object, float]],
    ) -> list[tuple[object, float, float]]:
        scored: list[tuple[object, float, float]] = []
        for chunk, vector_score in matches:
            lexical_score = self._lexical_overlap(question, chunk.text)
            combined = (vector_score * 0.7) + (lexical_score * 0.3)
            scored.append((chunk, vector_score, combined))
        scored.sort(key=lambda item: item[2], reverse=True)
        return scored

    @staticmethod
    def _lexical_overlap(question: str, text: str) -> float:
        q_tokens = set(WORD_RE.findall(question.lower()))
        t_tokens = set(WORD_RE.findall(text.lower()))
        if not q_tokens or not t_tokens:
            return 0.0
        return len(q_tokens & t_tokens) / len(q_tokens)
