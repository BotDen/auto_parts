from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.users.user_routers.auth_routers import router as auth_router
from app.advertisements.ad_routers.ad_routers import router as ad_router
from app.users.user_routers.user_routers import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="AutoParts",
    description="Сервис по покупке и продаже автозапчастей",
    version="0.1",
)

# Подключает endpoints пользователя
app.include_router(auth_router, prefix="/auth", tags=["auth"])
# Подключает endpoints объявления
app.include_router(ad_router, prefix="/advertisements", tags=["advertisements"])
# Подключает endpoints пользователя
app.include_router(user_router, prefix="/users", tags=["users"])
