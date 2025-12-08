import asyncio
from deps import get_server_service, get_alert_service, get_user_service
from schemas.alert import AlertSchema
from services.server import ServerService
from services.alert import AlertService
from fastapi import FastAPI, Depends, HTTPException, Body
from db.database import get_db
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import httpx
from models.server import  ServerStatus
import logging
from schemas.failure_log import FailureLog
from routers.server import router as server_router
from routers.alert import router as alert_router
from routers.user import user_router, admin_router, authentication_router
from fastapi import Request
from datetime import datetime, UTC


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)


async def periodic_healthcheck():
    from db.database import AsyncSessionLocal
    while True:
        try:
            async with AsyncSessionLocal() as db:

                server_service = ServerService(db)
                alert_service = AlertService(db)

                servers = await server_service.get_servers()
                logger.info("Performing periodic health check...")

                for server in servers:
                    logger.info(f"Health check for server {server.id} - {server.name}")

                    async with httpx.AsyncClient() as client:
                        try:
                            response = await client.get(
                                f"http://{server.host}:{server.port}/health",
                                timeout=5
                            )
                        except Exception as e:
                            response = None
                            logger.warning(f"Server {server.id} connection error: {str(e)}")

                        if response and response.status_code == 200:
                            server.status = ServerStatus.ONLINE.value
                            logger.info(f"Server {server.id} healthy")
                        else:
                            server.status = ServerStatus.OFFLINE.value
                            logger.warning(f"Server {server.id} unhealthy")

                            assigned_user = await alert_service.assign_healthcheck_user()

                            await alert_service.send_healthcheck_alert(
                                user=assigned_user,
                                server_name=server.name,
                                status=server.status,
                                message=response.text if response else "No response",
                                timestamp=datetime.now(UTC)
                            )

                await db.commit()

        except Exception as e:
            logger.error(f"Periodic healthcheck failed: {str(e)}")

        await asyncio.sleep(300)  # run again in 5 minutes

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(periodic_healthcheck())

    logger.info("Starting server up...")
    yield
    logger.info("Shutting server down...")

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/alerts", tags=["Alert"] )
async def create_alert(request: Request, failure_log: FailureLog,
                               alert_service: AlertService = Depends(get_alert_service),
                               server_service: ServerService = Depends(get_server_service),
                               user_service = Depends(get_user_service)
                               ):
    logger.info(f"Received failure log: {failure_log}")
    host, port = request.client.host, request.client.port
    print(f"Received host: {host}, port: {port}")
    cid = request.headers.get("X-CLIENT-ID")
    print(f"Received client ID: {cid}")
    if not cid:
        raise HTTPException(status_code=400, detail="X-CLIENT-ID header missing")

    server = await server_service.get_server_by_client_id(cid)

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    alert = AlertSchema(
        id_on_server=failure_log.id,
        server_id=server.id,
        assigned_group=failure_log.assigned_group,
        severity=failure_log.severity,
        error_status_code=failure_log.error_status_code,
        error_type=failure_log.error_type,
        error_traceback=failure_log.error_traceback,
        error_message=failure_log.error_message,
        error_timestamp=failure_log.timestamp
    )

    alert = await alert_service.create_alert(alert.model_dump())

    alert = await alert_service.assign_alert(alert.id, role=alert.assigned_group)

    assigned_user = await user_service.get_user_by_id(alert.assigned_to)
    if assigned_user:
        logger.info(f"Alert {alert.id} assigned to user {assigned_user.username} (ID: {assigned_user.id})")
        await AlertService.send_user_alert(alert, assigned_user)

    return JSONResponse(
        status_code=200,
        content={"message": "Alert created successfully", "alert_id": alert.id}
    )
app.include_router(server_router)
app.include_router(alert_router)
app.include_router(authentication_router)
app.include_router(user_router)
app.include_router(admin_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
