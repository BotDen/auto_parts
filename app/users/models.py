from datetime import datetime

from sqlalchemy import DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserBase(Base):
    """Базовая модель User для Базы Данных"""

    __tablename__ = "users"

    username: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    avatar_url: Mapped[str | None] = mapped_column(default=None)
    advertisements: Mapped[list["AdvertisementBase"] | None] = relationship(
        "AdvertisementBase",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, nullable=True)
    is_blocked: Mapped[bool] = mapped_column(default=False, server_default=text("false"), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(default=False, server_default=text("false"), nullable=False)
