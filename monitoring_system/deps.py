from fastapi import HTTPException
from jose.exceptions import JWTError
from models.user import UserRoles
from services.user import UserService
from services.alert import AlertService
from services.server import ServerService
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from fastapi import Depends
from starlette.requests import Request

async def get_server_service(db: AsyncSession = Depends(get_db)) -> ServerService:
    return ServerService(db)

async def get_alert_service(db: AsyncSession = Depends(get_db)) -> AlertService:
    return AlertService(db)

async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

async def verify_jwt(request: Request, user_service: UserService = Depends(get_user_service)):
    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    token = auth.split("Bearer ", 1)[1]

    try:
        return user_service.verify_jwt_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def has_admin_permission(token = Depends(verify_jwt)):
    if token["role"] == UserRoles.ADMIN.value:
        return True
    raise HTTPException(status_code=403, detail="Forbidden")

async def is_authenticated(token = Depends(verify_jwt)):
    """Basic authentication check - just verify user is logged in"""
    return token

async def has_alert_object_permission(
    alert_id: int,
    token=Depends(verify_jwt),
    alert_service: AlertService = Depends(get_alert_service)
):
    alert = await alert_service.get_alert_by_id(alert_id)
    if token["role"] == UserRoles.ADMIN.value or alert.assigned_to == int(token["sub"]):
        return token
    raise HTTPException(status_code=403, detail="Forbidden")