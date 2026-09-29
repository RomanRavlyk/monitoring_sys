from models.healthcheck import HealthCheck
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
from models.server import Server
import httpx
from datetime import datetime, timezone
from models.server import ServerStatus
from services.alert import AlertService
from schemas.healthcheck import HealthCheckCreate
from sqlalchemy import select
from core.settings import settings

logger = logging.getLogger(__name__)

class HealthCheckService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_health_check(self, data: dict) -> HealthCheck:
        try:
            new_check = HealthCheck(**data)

            self.db.add(new_check)
            await self.db.commit()
            await self.db.refresh(new_check)
            return new_check

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error creating health check: {str(e)}")
            raise

    async def perform_healthcheck(self, server: Server, alert_service: AlertService):
        async with httpx.AsyncClient() as client:
            headers = {'X-Api-Key': settings.api_key}
            try:
                response = await client.get(
                    f"http://{server.host}:{server.port}/health",
                    headers=headers,
                    timeout=5
                )
            except Exception as e:
                response = None
                logger.warning(f"Server {server.id} connection error: {str(e)}")

            health_check = HealthCheckCreate(
                server_id=server.id,
                success=False,
                checked_at=datetime.now(tz=timezone.utc)
            )

            if response and response.status_code == 200:
                server.status = ServerStatus.ONLINE.value
                logger.info(f"Server {server.id} healthy")

                health_check.success = True
                await self.create_health_check(health_check.model_dump())
            else:
                server.status = ServerStatus.OFFLINE.value
                logger.warning(f"Server {server.id} unhealthy")


                assigned_user = await alert_service.assign_healthcheck_user()

                await alert_service.send_healthcheck_alert(
                    user=assigned_user,
                    server_name=server.name,
                    status=server.status,
                    message=response.text if response else "No response",
                    timestamp=datetime.now(tz=timezone.utc)
                )

                await self.create_health_check(health_check.model_dump())

            await self.db.commit()

    async def get_health_checks(self, server_id: int):
        try:
            result = await self.db.execute(
                select(HealthCheck).where(HealthCheck.server_id == server_id)
            )
            checks = result.scalars().all()
            return checks

        except SQLAlchemyError as e:
            logger.error(f"Error retrieving health checks for server {server_id}: {str(e)}")
            raise
