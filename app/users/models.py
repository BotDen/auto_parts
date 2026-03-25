import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Model


class UserModel(Model):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(min_length=1, max_length=128)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False, min_length=8, max_length=128)
    avatar_url: Mapped[str | None] = mapped_column(nullable=True)
    is_blocked: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc))
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc))
