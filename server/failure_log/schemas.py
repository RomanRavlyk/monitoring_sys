from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class SeverityLevel(str, Enum):
    CRITICAL = "Critical"
    WARNING = "Warning"
    INFO = "Info"

class FailureLogCreate(BaseModel):
    assigned_group: str = Field(..., max_length=128)
    severity: SeverityLevel
    error_type: str = Field(..., max_length=256)
    error_traceback: str = Field(..., max_length=2048)
    error_message: str = Field(..., max_length=1024)

class FailureLogRead(BaseModel):
    id: int
    assigned_group: str
    severity: str
    error_type: str
    error_traceback: str
    error_message: str
    timestamp: datetime

    class Config:
        from_attributes = True

class FailureLogUpdate(BaseModel):
    assigned_group: str | None = Field(None, max_length=128)
    severity: str | None = Field(None, max_length=16)
    error_type: str | None = Field(None, max_length=256)
    error_traceback: str | None = Field(None, max_length=2048)
    error_message: str | None = Field(None, max_length=1024)