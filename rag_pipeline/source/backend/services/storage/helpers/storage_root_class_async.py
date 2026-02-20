from uuid import UUID
from typing import TypeVar, Union, Awaitable
import inspect

from redis.asyncio import Redis as RedisAsync

from .storage_root_class import BaseChatMemory
from project_settings import (
    CHAT_WINDOW_SIZE,
    DEFAULT_TTL_SECONDS,
    DEFAULT_TTL_BUFFER_SECONDS
)

T = TypeVar("T")


class BaseRedisAsyncManager(BaseChatMemory):
    """Base asynchronous Redis chat-memory manager."""

    def __init__(self,
                 redis: RedisAsync,
                 chat_passport_id: UUID,
                 window_size: int = CHAT_WINDOW_SIZE,
                 ttl_seconds: int = DEFAULT_TTL_SECONDS,
                 ttl_buffer_seconds: int = DEFAULT_TTL_BUFFER_SECONDS,
                 ):
        super().__init__(chat_passport_id=chat_passport_id, window_size=window_size)
        self.redis: RedisAsync = redis
        self.ttl = ttl_seconds
        self.ttl_buffer = ttl_buffer_seconds

    async def _typefix(self, result: Union[T, Awaitable[T]]) -> T:
        """
        Execute typefix.
        """
        if inspect.isawaitable(result):
            return await result
        return result

    async def _set_list(self, key: str, elements: list[str]) -> None:
        """
        Execute set list.
        """
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.delete(key)
            if elements:
                pipe.rpush(key, *elements)
            pipe.expire(key, self.ttl)
            await pipe.execute()

    async def _get_list_len(self, key: str) -> int:
        """
        Execute get list len.
        """
        return await self._typefix(self.redis.llen(key))

    async def _add_to_list(self, key: str, element: str):
        """
        Execute add to list.
        """
        ADD_SCRIPT = """
        redis.call("RPUSH", KEYS[1], ARGV[1])
        if redis.call("TTL", KEYS[1]) == -1 then
            redis.call("EXPIRE", KEYS[1], ARGV[2])
        end
        return 1
        """
        await self._typefix(self.redis.eval(ADD_SCRIPT, 1, key, element, self.ttl))
