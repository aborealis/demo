
from uuid import UUID

from redis.asyncio import Redis as RedisAsync

from models.orm.chat import ChatStage
from .storage_root_class_async import BaseRedisAsyncManager
from .storage_decorators import with_retry
from project_settings import (
    CHAT_WINDOW_SIZE,
    DEFAULT_TTL_SECONDS,
    DEFAULT_TTL_BUFFER_SECONDS
)

with_retry_async = with_retry(is_async=True)


class RedisClassifStageFastAPI(BaseRedisAsyncManager):
    """Redis manager for request classification data."""

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

    @with_retry_async
    async def set_bot_shortname(self,
                                bot_shortname: str,
                                chat_stage: ChatStage | str | None = None,
                                ):
        """
        Store bot shortname.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        key = self._bot_shortname_key
        await self.redis.set(key, bot_shortname, ex=self.ttl)
