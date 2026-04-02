from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.evaluation.service import EvaluationService
from app.generation.service import GenerationService
from app.retrieval.service import RetrievalService
from app.schemas import ComparisonResult, ExperimentResult, ExperimentRunRequest, PipelineConfig
from app.storage.repositories import DocumentRepository, ExperimentRepository


class PipelineService:
    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        experiment_repository: ExperimentRepository,
        retrieval_service: RetrievalService,
        generation_service: GenerationService,
        evaluation_service: EvaluationService,
    ):
        self.document_repository = document_repository
        self.experiment_repository = experiment_repository
        self.retrieval_service = retrieval_service
        self.generation_service = generation_service
        self.evaluation_service = evaluation_service

    async def run(self, request: ExperimentRunRequest) -> ExperimentResult:
        documents = self.document_repository.get_documents(request.document_ids)
        if not documents:
            raise ValueError("No documents available for retrieval. Upload or seed documents first.")

        retrieved = await self.retrieval_service.retrieve(
            question=request.question,
            documents=documents,
            config=request.config,
        )
        generation = await self.generation_service.grounded_answer(
            question=request.question,
            chunks=retrieved,
            model=request.config.generation_model,
        )
        evaluation = self.evaluation_service.evaluate(
            question=request.question,
            chunks=retrieved,
            generation=generation,
        )

        result = ExperimentResult(
            id=str(uuid4()),
            label=request.label,
            question=request.question,
            config=request.config,
            retrieved_chunks=retrieved,
            generation=generation,
            evaluation=evaluation,
            created_at=datetime.now(UTC).isoformat(),
        )
        self.experiment_repository.save_experiment(
            label=request.label,
            question=request.question,
            config_json=request.config.model_dump_json(),
            result=result,
        )
        return result

    async def compare(
        self,
        *,
        label: str | None,
        question: str,
        document_ids: list[str],
        left: PipelineConfig,
        right: PipelineConfig,
    ) -> ComparisonResult:
        left_result = await self.run(
            ExperimentRunRequest(
                label=f"{label or 'Comparison'} - A",
                question=question,
                document_ids=document_ids,
                config=left,
            )
        )
        right_result = await self.run(
            ExperimentRunRequest(
                label=f"{label or 'Comparison'} - B",
                question=question,
                document_ids=document_ids,
                config=right,
            )
        )
        return ComparisonResult(left=left_result, right=right_result)
