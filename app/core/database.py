from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from config import settings


engine = create_async_engine(settings.DATABASE_URL)


async_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(MappedAsDataclass, DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]
