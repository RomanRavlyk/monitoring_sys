from sqlalchemy.ext.asyncio import AsyncSession

from failure_log.services import FailureLogService
from db.db import get_db
from fastapi import Depends

def get_failure_log_service(db: AsyncSession = Depends(get_db)) -> FailureLogService:
    return FailureLogService(db)