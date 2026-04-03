from fastapi import APIRouter, Depends

from app.dependencies import ServiceContainer, get_container
from app.schemas import DriftMonitorResponse

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/drift", response_model=DriftMonitorResponse)
async def get_drift_report(
    container: ServiceContainer = Depends(get_container),
) -> DriftMonitorResponse:
    experiments = container.experiment_repository.list_experiments()
    return await container.monitoring_service.analyze(experiments)
