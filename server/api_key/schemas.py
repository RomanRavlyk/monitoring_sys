from pydantic import BaseModel
from datetime import datetime

class APIKeySchema(BaseModel):
    id: int
    key: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True