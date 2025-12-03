from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from .models import FailureLog, SeverityLevel
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

class FailureLogService:

    def __init__(self, db):
        self._db = db

    @property
    def db(self):
        return self._db

    async def get_failure_logs(self):
        result = await self.db.execute(select(FailureLog))
        return result.scalars().all()

    async def create_failure_log(self, data: dict) -> FailureLog:
        try:
            new_log = FailureLog(**data)
            new_log.severity = SeverityLevel(data['severity']).value

            self.db.add(new_log)
            await self.db.commit()
            await self.db.refresh(new_log)
            return new_log
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error creating failure log: {str(e)}")
            raise HTTPException(status_code=500, detail="Error creating failure log")

    async def get_failure_log_by_id(self, log_id: int) -> FailureLog | None:
        try:
            result = await self.db.execute(select(FailureLog).where(FailureLog.id == log_id))
            log = result.scalars().first()

            if not log:
                logger.info(f"Failure log with id {log_id} not found")
                raise HTTPException(status_code=404, detail="Failure log not found")

            return log
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving failure log with id {log_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error retrieving failure log")

    async def update_failure_log(self, log_id: int, data: dict) -> FailureLog | None:
        try:
            log = await self.get_failure_log_by_id(log_id)
            for key, value in data.items():
                setattr(log, key, value)

            self.db.add(log)
            await self.db.commit()
            await self.db.refresh(log)
            return log
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error updating failure log with id {log_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error updating failure log")

    async def delete_failure_log(self, log_id: int) -> bool:
        # log = await self.get_failure_log_by_id(log_id)
        try:
            log = await self.db.execute(select(FailureLog).where(FailureLog.id == log_id))
            log = log.scalars().first()

            await self.db.delete(log)
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error deleting failure log with id {log_id}: {e}")
            raise HTTPException(status_code=500, detail="Error deleting failure log")