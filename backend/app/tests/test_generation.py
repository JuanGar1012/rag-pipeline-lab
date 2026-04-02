import pytest

from app.generation.service import GenerationService
from app.schemas import RetrievedChunk


class DummyGenerator:
    async def generate(self, prompt: str, model: str) -> str:
        return f"Answer with citation [rag-overview-c0] using {model}"


@pytest.mark.asyncio
async def test_generation_service_extracts_citations():
    service = GenerationService(client=DummyGenerator(), default_generation_model="demo-model")
    chunks = [
        RetrievedChunk(
            chunk_id="doc:0",
            document_id="doc",
            document_name="rag-overview.md",
            chunk_index=0,
            text="RAG combines search and generation.",
            token_count=6,
            metadata={},
            rank=1,
            citation="[rag-overview-c0]",
            vector_score=0.9,
            rerank_score=0.94,
        )
    ]

    result = await service.grounded_answer(question="What is RAG?", chunks=chunks, model=None)

    assert "[rag-overview-c0]" in result.answer
    assert result.citations == ["[rag-overview-c0]"]
