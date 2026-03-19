from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FieldMapping(Base):
    __tablename__ = "field_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    field_key: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    json_path: Mapped[str] = mapped_column(String(255), nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_searchable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_exportable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
