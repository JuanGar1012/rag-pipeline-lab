from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import documents, experiments, health
from app.chunking.strategies import ChunkingService
from app.config import get_settings
from app.dependencies import ServiceContainer
from app.embeddings.ollama import OllamaEmbeddingClient
from app.evaluation.service import EvaluationService
from app.generation.ollama import OllamaGenerationClient
from app.generation.service import GenerationService
from app.indexing.faiss_store import FaissIndexStore
from app.ingestion.parsers import DocumentParser
from app.ingestion.service import IngestionService
from app.pipeline import PipelineService
from app.retrieval.service import RetrievalService
from app.storage.database import Database
from app.storage.repositories import DocumentRepository, ExperimentRepository


def build_container() -> ServiceContainer:
    settings = get_settings()
    database = Database(settings.sqlite_path)
    database.init()

    document_repository = DocumentRepository(database)
    experiment_repository = ExperimentRepository(database)
    parser = DocumentParser()
    chunking_service = ChunkingService()
    index_store = FaissIndexStore(settings.index_dir)
    embedding_client = OllamaEmbeddingClient(settings.ollama_base_url)
    generation_client = OllamaGenerationClient(settings.ollama_base_url)

    ingestion_service = IngestionService(settings.upload_dir, document_repository, parser)
    retrieval_service = RetrievalService(
        chunking_service=chunking_service,
        embedding_client=embedding_client,
        index_store=index_store,
        default_embedding_model=settings.ollama_embedding_model,
    )
    generation_service = GenerationService(
        client=generation_client,
        default_generation_model=settings.ollama_chat_model,
    )
    evaluation_service = EvaluationService()
    pipeline_service = PipelineService(
        document_repository=document_repository,
        experiment_repository=experiment_repository,
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        evaluation_service=evaluation_service,
    )
    return ServiceContainer(
        settings=settings,
        database=database,
        document_repository=document_repository,
        experiment_repository=experiment_repository,
        ingestion_service=ingestion_service,
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        evaluation_service=evaluation_service,
        pipeline_service=pipeline_service,
        index_store=index_store,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = build_container()
    if container.settings.auto_seed and container.document_repository.count_documents() == 0:
        container.ingestion_service.seed_directory(container.settings.seed_docs_dir)
    app.state.container = container
    yield


app = FastAPI(title="RAG Pipeline Lab", version="0.1.0", lifespan=lifespan)
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(documents.router, prefix=settings.api_prefix)
app.include_router(experiments.router, prefix=settings.api_prefix)
