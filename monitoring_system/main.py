import asyncio
from deps import get_server_service, get_alert_service
from schemas.alert import AlertSchema
from services.server import ServerService
from services.alert import AlertService
from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.responses import Response
from contextlib import asynccontextmanager
import logging
from schemas.failure_log import FailureLog
from routers.server import router as server_router
from routers.alert import router as alert_router
from routers.user import user_router, admin_router, authentication_router
from fastapi import Request


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
    while True:
        logger.info("Performing periodic health check...")
        # Here you would add the actual health check logic
        await asyncio.sleep(300)  # Sleep for 5 minutes


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server up...")
    yield
    logger.info("Shutting server down...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/alerts", tags=["Alert"] )
async def create_alert_service(request: Request, failure_log: FailureLog,
                               alert_service: AlertService = Depends(get_alert_service),
                               server_service: ServerService = Depends(get_server_service)
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

    await alert_service.create_alert(alert.model_dump())

    return Response(status_code=200, content="Alert created successfully")
app.include_router(server_router)
app.include_router(alert_router)
app.include_router(authentication_router)
app.include_router(user_router)
app.include_router(admin_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
