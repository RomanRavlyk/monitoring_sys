import json

from core.settings import settings
from sqlalchemy.exc import SQLAlchemyError
import exceptions.failure_log as failure_log_exceptions
from models.failure_log import FailureLog, SeverityLevel, Groups
from sqlalchemy import select
import logging
from exceptions.devops import DEVOPS_EXCEPTIONS
from exceptions.developer import DEVELOPER_EXCEPTIONS
import httpx
from schemas.failure_log import FailureLogResult

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
            raise failure_log_exceptions.FailureLogDatabaseError() from e

    async def get_failure_log_by_id(self, log_id: int) -> FailureLog | None:
        try:
            result = await self.db.execute(select(FailureLog).where(FailureLog.id == log_id))
            log = result.scalars().first()

            if not log:
                logger.info(f"Failure log with id {log_id} not found")
                raise failure_log_exceptions.FailureLogNotFound()

            return log

        except SQLAlchemyError as e:
            logger.error(f"Error retrieving failure log with id {log_id}: {str(e)}")
            raise failure_log_exceptions.FailureLogDatabaseError() from e

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
            raise failure_log_exceptions.FailureLogDatabaseError() from e

    async def delete_failure_log(self, log_id: int) -> bool:
        # log = await self.get_failure_log_by_id(log_id)
        try:
            log = await self.db.execute(select(FailureLog).where(FailureLog.id == log_id))
            log = log.scalars().first()

            if log is None:
                logger.info(f"Failure log with id {log_id} not found for deletion")
                raise failure_log_exceptions.FailureLogNotFound()

            await self.db.delete(log)
            await self.db.commit()
            return True

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error deleting failure log with id {log_id}: {e}")
            raise failure_log_exceptions.FailureLogDatabaseError() from e


    @staticmethod
    async def analise_exception(exc: Exception, failure_log: FailureLog):
        if isinstance(exc, DEVELOPER_EXCEPTIONS):
            failure_log.severity = SeverityLevel.CRITICAL.value
            failure_log.assigned_group = Groups.DEVELOPER.value
        elif isinstance(exc, DEVOPS_EXCEPTIONS):
            failure_log.severity = SeverityLevel.CRITICAL.value
            failure_log.assigned_group = Groups.DEVOPS.value
        else:
            failure_log.severity = SeverityLevel.MINOR.value
            failure_log.assigned_group = Groups.ADMIN.value

        return failure_log

    @staticmethod
    async def send_failure_log_alert(failure_log: FailureLog):
        # Placeholder for notification logic (e.g., email, Slack)
        logger.info(f"Notification sent for failure log ID {failure_log.id}")

        payload = FailureLogResult.model_validate(failure_log)
        async with httpx.AsyncClient() as client:
            try:
                obj = payload.model_dump(mode="json")
                print("SERIALISED ERROR TRACEBACK: ", obj['error_traceback'])
                response = await client.post(f"{settings.monitoring_system_url}/failure_log", json=payload.model_dump(mode="json"), timeout=10)
                response.raise_for_status()
                logger.info(f"Successfully sent failure log ID {failure_log.id} to monitoring system.")
            except httpx.HTTPError as e:
                logger.error(f"Failed to send failure log ID {failure_log.id} to monitoring system: {str(e)}")
                raise failure_log_exceptions.FailureLogRequestSendingError() from e