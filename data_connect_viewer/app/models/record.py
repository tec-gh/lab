from datetime import datetime

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hostname: Mapped[str | None] = mapped_column(Text, nullable=True)
    ipaddress: Mapped[str | None] = mapped_column(Text, nullable=True)
    area: Mapped[str | None] = mapped_column(Text, nullable=True)
    building: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(Text, nullable=True)
    model: Mapped[str | None] = mapped_column(Text, nullable=True)
    ping_test_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    exec_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    mapping_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    received_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
