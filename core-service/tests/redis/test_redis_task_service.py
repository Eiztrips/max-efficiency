import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
import json

from app.services.redis.redis import RedisTaskService
from app.schemas.ai import RedisTaskMessage


@pytest_asyncio.fixture
async def mock_redis():
    """Мок для Redis клиента"""
    redis_mock = AsyncMock()
    with patch('app.services.redis.redis.get_redis', return_value=redis_mock):
        yield redis_mock


class TestRedisTaskService:
    """Тесты для RedisTaskService"""

    @pytest.mark.asyncio
    async def test_save_task_success(self, mock_redis):
        """Тест успешного сохранения задачи в Redis"""
        task_id = "test-task-123"
        payload = RedisTaskMessage(
            task_id=task_id,
            user_id=1,
            category_id=10
        )

        mock_redis.set.return_value = True

        result = await RedisTaskService.save_task(task_id, payload)

        assert result is True
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert call_args[0][0] == f"{RedisTaskService.TASK_PREFIX}{task_id}"
        assert call_args[1]["ex"] == RedisTaskService.TASK_TTL

    @pytest.mark.asyncio
    async def test_save_task_without_category(self, mock_redis):
        """Тест сохранения задачи без категории"""
        task_id = "test-task-456"
        payload = RedisTaskMessage(
            task_id=task_id,
            user_id=2,
            category_id=None
        )

        mock_redis.set.return_value = True

        result = await RedisTaskService.save_task(task_id, payload)

        assert result is True
        mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_task_success(self, mock_redis):
        """Тест успешного получения задачи из Redis"""
        task_id = "test-task-789"
        expected_data = RedisTaskMessage(
            task_id=task_id,
            user_id=3,
            category_id=20
        )

        mock_redis.get.return_value = json.dumps(expected_data.model_dump())

        result = await RedisTaskService.get_task(task_id)

        assert result is not None
        assert result.task_id == expected_data.task_id
        assert result.user_id == expected_data.user_id
        assert result.category_id == expected_data.category_id
        mock_redis.get.assert_called_once_with(f"{RedisTaskService.TASK_PREFIX}{task_id}")

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, mock_redis):
        """Тест получения несуществующей задачи"""
        task_id = "nonexistent-task"
        mock_redis.get.return_value = None

        result = await RedisTaskService.get_task(task_id)

        assert result is None
        mock_redis.get.assert_called_once_with(f"{RedisTaskService.TASK_PREFIX}{task_id}")

    @pytest.mark.asyncio
    async def test_delete_task_success(self, mock_redis):
        """Тест успешного удаления задачи"""
        task_id = "test-task-delete"
        mock_redis.delete.return_value = 1

        result = await RedisTaskService.delete_task(task_id)

        assert result is True
        mock_redis.delete.assert_called_once_with(f"{RedisTaskService.TASK_PREFIX}{task_id}")

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, mock_redis):
        """Тест удаления несуществующей задачи"""
        task_id = "nonexistent-task"
        mock_redis.delete.return_value = 0

        result = await RedisTaskService.delete_task(task_id)

        assert result is False
        mock_redis.delete.assert_called_once_with(f"{RedisTaskService.TASK_PREFIX}{task_id}")

