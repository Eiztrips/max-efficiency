import json
from app.core.redis import get_redis
from app.schemas.ai import RedisTaskMessage


class RedisTaskService:
    """Сервис для работы с задачами в Redis"""

    TASK_PREFIX = "task:"
    TASK_TTL = 360

    @staticmethod
    async def save_task(task_id: str, payload: RedisTaskMessage) -> bool:
        redis = await get_redis()
        key = RedisTaskService.TASK_PREFIX + task_id
        value = json.dumps(payload.model_dump())
        result = await redis.set(key, value, ex=RedisTaskService.TASK_TTL)
        return result

    @staticmethod
    async def get_task(task_id: str) -> RedisTaskMessage | None:
        redis = await get_redis()
        key = RedisTaskService.TASK_PREFIX + task_id
        value = await redis.get(key)
        if value is None:
            return None
        data = json.loads(value)
        return RedisTaskMessage(**data)

    @staticmethod
    async def delete_task(task_id: str) -> bool:
        redis = await get_redis()
        key = RedisTaskService.TASK_PREFIX + task_id
        result = await redis.delete(key)
        return result == 1

redis_task_service = RedisTaskService()
