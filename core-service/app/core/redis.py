from typing import Optional
from redis.asyncio import Redis

redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    if redis_client is None:
        raise RuntimeError("Redis не инициализирован.")
    return redis_client


async def init_redis(url: str):
    global redis_client
    redis_client = await Redis.from_url(url, decode_responses=True)


async def close_redis():
    if redis_client:
        await redis_client.close()
