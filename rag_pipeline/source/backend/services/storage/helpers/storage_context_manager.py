from typing import Optional
from uuid import UUID


from redis.asyncio import Redis as RedisAsync
from haystack.dataclasses import ChatMessage

from models.orm.chat import ChatStage
from .storage_root_class_async import BaseRedisAsyncManager
from .storage_decorators import with_retry
from project_settings import (
    CHAT_WINDOW_SIZE,
    DEFAULT_TTL_SECONDS,
    DEFAULT_TTL_BUFFER_SECONDS
)


with_retry_async = with_retry(is_async=True)


class RedisUserContextyFastAPI(BaseRedisAsyncManager):
    """Redis manager for user context storage."""

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
    async def set_user_context(self,
                               message: str,
                               chat_stage: ChatStage | str | None = None
                               ):
        """
        Store user context.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        await self.redis.set(
            self._user_context_key,
            message,
            ex=self.ttl,
        )

    @with_retry_async
    async def get_user_context(self,
                               chat_stage: ChatStage | str | None = None
                               ) -> Optional[ChatMessage]:
        """
        Get user context.
        """
        message = await self.redis.get(self._user_context_key)
        if not message:
            return None
        return ChatMessage.from_system(message)
