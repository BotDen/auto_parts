from datetime import datetime
from typing import List

from sqlalchemy import ARRAY, DateTime, ForeignKey, String, text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from utility.sql_enum import StatusEnum


class AdvertisementBase(Base):
    """Базовая модель объекта объявления для базы данных"""
    __tablename__ = "advertisements"

    title: Mapped[str]
    price: Mapped[float]
    description: Mapped[str]
    status: Mapped[StatusEnum] = mapped_column(server_default=text("'DRAFT'"), init=False, create_type=False)
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    author: Mapped["UserBase"] = relationship("UserBase", back_populates="advertisements", init=False)
    photos_url: Mapped[List[str] | None] = mapped_column(ARRAY(String), default_factory=list, server_default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, nullable=True)
