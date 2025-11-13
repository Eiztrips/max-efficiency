import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from unittest.mock import AsyncMock, patch

from app.main import app
from app.database import get_db
from app.models.base import Base
from app.services.kafka.producer import KafkaProducerService

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Создает async engine для тестовой БД"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine):
    """Создает async session для каждого теста"""
    async_session_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def mock_kafka_producer():
    """Мок для Kafka Producer в API тестах"""
    with patch('app.services.kafka.producer.kafka_producer.send_task_request', new_callable=AsyncMock) as mock_send:
        yield mock_send


@pytest_asyncio.fixture(autouse=True)
async def mock_redis():
    """Мок для Redis в API тестах"""
    with patch('app.services.redis.redis.RedisTaskService.save_task', new_callable=AsyncMock) as mock_save:
        with patch('app.services.redis.redis.RedisTaskService.get_task', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            yield mock_save, mock_get


@pytest_asyncio.fixture
async def client(db_session):
    """Создает тестовый HTTP клиент с переопределенной БД"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
