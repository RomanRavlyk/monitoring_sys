from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base
from sqlalchemy import String, DateTime, Text, Enum, Integer
from sqlalchemy.sql import func
from datetime import datetime
import enum

class SeverityLevel(str, enum.Enum):
    CRITICAL = "Critical"
    WARNING = "Warning"
    MINOR = "Minor"

class Groups(str, enum.Enum):
    DEVOPS = "DEVOPS"
    ADMIN = "ADMIN"
    DEVELOPER = "DEVELOPER"

class FailureLog(Base):
    __tablename__ = "failure_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    assigned_group: Mapped[Groups] = mapped_column(Enum(Groups), nullable=True)
    severity: Mapped[SeverityLevel] = mapped_column(Enum(SeverityLevel), nullable=True)
    error_status_code: Mapped[int] = mapped_column(Integer, nullable=False, server_default="500")
    error_type: Mapped[str] = mapped_column(String(256), nullable=False)
    error_traceback: Mapped[str] = mapped_column(Text, nullable=False)
    error_message: Mapped[str] = mapped_column(String(1024), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
