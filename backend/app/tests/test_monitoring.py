import pytest

from app.monitoring.service import DriftMonitoringService
from app.schemas import EvaluationResult, ExperimentResult, GenerationResult, PipelineConfig, RetrievedChunk


class FakeEmbeddingClient:
    async def embed_texts(self, texts: list[str], model: str) -> list[list[float]]:
        mapping = {
            "steady answer one": [1.0, 0.0],
            "steady answer two": [0.98, 0.02],
            "drifted answer": [0.0, 1.0],
            "steady question": [1.0, 0.0],
        }
        return [mapping[text] for text in texts]


def make_run(run_id: str, answer: str, groundedness: float, flags: list[str], created_at: str) -> ExperimentResult:
    chunk = RetrievedChunk(
        chunk_id=f"{run_id}:0",
        document_id="doc-1",
        document_name="rag.md",
        chunk_index=0,
        text="RAG systems should stay grounded in retrieved evidence.",
        token_count=8,
        metadata={},
        rank=1,
        citation="[rag-c0]",
        vector_score=0.9,
        rerank_score=0.91,
    )
    return ExperimentResult(
        id=run_id,
        label="Support QA",
        question="steady question",
        config=PipelineConfig(),
        retrieved_chunks=[chunk],
        generation=GenerationResult(prompt="prompt", answer=answer, citations=["[rag-c0]"] if not flags else []),
        evaluation=EvaluationResult(
            groundedness=groundedness,
            answer_relevance=0.8,
            context_coverage=0.7,
            hallucination_flags=flags,
            summary="summary",
        ),
        created_at=created_at,
    )


@pytest.mark.asyncio
async def test_monitoring_service_flags_semantic_drift():
    service = DriftMonitoringService(FakeEmbeddingClient(), "fake-model")
    experiments = [
        make_run("run-1", "steady answer one", 0.9, [], "2026-04-01T10:00:00Z"),
        make_run("run-2", "steady answer two", 0.88, [], "2026-04-01T11:00:00Z"),
        make_run("run-3", "drifted answer", 0.55, ["Low-context support"], "2026-04-01T12:00:00Z"),
    ]

    result = await service.analyze(experiments)

    assert len(result.reports) == 1
    report = result.reports[0]
    assert report.status == "alert"
    assert any("Semantic drift" in alert for alert in report.alerts)
