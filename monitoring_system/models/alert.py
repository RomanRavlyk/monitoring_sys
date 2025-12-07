from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, String, Integer, DateTime, func
from datetime import datetime

class Alert(Base):
    __tablename__ = 'alerts'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_on_server: Mapped[int] = mapped_column(Integer, nullable=False)

    server_id: Mapped[int] = mapped_column(
        ForeignKey('servers.id', ondelete="CASCADE"),
        nullable=False
    )
    server: Mapped["Server"] = relationship('Server', back_populates='alerts')

    assigned_group: Mapped[str] = mapped_column(String(20), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    error_status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    error_type: Mapped[str] = mapped_column(String(256), nullable=False)
    error_traceback: Mapped[str] = mapped_column(Text, nullable=False)
    error_message: Mapped[str] = mapped_column(String(1024), nullable=False)
    error_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    alert_created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)



