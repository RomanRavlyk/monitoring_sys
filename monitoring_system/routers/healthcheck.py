from typing import List
from fastapi import APIRouter, Depends
from services.healthcheck import HealthCheckService
from schemas.healthcheck import HealthCheckResult
from deps import get_healthcheck_service

router = APIRouter(tags=["Healthcheck"])

@router.get("/health_checks/{server_id}", response_model=List[HealthCheckResult])
async def get_healthcheck_status(server_id: int,
                                 service: HealthCheckService = Depends(get_healthcheck_service)):
    return await service.get_health_checks(server_id)