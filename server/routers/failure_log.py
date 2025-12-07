from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_failure_log_service
from exceptions.failure_log import FailureLogNotFound
from schemas.failure_log import FailureLogCreate, FailureLogResult
from services.failure_log import FailureLogService
from fastapi.responses import Response
router = APIRouter()

@router.get("/failure-logs")
async def get_failure_logs(service: FailureLogService = Depends(get_failure_log_service)) -> list[FailureLogResult]:
    result = await service.get_failure_logs()
    data = [FailureLogResult.model_validate(data) for data in result]
    return data

@router.post("/failure-logs")
async def create_failure_log(data: FailureLogCreate, service: FailureLogService = Depends(get_failure_log_service)):
    res = await service.create_failure_log(data.model_dump())
    return FailureLogResult.model_validate(res).model_dump()

@router.get("/failure-logs/{log_id}")
async def get_failure_log(log_id: int, service: FailureLogService = Depends(get_failure_log_service)):
    return await service.get_failure_log_by_id(log_id)

@router.put("/failure-logs/{log_id}")
async def update_failure_log(log_id: int, data: dict, service: FailureLogService = Depends(get_failure_log_service)):
    return await service.update_failure_log(log_id, data)

@router.delete("/failure-logs/{log_id}")
async def delete_failure_log(log_id: int, service: FailureLogService = Depends(get_failure_log_service)):
    await service.delete_failure_log(log_id)
    return Response(status_code=204)
