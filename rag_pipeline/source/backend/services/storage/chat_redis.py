from uuid import UUID
from redis.asyncio import Redis as RedisAsync
from redis import Redis as RedisSync

from .helpers.async_redis_manager import RedisChatMemoryFastAPI
from .helpers.sync_redis_manager import RedisChatMemoryCelery
from project_settings import (
    CHAT_WINDOW_SIZE,
    REDIS_URL,
    DEFAULT_TTL_SECONDS,
    DEFAULT_TTL_BUFFER_SECONDS
)


async def get_chat_memory_fastapi(
        chat_passport_id: UUID,
) -> RedisChatMemoryFastAPI:
    """
    Get chat memory fastapi.
    """
    redis = await RedisAsync.from_url(REDIS_URL, decode_responses=True)
    return RedisChatMemoryFastAPI(
        redis,
        chat_passport_id=chat_passport_id,
        window_size=CHAT_WINDOW_SIZE,
        ttl_seconds=DEFAULT_TTL_SECONDS,
        ttl_buffer_seconds=DEFAULT_TTL_BUFFER_SECONDS,
    )


def get_chat_memory_celery(
        chat_passport_id: UUID,
) -> RedisChatMemoryCelery:
    """
    Get chat memory celery.
    """
    redis = RedisSync.from_url(REDIS_URL, decode_responses=True)
    return RedisChatMemoryCelery(
        redis,
        chat_passport_id=chat_passport_id,
        window_size=CHAT_WINDOW_SIZE,
        ttl_seconds=DEFAULT_TTL_SECONDS,
    )
