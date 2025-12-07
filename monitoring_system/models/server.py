from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Enum, DateTime, func
import enum
from datetime import datetime
from .alert import Alert

class ServerStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"

class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256))
    ip_address: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    desc: Mapped[str | None] = mapped_column(String(512), nullable=True)
    alerts: Mapped[list[Alert]] = relationship("Alert", back_populates="server", uselist=True, lazy="selectin")
    status: Mapped[ServerStatus] = mapped_column(
        Enum(ServerStatus),
        nullable=False,
        default=ServerStatus.OFFLINE.value,
        server_default="OFFLINE"
    )
    added_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())