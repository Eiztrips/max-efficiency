from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import init_db
from .api import router as api_router
from .core import setup_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Max",
    description="""ИИ сервис по созданию задач""",
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Eiztrips",
        "url": "https://eiztrips.dev",
        "email": "eiztrips.dev@yandex.ru"
    }
)

setup_middleware(app)

app.include_router(api_router.router_v1)