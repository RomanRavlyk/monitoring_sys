from db.base import Base
from sqlalchemy import Integer, String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum

class UserRoles(str, enum.Enum):
    ADMIN = "ADMIN"
    DEVOPS = "DEVOPS"
    DEVELOPER = "DEVELOPER"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slack_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    assigned_tasks_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_man: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    role: Mapped[UserRoles] = mapped_column(
        Enum(UserRoles),
        default=UserRoles.DEVELOPER,
        server_default="DEVELOPER",
        nullable=False
    )