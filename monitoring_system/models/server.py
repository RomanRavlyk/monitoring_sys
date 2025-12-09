from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Enum, DateTime, func, UniqueConstraint
import enum
from datetime import datetime

from models.healthcheck import HealthCheck
from .alert import Alert
from sqlalchemy.dialects.postgresql import UUID

class ServerStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"

class Server(Base):
    __tablename__ = "servers"
    __table_args__ = (UniqueConstraint('host', 'port', name='uix_host_port'),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256))
    host: Mapped[str] = mapped_column(String(256))
    port: Mapped[int] = mapped_column(Integer)

    health_checks: Mapped[list["HealthCheck"]] = relationship(HealthCheck,
                                                        back_populates="server",
                                                        lazy="selectin"
                                                        )

    client_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=True
    )

    desc: Mapped[str | None] = mapped_column(String(512), nullable=True)
    alerts: Mapped[list[Alert]] = relationship("Alert", back_populates="server", uselist=True, lazy="selectin")
    status: Mapped[ServerStatus] = mapped_column(
        Enum(ServerStatus),
        nullable=False,
        default=ServerStatus.OFFLINE.value,
        server_default="OFFLINE"
    )

    added_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())