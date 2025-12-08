from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AlertSchema(BaseModel):
    id_on_server: int
    server_id: int
    assigned_group: str
    severity: str
    error_status_code: int
    error_type: str
    error_traceback: str
    error_message: str
    error_timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
