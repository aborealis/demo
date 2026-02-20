from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from uuid import UUID
from uuid import uuid4

from redis.asyncio import Redis as RedisAsync
from models.orm.chat import ChatStage
from .storage_root_class_async import BaseRedisAsyncManager
from .storage_decorators import with_retry
from project_settings import (
    CHAT_WINDOW_SIZE,
    DEFAULT_TTL_LOCK_SECONDS,
    DEFAULT_TTL_SECONDS,
    DEFAULT_TTL_BUFFER_SECONDS
)


with_retry_async = with_retry(is_async=True)


class RedisLockManagerFastAPI(BaseRedisAsyncManager):
    """Redis-based lock manager for chat processing."""

    def __init__(self,
                 redis: RedisAsync,
                 chat_passport_id: UUID,
                 window_size: int = CHAT_WINDOW_SIZE,
                 ttl_seconds: int = DEFAULT_TTL_SECONDS,
                 ttl_buffer_seconds: int = DEFAULT_TTL_BUFFER_SECONDS,
                 ):
        super().__init__(redis,
                         chat_passport_id=chat_passport_id,
                         window_size=window_size,
                         ttl_seconds=ttl_seconds,
                         ttl_buffer_seconds=ttl_buffer_seconds)
        self.redis = redis
        self.ttl = ttl_seconds
        self.ttl_buffer = ttl_buffer_seconds
        self._lock_token: str | None = None

    @with_retry_async
    async def try_start_processing_inbox(
        self,
        ttl: int = DEFAULT_TTL_LOCK_SECONDS,
        chat_stage: ChatStage | str | None = None,
    ) -> bool:
        """
        Execute try start processing inbox.

        :param chat_stage: Current chat stage used for logging and state handling.
        :return: ``True`` when the condition is satisfied, otherwise ``False``.
        """
        lock_token = uuid4().hex
        inbox_lock_acquired = await self.redis.set(
            self._lock_key,
            lock_token,
            nx=True,
            ex=ttl
        )
        is_acquired = bool(inbox_lock_acquired)
        if is_acquired:
            self._lock_token = lock_token
        return is_acquired

    @with_retry_async
    async def finish_processing_inbox(
        self,
        chat_stage: ChatStage | str | None = None,
    ) -> bool:
        """
        Execute finish processing inbox.

        :param chat_stage: Current chat stage used for logging and state handling.
        :return: ``True`` when the condition is satisfied, otherwise ``False``.
        """
        if self._lock_token is None:
            return False

        release_script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """
        deleted = await self._typefix(
            self.redis.eval(
                release_script,
                1,
                self._lock_key,
                self._lock_token,
            )
        )
        self._lock_token = None
        return bool(deleted)

    @asynccontextmanager
    async def acquired_processing_inbox(
        self,
        chat_stage: ChatStage | str | None = None,
    ) -> AsyncIterator[None]:
        """
        Execute acquired processing inbox.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        try:
            yield
        finally:
            await self.finish_processing_inbox(chat_stage=chat_stage)
