from datetime import datetime
from core.settings import settings
import httpx
from fastapi import HTTPException
from models.user import User, UserRoles
from sqlalchemy.ext.asyncio import AsyncSession
from models.alert import Alert
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy import select
from utils import send_email


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

    async def get_assigned_alerts(self, user_id: int):
        try:
            result = await self.db.execute(
                select(Alert).where(Alert.assigned_to == user_id, Alert.solved == False)
            )
            alerts = result.scalars().all()
            return alerts
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving assigned alerts for user {user_id}: {str(e)}")
            raise

    async def complete_alert(self, alert_id: int, user_id: int):
        try:
            alert = await self.get_alert_by_id(alert_id)
            if not alert:
                logger.info(f"Alert with id {alert_id} not found for completion")
                raise

            stmt = select(User).where(User.id == user_id).with_for_update()
            user = (await self.db.execute(stmt)).scalars().first()

            if not user:
                logger.info(f"User with id {user_id} not found for completing alert")
                raise HTTPException(status_code=404, detail="User not found")

            user.assigned_tasks_number = max(0, user.assigned_tasks_number - 1)

            alert.solved = True
            alert.solved_at = datetime.now()

            await self.db.commit()
            await self.db.refresh(alert)
            return alert
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error completing alert with id {alert_id}: {str(e)}")
            raise

    async def assign_healthcheck_user(self) -> User:
        stmt = (
            select(User)
            .where(User.role == UserRoles.DEVOPS)
            .order_by(User.assigned_tasks_number.asc())
            .with_for_update()
            .limit(1)
        )

        result = await self.db.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="No DevOps user available")

        user.assigned_tasks_number += 1
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def assign_alert(self, alert_id: int, role: str):
        try:
            alert = await self.get_alert_by_id(alert_id)
            if not alert:
                logger.info(f"Alert with id {alert_id} not found for assignment")
                raise HTTPException(status_code=404, detail="Alert {alert_id} not found")

            stmt = (
                select(User)
                .where(User.role == role)
                .order_by(User.assigned_tasks_number.asc())
                .with_for_update()
                .limit(1)
            )
            result = await self.db.execute(stmt)
            user = result.scalars().first()

            if not user:
                logger.info(f"No user found with role {role} for assignment")
                raise HTTPException(status_code=404, detail=f"No user with role {role} available")

            alert.assigned_to = user.id
            user.assigned_tasks_number += 1

            self.db.add(alert)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(alert)
            return alert

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error assigning alert {alert_id}: {str(e)}")
            raise

    @staticmethod
    async def send_healthcheck_alert(user: User, server_name: str, status: str, message: str,
                                     timestamp: datetime):
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        body = (
            f"🚨 *Healthcheck Alert*\n"
            f"Hello, <@{user.slack_id}>!\n\n"
            f"*Server:* `{server_name}`\n"
            f"*Status:* `{status}`\n"
            f"*Timestamp:* `{timestamp}`\n\n"
            f"*Details:*\n```{message}```"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(settings.slack_webhook_url, json={"text": body})
            response.raise_for_status()
            return response.text

    @staticmethod
    async def send_user_alert(alert: Alert, user: User):
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found")

        body = (
            f"Hello, {user.email}!\nYou have been assigned a new alert.\n\n"
            f"Alert ID: {alert.id}\n"
            f"Error Type: {alert.error_type}\n"
            f"Error Message: {alert.error_message}\n"
            f"Severity: {alert.severity}\n"
            f"Timestamp: {alert.error_timestamp}\n\n"
            f"Please check the monitoring system for more details."
        )

        payload = {"text": body}

        async with httpx.AsyncClient() as client:
            response = await client.post(settings.slack_webhook_url, json=payload)
            response.raise_for_status()
            logger.info(f"Message sent to user {user.username} (ID: {user.id}) for alert {alert.id}")
            return response.text

    # @staticmethod
    # async def send_healthcheck_alert(message: str, user: User):
    #     if not user:
    #         raise HTTPException(status_code=404, detail="User not found")
    #
    #     body = (
    #         f"🚨 *Healthcheck Alert*\n"
    #         f"Hello, {user.username}!\n\n"
    #         f"There was an issue during the server healthcheck.\n\n"
    #         f"*Details:*\n{message}\n\n"
    #         f"Please check the monitoring system for more information."
    #     )
    #
    #     payload = {"text": body}
    #
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(settings.slack_webhook_url, json=payload)
    #         response.raise_for_status()
    #         logger.info(f"Healthcheck alert sent to user {user.username} (ID: {user.id})")
    #         return response.text