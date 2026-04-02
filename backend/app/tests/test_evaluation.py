from app.evaluation.service import EvaluationService
from app.schemas import GenerationResult, RetrievedChunk


def test_evaluation_flags_missing_citations():
    service = EvaluationService()
    chunks = [
        RetrievedChunk(
            chunk_id="doc:0",
            document_id="doc",
            document_name="doc.txt",
            chunk_index=0,
            text="RAG systems assemble prompts from retrieved evidence chunks.",
            token_count=9,
            metadata={},
            rank=1,
            citation="[doc-c0]",
            vector_score=0.9,
            rerank_score=0.91,
        )
    ]
    result = service.evaluate(
        question="How do RAG systems use context?",
        chunks=chunks,
        generation=GenerationResult(
            prompt="prompt",
            answer="RAG systems use retrieved evidence chunks to build a prompt.",
            citations=[],
        ),
    )

    assert result.groundedness > 0
    assert any("No inline citations" in flag for flag in result.hallucination_flags)
