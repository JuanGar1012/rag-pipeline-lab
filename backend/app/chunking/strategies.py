from __future__ import annotations

import math
import re

from app.schemas import ChunkRecord, ChunkStrategy, DocumentDetail, PipelineConfig


TOKEN_RE = re.compile(r"\S+")


def token_count(text: str) -> int:
    return len(TOKEN_RE.findall(text))


class ChunkingService:
    def chunk_documents(
        self,
        documents: list[DocumentDetail],
        config: PipelineConfig,
    ) -> list[ChunkRecord]:
        chunks: list[ChunkRecord] = []
        for document in documents:
            words = TOKEN_RE.findall(document.raw_text)
            if not words:
                continue
            if config.chunk_strategy == ChunkStrategy.FIXED:
                spans = self._fixed_spans(words, config.chunk_size)
            elif config.chunk_strategy == ChunkStrategy.OVERLAP:
                spans = self._overlap_spans(words, config.chunk_size, config.overlap)
            else:
                spans = self._semanticish_spans(document.raw_text, config.chunk_size)

            for index, chunk_text in enumerate(spans):
                normalized = chunk_text.strip()
                if not normalized:
                    continue
                chunks.append(
                    ChunkRecord(
                        chunk_id=f"{document.id}:{index}",
                        document_id=document.id,
                        document_name=document.filename,
                        chunk_index=index,
                        text=normalized,
                        token_count=token_count(normalized),
                        metadata={
                            "strategy": config.chunk_strategy.value,
                            "estimated_chunks": len(spans),
                            "density": round(token_count(normalized) / max(config.chunk_size, 1), 3),
                        },
                    )
                )
        return chunks

    @staticmethod
    def _fixed_spans(words: list[str], chunk_size: int) -> list[str]:
        return [" ".join(words[index : index + chunk_size]) for index in range(0, len(words), chunk_size)]

    @staticmethod
    def _overlap_spans(words: list[str], chunk_size: int, overlap: int) -> list[str]:
        step = max(1, chunk_size - overlap)
        spans = []
        for index in range(0, len(words), step):
            window = words[index : index + chunk_size]
            if not window:
                continue
            spans.append(" ".join(window))
            if index + chunk_size >= len(words):
                break
        return spans

    @staticmethod
    def _semanticish_spans(text: str, chunk_size: int) -> list[str]:
        paragraphs = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
        if not paragraphs:
            return [text]

        chunks: list[str] = []
        current: list[str] = []
        current_tokens = 0
        threshold = max(40, math.floor(chunk_size * 0.8))

        for paragraph in paragraphs:
            paragraph_tokens = token_count(paragraph)
            if current and current_tokens + paragraph_tokens > chunk_size:
                chunks.append("\n\n".join(current))
                current = [paragraph]
                current_tokens = paragraph_tokens
                continue
            current.append(paragraph)
            current_tokens += paragraph_tokens
            if current_tokens >= threshold:
                chunks.append("\n\n".join(current))
                current = []
                current_tokens = 0

        if current:
            chunks.append("\n\n".join(current))
        return chunks
