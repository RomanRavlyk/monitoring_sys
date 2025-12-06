from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from db.database import get_db
from exceptions.api_key import ApiKeyNotFound
from services.api_key import APIKeyService


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
            return await call_next(request)

        request_api_key = request.headers.get("X-Api-Key")

        if not request_api_key:
            raise HTTPException(status_code=401, detail="API key header missing")

        async for db in get_db():
            api_key_service = APIKeyService(db)
            try:
                await api_key_service.get_api_key_by_key(request_api_key)
            except ApiKeyNotFound:
                raise HTTPException(status_code=401, detail="Invalid credentials")

        return await call_next(request)
