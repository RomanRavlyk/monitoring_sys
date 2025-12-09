from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from uuid import UUID
from .alert import AlertSchema


class StatusEnum(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"

class ServerCreate(BaseModel):
    name: str = Field(..., max_length=256)
    host: str = Field(..., max_length=256)
    port: int = Field(...)
    desc: str | None = Field(None, max_length=512)
    status: str | None = Field(StatusEnum | None , max_length=20)

class ServerRegister(BaseModel):
    name: str = Field(..., max_length=256)
    host: str = Field(..., max_length=256)
    port: int = Field(...)
    desc: str | None = Field(None, max_length=512)

class ServerResult(BaseModel):
    id: int
    name: str
    host: str
    port: int
    desc: str | None
    # alerts: list[AlertSchema]
    status: str
    added_at: datetime
    client_id: UUID

    model_config = ConfigDict(from_attributes=True)

class ServerUpdate(BaseModel):
    name: str | None = Field(None, max_length=256)
    host: str | None = Field(None, max_length=256)
    port: int | None = Field(None)
    desc: str | None = Field(None, max_length=512)
    status: str | None = Field(None, max_length=20)
