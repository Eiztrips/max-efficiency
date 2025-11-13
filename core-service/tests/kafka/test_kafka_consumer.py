import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from app.services.kafka.consumer import KafkaConsumerService


@pytest_asyncio.fixture
async def kafka_consumer_service():
    """Фикстура для KafkaConsumerService"""
    service = KafkaConsumerService()
    yield service
    if service.running:
        await service.stop()


@pytest_asyncio.fixture
async def mock_aiokafka_consumer():
    """Мок для AIOKafkaConsumer"""
    with patch('app.services.kafka.consumer.AIOKafkaConsumer') as mock_consumer_class:
        mock_consumer = AsyncMock()
        mock_consumer_class.return_value = mock_consumer
        yield mock_consumer


class TestKafkaConsumerService:
    """Тесты для KafkaConsumerService (MVP)"""

    @pytest.mark.asyncio
    async def test_start_consumer(self, kafka_consumer_service, mock_aiokafka_consumer):
        """Тест запуска консьюмера"""
        await kafka_consumer_service.start()

        assert kafka_consumer_service.consumer is not None
        assert kafka_consumer_service.running is True
        mock_aiokafka_consumer.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_consumer(self, kafka_consumer_service, mock_aiokafka_consumer):
        """Тест остановки консьюмера"""
        await kafka_consumer_service.start()
        await kafka_consumer_service.stop()

        assert kafka_consumer_service.running is False
        mock_aiokafka_consumer.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_consumer_when_not_started(self, kafka_consumer_service):
        """Тест остановки консьюмера, который не был запущен"""
        await kafka_consumer_service.stop()

        assert kafka_consumer_service.running is False

    @pytest.mark.asyncio
    async def test_consumer_initialization(self, kafka_consumer_service):
        """Тест начального состояния консьюмера"""
        assert kafka_consumer_service.consumer is None
        assert kafka_consumer_service.running is False

    @pytest.mark.asyncio
    async def test_start_sets_running_flag(self, kafka_consumer_service, mock_aiokafka_consumer):
        """Тест установки флага running при запуске"""
        assert kafka_consumer_service.running is False

        await kafka_consumer_service.start()

        assert kafka_consumer_service.running is True


