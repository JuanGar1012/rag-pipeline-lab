from dataclasses import dataclass

from fastapi import Request

from app.config import Settings
from app.evaluation.service import EvaluationService
from app.generation.service import GenerationService
from app.indexing.faiss_store import FaissIndexStore
from app.ingestion.service import IngestionService
from app.pipeline import PipelineService
from app.retrieval.service import RetrievalService
from app.storage.database import Database
from app.storage.repositories import DocumentRepository, ExperimentRepository


@dataclass
class ServiceContainer:
    settings: Settings
    database: Database
    document_repository: DocumentRepository
    experiment_repository: ExperimentRepository
    ingestion_service: IngestionService
    retrieval_service: RetrievalService
    generation_service: GenerationService
    evaluation_service: EvaluationService
    pipeline_service: PipelineService
    index_store: FaissIndexStore


def get_container(request: Request) -> ServiceContainer:
    return request.app.state.container
