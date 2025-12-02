from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base
from sqlalchemy import String, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy import Enum
import enum

class SeverityLevel(str, enum.Enum):
    CRITICAL = "Critical"
    WARNING = "Warning"
    INFO = "Info"

class FailureLog(Base):
    __tablename__ = "failure_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    assigned_group: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[SeverityLevel] = mapped_column(Enum(SeverityLevel), nullable=False)
    error_type: Mapped[str] = mapped_column(String(256), nullable=False)
    error_traceback: Mapped[str] = mapped_column(String(2048), nullable=False)
    error_message: Mapped[str] = mapped_column(String(1024), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
