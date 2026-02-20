from uuid import UUID
from redis.asyncio import Redis as RedisAsync

from .storage_decorators import with_retry
from .storage_root_class_async import BaseRedisAsyncManager
from project_settings import (
    CHAT_WINDOW_SIZE,
    DEFAULT_TTL_SECONDS,
    DEFAULT_TTL_BUFFER_SECONDS
)

with_retry_async = with_retry(is_async=True)


class RedisExtraxctStageFastAPI(BaseRedisAsyncManager):
    """Redis manager for extracted request data."""

    def __init__(self,
                 redis: RedisAsync,
                 chat_passport_id: UUID,
                 window_size: int = CHAT_WINDOW_SIZE,
                 ttl_seconds: int = DEFAULT_TTL_SECONDS,
                 ttl_buffer_seconds: int = DEFAULT_TTL_BUFFER_SECONDS,
                 ):

        args = (redis, chat_passport_id, window_size,
                ttl_seconds, ttl_buffer_seconds)

        super().__init__(*args)
        self.redis = redis
        self.ttl = ttl_seconds
        self.ttl_buffer = ttl_buffer_seconds
