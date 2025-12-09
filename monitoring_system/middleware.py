from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from db.database import get_db
from deps import verify_jwt

class IsAuthenticatedMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public endpoints
        if request.url.path.startswith("/docs") or \
           request.url.path.startswith("/openapi.json") or \
           request.url.path.startswith("/users/login") or \
           request.url.path.startswith("/users/register") or \
           (request.url.path.startswith("/alerts") and request.method == "POST"):
            return await call_next(request)

        # Try to verify JWT token
        try:
            token = await verify_jwt(request)
            if not token:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Unauthorized"}
                )
        except HTTPException as e:
            # Properly handle HTTPException from verify_jwt
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            # Handle any other unexpected errors
            return JSONResponse(
                status_code=500,
                content={"detail": f"Internal server error: {str(e)}"}
            )

        return await call_next(request)
