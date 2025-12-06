from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, HTTPException
from services.failure_log import FailureLogService
from db.database import get_db
from fastapi import Depends
from services.api_key import APIKeyService
from exceptions.api_key import ApiKeyNotFound

def get_failure_log_service(db: AsyncSession = Depends(get_db)) -> FailureLogService:
    return FailureLogService(db)

async def get_api_key_service(db: AsyncSession = Depends(get_db)) -> APIKeyService:
    return APIKeyService(db)

async def check_api_key(request: Request, api_key_service: APIKeyService = Depends(get_api_key_service)):

    api_key = request.headers.get("X-API-KEY")

    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    try:
        await api_key_service.get_api_key_by_key(api_key)
    except ApiKeyNotFound:
        raise HTTPException(status_code=401, detail="Invalid credentials")
