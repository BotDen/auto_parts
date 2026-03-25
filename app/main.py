from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.database import engine, Model
from users.routers.auth_routers import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="AutoParts",
    description="Сервис по покупке и продаже автозапчастей",
    version="0.1",
)

app.include_router(auth_router)
