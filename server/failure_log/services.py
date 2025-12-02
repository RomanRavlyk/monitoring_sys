from .models import FailureLog, SeverityLevel
from sqlalchemy import select

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
        new_log = FailureLog(**data)
        new_log.severity = SeverityLevel(data['severity']).value

        self.db.add(new_log)
        await self.db.commit()
        await self.db.refresh(new_log)
        return new_log

    async def get_failure_log_by_id(self, log_id: int) -> FailureLog | None:
        result = await self.db.execute(select(FailureLog).where(FailureLog.id == log_id))
        return result.scalars().first()

    async def update_failure_log(self, log_id: int, data: dict) -> FailureLog | None:
        log = await self.get_failure_log_by_id(log_id)
        if not log:
            return None
        for key, value in data.items():
            setattr(log, key, value)
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def delete_failure_log(self, log_id: int) -> FailureLog | None:
        log = await self.get_failure_log_by_id(log_id)
        if not log:
            return None
        await self.db.delete(log)
        await self.db.commit()
        return log