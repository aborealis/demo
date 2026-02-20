from uuid import UUID

from redis.asyncio import Redis as RedisAsync

from models.orm.chat import ChatStage
from .storage_decorators import with_retry, no_retry
from .storage_root_class_async import BaseRedisAsyncManager
from project_settings import (
    CHAT_WINDOW_SIZE,
    DEFAULT_TTL_SECONDS,
    DEFAULT_TTL_BUFFER_SECONDS
)

with_retry_async = with_retry(is_async=True)
no_retry_async = no_retry(is_async=True)


class RedisLastStagesFastAPI(BaseRedisAsyncManager):
    """Redis manager for the latest chat stages."""

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

    @no_retry_async
    async def add_search_query(self,
                               search_query: str,
                               chat_passport_id: UUID | None = None,
                               chat_stage: ChatStage | str | None = None,
                               ):
        """
        Execute add search query.

        :param search_query: User search query.
        :param chat_passport_id: Chat passport identifier.
        :param chat_stage: Current chat stage used for logging and state handling.
        """
        key = self._search_queries_key
        await self._add_to_list(key, search_query)

    @with_retry_async
    async def set_search_queries(self,
                                 search_queries: list[str],
                                 chat_stage: ChatStage | str | None = None,
                                 ):
        """
        Store search queries.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        key = self._search_queries_key
        await self._set_list(key, search_queries)

    @with_retry_async
    async def get_search_queries(self,
                                 chat_stage: ChatStage | str | None = None,
                                 ):
        """
        Get search queries.
        """
        key = self._search_queries_key
        return await self._typefix(self.redis.lrange(key, 0, -1))
