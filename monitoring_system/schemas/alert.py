from typing import Optional

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AlertSchema(BaseModel):
    id_on_server: Optional[int] = None
    server_id: Optional[int] = None
    assigned_group: Optional[str] = None
    severity: Optional[str] = None
    error_status_code: Optional[int] = None
    error_type: Optional[str] = None
    error_traceback: Optional[str] = None
    error_message: Optional[str] = None
    error_timestamp: Optional[datetime] = None
    solved: Optional[bool] = None
    assigned_to: Optional[int] = None
    solved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AlertSchemaResponse(BaseModel):
    id: int
    id_on_server: Optional[int] = None
    server_id: Optional[int] = None
    assigned_group: Optional[str] = None
    severity: Optional[str] = None
    error_status_code: Optional[int] = None
    error_type: Optional[str] = None
    error_traceback: Optional[str] = None
    error_message: Optional[str] = None
    error_timestamp: Optional[datetime] = None
    solved: Optional[bool] = None
    assigned_to: Optional[int] = None
    solved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
