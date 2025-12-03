from fastapi import APIRouter, Depends, Body
from db.db import get_db
from dependencies import get_failure_log_service
from .schemas import FailureLogCreate, FailureLogUpdate, FailureLogRead
from sqlalchemy.ext.asyncio import AsyncSession
from .services import FailureLogService
from fastapi.responses import Response
router = APIRouter()

@router.get("/failure-log")
async def get_failure_logs(service: FailureLogService = Depends(get_failure_log_service)) -> list[FailureLogRead]:
    result = await service.get_failure_logs()
    data = [FailureLogRead.model_validate(data) for data in result]
    return data

@router.post("/failure-log")
async def create_failure_log(data: FailureLogCreate, service: FailureLogService = Depends(get_failure_log_service)):
    res = await service.create_failure_log(data.model_dump())
    return FailureLogRead.model_validate(res).model_dump()

@router.get("/failure-log/{log_id}")
async def get_failure_log(log_id: int, service: FailureLogService = Depends(get_failure_log_service)):
    return await service.get_failure_log_by_id(log_id)

@router.put("/failure-log/{log_id}")
async def update_failure_log(log_id: int, data: dict, service: FailureLogService = Depends(get_failure_log_service)):
    return await service.update_failure_log(log_id, data)

@router.delete("/failure-log/{log_id}")
async def delete_failure_log(log_id: int, service: FailureLogService = Depends(get_failure_log_service)):
    await service.delete_failure_log(log_id)
    return Response(status_code=204)
