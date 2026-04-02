from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import ServiceContainer, get_container
from app.schemas import ChunkStrategy, ComparisonResult, ComparisonRunRequest, ConfigOptions, ExperimentResult, ExperimentRunRequest

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("", response_model=list[ExperimentResult])
async def list_experiments(
    container: ServiceContainer = Depends(get_container),
) -> list[ExperimentResult]:
    return container.experiment_repository.list_experiments()


@router.get("/config/options", response_model=ConfigOptions)
async def config_options(
    container: ServiceContainer = Depends(get_container),
) -> ConfigOptions:
    settings = container.settings
    return ConfigOptions(
        embedding_models=[settings.ollama_embedding_model, "mxbai-embed-large"],
        generation_models=[settings.ollama_chat_model, "qwen2.5", "mistral"],
        chunk_strategies=[ChunkStrategy.FIXED, ChunkStrategy.OVERLAP, ChunkStrategy.SEMANTIC],
    )


@router.post("/run", response_model=ExperimentResult, status_code=status.HTTP_201_CREATED)
async def run_experiment(
    request: ExperimentRunRequest,
    container: ServiceContainer = Depends(get_container),
) -> ExperimentResult:
    try:
        return await container.pipeline_service.run(request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/compare", response_model=ComparisonResult, status_code=status.HTTP_201_CREATED)
async def compare_experiments(
    request: ComparisonRunRequest,
    container: ServiceContainer = Depends(get_container),
) -> ComparisonResult:
    try:
        return await container.pipeline_service.compare(
            label=request.label,
            question=request.question,
            document_ids=request.document_ids,
            left=request.left,
            right=request.right,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{experiment_id}", response_model=ExperimentResult)
async def get_experiment(
    experiment_id: str,
    container: ServiceContainer = Depends(get_container),
) -> ExperimentResult:
    experiment = container.experiment_repository.get_experiment(experiment_id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found.")
    return experiment
