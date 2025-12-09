from fastapi import HTTPException
from jose.exceptions import JWTError
from models.user import UserRoles
from services.report import ReportService
from services.user import UserService
from services.alert import AlertService
from services.server import ServerService
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from fastapi import Depends
from starlette.requests import Request
from services.healthcheck import HealthCheckService


async def get_server_service(db: AsyncSession = Depends(get_db)) -> ServerService:
    return ServerService(db)

async def get_alert_service(db: AsyncSession = Depends(get_db)) -> AlertService:
    return AlertService(db)

async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

async def get_healthcheck_service(db: AsyncSession = Depends(get_db)) -> HealthCheckService:
    return HealthCheckService(db)

async def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    server_service = await get_server_service(db)
    healthcheck_service = await get_healthcheck_service(db)
    alert_service = await get_alert_service(db)

    return ReportService(
        db,
        server_service,
        healthcheck_service,
        alert_service
    )

async def verify_jwt(request: Request):
    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    token = auth.split("Bearer ", 1)[1]

    try:
        return UserService.verify_jwt_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def has_admin_permission(token = Depends(verify_jwt)):
    if token["role"] == UserRoles.ADMIN.value:
        return True
    raise HTTPException(status_code=403, detail="Forbidden")

async def has_alert_object_permission(
    alert_id: int,
    token=Depends(verify_jwt),
    alert_service: AlertService = Depends(get_alert_service)
):
    alert = await alert_service.get_alert_by_id(alert_id)
    if token["role"] == UserRoles.ADMIN.value or alert.assigned_to == int(token["sub"]):
        return token
    raise HTTPException(status_code=403, detail="Forbidden")