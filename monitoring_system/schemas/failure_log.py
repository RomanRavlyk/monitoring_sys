from pydantic import BaseModel
from datetime import datetime

class FailureLog(BaseModel):
    id: int
    assigned_group: str
    severity: str
    error_status_code: int
    error_type: str
    error_traceback: str
    error_message: str
    timestamp: datetime