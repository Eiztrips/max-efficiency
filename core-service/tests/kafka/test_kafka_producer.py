import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from app.services.kafka.producer import KafkaProducerService
from app.schemas.ai import InputMessage


@pytest_asyncio.fixture
async def kafka_producer_service():
    """Фикстура для KafkaProducerService"""
    service = KafkaProducerService()
    yield service
    if service.producer:
        await service.stop()


@pytest_asyncio.fixture
async def mock_aiokafka_producer():
    """Мок для AIOKafkaProducer"""
    with patch('app.services.kafka.producer.AIOKafkaProducer') as mock_producer_class:
        mock_producer = AsyncMock()
        mock_producer_class.return_value = mock_producer
        yield mock_producer


class TestKafkaProducerService:
    """Тесты для KafkaProducerService"""

    @pytest.mark.asyncio
    async def test_start_producer(self, kafka_producer_service, mock_aiokafka_producer):
        """Тест инициализации продюсера"""
        await kafka_producer_service.start()

        assert kafka_producer_service.producer is not None
        mock_aiokafka_producer.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_producer(self, kafka_producer_service, mock_aiokafka_producer):
        """Тест остановки продюсера"""
        await kafka_producer_service.start()
        await kafka_producer_service.stop()

        mock_aiokafka_producer.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_producer_when_not_started(self, kafka_producer_service):
        """Тест остановки продюсера, который не был запущен"""
        await kafka_producer_service.stop()

    @pytest.mark.asyncio
    async def test_send_task_request_success(self, kafka_producer_service, mock_aiokafka_producer):
        """Тест успешной отправки сообщения"""
        await kafka_producer_service.start()

        message = InputMessage(
            task_id="test-task-123",
            prompt="Test prompt",
            tags=["tag1", "tag2"],
            categories=["category1"]
        )

        await kafka_producer_service.send_task_request(message)

        mock_aiokafka_producer.send.assert_called_once()
        call_args = mock_aiokafka_producer.send.call_args
        assert call_args[1]["value"] == message.model_dump()

    @pytest.mark.asyncio
    async def test_send_task_request_without_tags(self, kafka_producer_service, mock_aiokafka_producer):
        """Тест отправки сообщения без тегов"""
        await kafka_producer_service.start()

        message = InputMessage(
            task_id="test-task-456",
            prompt="Test prompt without tags",
            tags=None,
            categories=["category1"]
        )

        await kafka_producer_service.send_task_request(message)

        mock_aiokafka_producer.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_task_request_not_initialized(self, kafka_producer_service):
        """Тест отправки сообщения без инициализации продюсера"""
        message = InputMessage(
            task_id="test-task-789",
            prompt="Test prompt",
            tags=["tag1"],
            categories=["category1"]
        )

        with pytest.raises(RuntimeError, match="Кафка продюсер не инициализирован"):
            await kafka_producer_service.send_task_request(message)

    @pytest.mark.asyncio
    async def test_send_task_request_with_empty_categories(self, kafka_producer_service, mock_aiokafka_producer):
        """Тест отправки сообщения с пустым списком категорий"""
        await kafka_producer_service.start()

        message = InputMessage(
            task_id="test-task-999",
            prompt="Test prompt with empty categories",
            tags=["tag1"],
            categories=[]
        )

        await kafka_producer_service.send_task_request(message)

        mock_aiokafka_producer.send.assert_called_once()
