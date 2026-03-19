from datetime import datetime

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SettingHistory(Base):
    __tablename__ = "setting_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    setting_type: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    changed_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
