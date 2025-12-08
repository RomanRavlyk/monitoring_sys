from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from schemas.user import UserResult, Token, UserCreate, UserLogin, UserUpdate, UserCreateAdmin, UserUpdateAdmin
from deps import verify_jwt, get_user_service, has_admin_permission
from services.user import UserService
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

user_router = APIRouter(tags=["Users"])
admin_router = APIRouter(prefix="/admin", tags=["Users-Admin"])
authentication_router = APIRouter(tags=["Authentication"])


@authentication_router.post("/users/register", status_code=status.HTTP_201_CREATED)
async def register_user(data: UserCreate, service: UserService = Depends(get_user_service)):
    await service.register_user(data.model_dump())
    return {"message": "User registered"}


@authentication_router.post("/users/login", response_model=Token)
async def user_login(data: UserLogin, service: UserService = Depends(get_user_service)):
    return await service.login_user(data.model_dump())


@user_router.get("/users/me", response_model=UserResult)
async def read_current_user(payload: str = Depends(verify_jwt), service: UserService = Depends(get_user_service)):
    return await service.get_current_user(payload)


@user_router.put("/users/me", response_model=UserResult)
async def update_current_user(data: UserUpdate, payload: dict = Depends(verify_jwt),
                              service: UserService = Depends(get_user_service)
                              ):
    user_id = int(payload["sub"])
    return await service.change_current_user(data.model_dump(exclude_unset=True), user_id)


@user_router.delete("/users/me")
async def delete_current_user(payload: dict = Depends(verify_jwt),
                              service: UserService = Depends(get_user_service)
                              ):
    return await service.delete_current_user(payload)


@admin_router.post("/users", response_model=UserResult)
async def create_user(data: UserCreateAdmin,
                      service: UserService = Depends(get_user_service),
                      is_admin: bool = Depends(has_admin_permission)
                      ):
    return await service.register_user(data.model_dump())


@admin_router.get("/users/{user_id}", response_model=UserResult)
async def read_user(user_id: int,
                    is_admin: bool = Depends(has_admin_permission),
                    service: UserService = Depends(get_user_service)
                    ):
    return await service.get_user_by_id(user_id)


@admin_router.get("/users")  # , response_model=List[UserResult]
async def read_all_users(is_admin: bool = Depends(has_admin_permission),
                         service: UserService = Depends(get_user_service)
                         ):
    return await service.get_users()


@admin_router.put("/users/{user_id}", response_model=UserResult)
async def update_user(user_id: int, data: UserUpdateAdmin, service: UserService = Depends(get_user_service), is_admin: bool = Depends(has_admin_permission)):
    return await service.update_user(user_id, data.model_dump(exclude_unset=True))


@admin_router.delete("/users/{user_id}")
async def delete_user(user_id: int,
                      service: UserService = Depends(get_user_service),
                      is_admin: bool = Depends(has_admin_permission)
                      ):
    return await service.delete_user(user_id)
