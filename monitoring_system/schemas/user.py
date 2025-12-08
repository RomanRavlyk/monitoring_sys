from pydantic import BaseModel
from pydantic import Field, ConfigDict
import enum

class UserRoles(str, enum.Enum):
    ADMIN = "ADMIN"
    DEVOPS = "DEVOPS"
    DEVELOPER = "DEVELOPER"

class UserCreate(BaseModel):
    username: str = Field(..., max_length=150)
    email: str = Field(..., max_length=254)
    slack_id: str = Field(..., max_length=50)
    password: str = Field(..., min_length=8)

class UserCreateAdmin(BaseModel):
    username: str| None = Field(None, max_length=150)
    email: str| None = Field(None, max_length=254)
    slack_id: str | None = Field(None, max_length=50)
    password: str| None = Field(None, min_length=8)
    is_active: bool = Field(default=True)
    role: str| None = Field(None)

class UserLogin(BaseModel):
    username: str = Field(..., max_length=150)
    password: str = Field(..., min_length=8)

class UserResult(BaseModel):
    id: int
    username: str
    email: str
    slack_id: str
    is_active: bool
    role: UserRoles

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: str | None = Field(None, max_length=150)
    email: str | None = Field(None, max_length=254)
    slack_id: str | None = Field(None, max_length=50)
    password: str | None = Field(None, min_length=8)

class UserUpdateAdmin(BaseModel):
    username: str | None = Field(None, max_length=150)
    email: str | None = Field(None, max_length=254)
    slack_id: str | None = Field(None, max_length=50)
    password: str | None = Field(None, min_length=8)
    is_active: bool | None = Field(None)
    role: UserRoles | None = Field(None)

class Token(BaseModel):
    access_token: str