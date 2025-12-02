from db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from sqlalchemy.sql import func
from datetime import datetime

class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)