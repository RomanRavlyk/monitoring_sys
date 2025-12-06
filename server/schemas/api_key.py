from pydantic import BaseModel, ConfigDict
from datetime import datetime

class APIKeySchema(BaseModel):
    id: int
    key: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)