from typing import List
from deps import get_server_service
from fastapi import APIRouter, Depends
from db.database import get_db
from services.server import ServerService
from fastapi.responses import JSONResponse
from schemas.server import ServerResult, ServerUpdate, ServerCreate, ServerRegister

from deps import has_admin_permission

router = APIRouter(tags=["Server"])

@router.post("/register/server", response_model=ServerResult)
async def register_server(data: ServerRegister,
                          service: ServerService = Depends(get_server_service),
                          is_admin: bool = Depends(has_admin_permission)
                          ):
    server = await service.create_server(data.model_dump(exclude_unset=True))
    return JSONResponse(status_code=204, content={"Server was successfully registered!"
                                                  "Your client_id:": str(server.client_id)} )

@router.get("/servers", response_model=List[ServerResult])
async def get_servers(service: ServerService = Depends(get_server_service)):
    return await service.get_servers()


@router.post("/servers", response_model=ServerResult)
async def create_server(data: ServerCreate,
                        service: ServerService = Depends(get_server_service),
                        is_admin: bool = Depends(has_admin_permission)
                        ):
    return await service.create_server(data.model_dump(exclude_unset=True))


@router.get("/servers/{server_id}", response_model=ServerResult)
async def get_server(server_id: int,
                     service: ServerService = Depends(get_server_service),
                     ):
    return await service.get_server_by_id(server_id)


@router.put("/servers/{server_id}", response_model=ServerResult)
async def update_server(server_id: int,
                        data: ServerUpdate,
                        service: ServerService = Depends(get_server_service),
                        is_admin: bool = Depends(has_admin_permission)
                        ):
    return await service.update_server(server_id, data.model_dump(exclude_unset=True))


@router.delete("/servers/{server_id}")
async def delete_server(server_id: int,
                        service: ServerService = Depends(get_server_service),
                        is_admin: bool = Depends(has_admin_permission)
                        ):
    return await service.delete_server(server_id)
