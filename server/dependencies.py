from sqlalchemy.ext.asyncio import AsyncSession

from services.failure_log import FailureLogService
from db.database import get_db
from fastapi import Depends

def get_failure_log_service(db: AsyncSession = Depends(get_db)) -> FailureLogService:
    return FailureLogService(db)