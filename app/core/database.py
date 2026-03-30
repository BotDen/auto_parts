import uuid
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import DateTime, func, text, UUID
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncAttrs, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from config import settings


# Получаем URL адрес базы данных
DATABASE_URL = settings.get_db_url()

# Создаем асинхронный движок для БД
engine = create_async_engine(url=DATABASE_URL)

# Фабрика асинхронных сессий
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    """Базовый класс для моделей базы данных"""
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


async def get_db():
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]
