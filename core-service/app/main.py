from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import init_db
from app.core.redis import init_redis, close_redis
from . import settings
from .services.kafka import kafka_producer, kafka_consumer
from .api import router as api_router
from .core import setup_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_redis(settings.REDIS_URL)
    await kafka_producer.start()
    await kafka_consumer.start()
    yield
    await kafka_consumer.stop()
    await kafka_producer.stop()
    await close_redis()

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