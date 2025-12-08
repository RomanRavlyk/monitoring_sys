from sqlalchemy.ext.asyncio import AsyncSession
from models.alert import Alert
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy import select


logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    @property
    def db(self):
        return self._db

    async def create_alert(self, data: dict) -> Alert:
        try:
            new_alert = Alert(**data)
            self.db.add(new_alert)
            await self.db.commit()
            await self.db.refresh(new_alert)
            return new_alert
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error creating alert: {str(e)}")
            raise

    async def get_alerts_by_server(self, server_id) -> list[Alert]:
        try:
            result = await self.db.execute(select(Alert).where(Alert.server_id == server_id))
            alerts = result.scalars().all()
            return alerts
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving alerts for server {server_id}: {str(e)}")
            raise

    async def get_alert_by_id(self, alert_id: int) -> Alert | None:
        try:
            result = await self.db.execute(select(Alert).where(Alert.id == alert_id))
            alert = result.scalars().first()
            if not alert:
                logger.info(f"Alert with id {alert_id} not found")
                raise
            return alert
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving alert with id {alert_id}: {str(e)}")
            raise

    async def get_alerts(self):
        try:
            result = await self.db.execute(select(Alert))
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving alerts: {str(e)}")
            raise

    async def delete_alert(self, alert_id: int):
        try:
            alert = await self.get_alert_by_id(alert_id)
            if not alert:
                logger.info(f"Alert with id {alert_id} not found for deletion")
                raise

            await self.db.delete(alert)
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error deleting alert with id {alert_id}: {str(e)}")
            raise
