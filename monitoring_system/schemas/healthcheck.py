from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class HealthCheckCreate(BaseModel):
    server_id: int = Field(...)
    success: bool = Field(...)
    checked_at: datetime = Field(...)

class HealthCheckResult(BaseModel):
    id: int
    server_id: int
    success: bool
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)