from typing import Optional, Any, TypeVar
from uuid import UUID
import logging
import json

from logging_setup import LogContext
from redis.asyncio import Redis as RedisAsync
from haystack.dataclasses import ChatMessage

from models.orm.chat import ChatStage
from .storage_decorators import with_retry, no_retry
from .storage_root_class_async import BaseRedisAsyncManager
from .storage_lock_manager import RedisLockManagerFastAPI
from .storage_context_manager import RedisUserContextyFastAPI
from .storage_classification_manager import RedisClassifStageFastAPI
from .storage_extraction_manager import RedisExtraxctStageFastAPI
from .storage_last_stages_manager import RedisLastStagesFastAPI
from services.chat_constants import SYSTEM_PROMPT_CHAT_INIT
from project_settings import (
    CHAT_WINDOW_SIZE,
    DEFAULT_TTL_SECONDS,
    DEFAULT_TTL_BUFFER_SECONDS
)

logger = logging.getLogger(__name__)
with_retry_async = with_retry(is_async=True)
no_retry_async = no_retry(is_async=True)

T = TypeVar("T")


class RedisChatMemoryFastAPI(BaseRedisAsyncManager):
    """Base class for Redis-backed chat memory operations."""

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
        self.lock = RedisLockManagerFastAPI(*args)
        self.context = RedisUserContextyFastAPI(*args)
        self.classify = RedisClassifStageFastAPI(*args)
        self.extract = RedisExtraxctStageFastAPI(*args)
        self.closure = RedisLastStagesFastAPI(*args)

    @with_retry_async
    async def set_start_msg_index(self,
                                  start_idx: int,
                                  chat_stage: ChatStage | str | None = None):
        """
        Store start msg index.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        idx_key = self._message_idx_key
        exists = await self.redis.exists(idx_key)
        if not exists:
            await self.redis.set(idx_key, start_idx, ex=self.ttl)

    @with_retry_async
    async def append_message(self,
                             message: ChatMessage,
                             chat_stage: ChatStage | str | None = None
                             ) -> int:
        """
        Execute append message.

        :param chat_stage: Current chat stage used for logging and state handling.
        """

        lua_script = """
        local idx = redis.call("INCR", KEYS[1])
        redis.call("EXPIRE", KEYS[1], ARGV[2])
        redis.call("ZADD", KEYS[2], idx, ARGV[1])
        redis.call("EXPIRE", KEYS[2], ARGV[2])
        return idx
        """

        payload = self._serialize_message(message)

        msg_idx = await self._typefix(self.redis.eval(
            lua_script,
            2,
            self._message_idx_key,
            self._messages_key,
            payload,
            self.ttl,
        ))
        return int(msg_idx)

    @with_retry_async
    async def get_messages(self,
                           chat_stage: ChatStage | None = None
                           ) -> list[ChatMessage]:
        """
        Get messages.
        """
        logging_context = LogContext(
            chat_stage=chat_stage,
        ).model_dump(exclude_unset=True)

        messages: list[ChatMessage] = []

        prompt = ChatMessage.from_system(SYSTEM_PROMPT_CHAT_INIT)
        messages.append(prompt)

        user_context = await self.context.get_user_context(**logging_context)
        if user_context:
            messages.append(user_context)

        summary = await self.get_summary(**logging_context)
        if summary:
            messages.append(
                ChatMessage.from_system(
                    f"Conversation summary so far:\n{summary}"
                )
            )

        raw = await self.redis.zrange(self._messages_key, 0, -1,)

        messages = [
            self._deserialize_message(r, chat_stage)
            for r in raw
        ]

        return messages

    @with_retry_async
    async def add_to_inbox(self,
                           message: str,
                           chat_stage: ChatStage | str | None = None):
        """
        Execute add to inbox.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        key = self._inbox_key
        await self._add_to_list(key, message)

    @with_retry_async
    async def inbox_not_empty(self,
                              chat_stage: ChatStage | str | None = None) -> bool:
        """
        Read not empty.

        :param chat_stage: Current chat stage used for logging and state handling.
        :return: ``True`` when the condition is satisfied, otherwise ``False``.
        """
        return await self._typefix(self.redis.llen(self._inbox_key)) > 0

    @with_retry_async
    async def drain_inbox(self,
                          chat_stage: ChatStage | str | None = None
                          ) -> list[str]:
        """
        Execute drain inbox.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        inbox = self._inbox_key
        processing = self._processing_key

        messages: list[str] = []

        while True:
            msg = await self.redis.lmove(
                inbox,
                processing,
                src="LEFT",
                dest="RIGHT"
            )
            if msg is None:
                break
            messages.append(msg)

        return messages

    @with_retry_async
    async def get_inbox_size(self,
                             chat_stage: ChatStage | str | None = None
                             ) -> int:
        """
        Get inbox size.
        """
        key = self._inbox_key
        return await self._get_list_len(key)

    @with_retry_async
    async def clear_processing(self,
                               chat_stage: ChatStage | str | None = None
                               ):
        """
        Execute clear processing.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        await self.redis.delete(self._processing_key)

    @with_retry_async
    async def get_last_message_idx(self,
                                   chat_stage: ChatStage | str | None = None):
        """
        Get last message idx.
        """
        index = await self.redis.get(self._message_idx_key)
        return int(index) if index else 0

    @with_retry_async
    async def set_summary_idx_cutoff_and_stage(
        self,
        summary: str,
        msg_idx_summary_cutoff: int,
        chat_stage: ChatStage | str | None = None,
    ) -> None:
        """
        Set summary idx cutoff and stage.
        """
        pipe = self.redis.pipeline()

        pipe.set(self._summary_key, summary, ex=self.ttl)
        pipe.set(self._summary_until_key,
                 msg_idx_summary_cutoff, ex=self.ttl)
        if chat_stage:
            pipe.set(self._chat_stage_key, chat_stage, ex=self.ttl)

        await pipe.execute()

    @with_retry_async
    async def get_summary(self,
                          chat_stage: ChatStage | str | None = None,
                          ) -> Optional[str]:
        """
        Get summary.
        """
        key = self._summary_key
        return await self.redis.get(key)

    @with_retry_async
    async def set_language(self,
                           lang: str = "",
                           chat_stage: ChatStage | str | None = None,):
        """
        Store language.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        await self.redis.set(self._lang_key, lang, ex=self.ttl)

    @with_retry_async
    async def get_language(self,
                           chat_stage: ChatStage | str | None = None,
                           ):
        """
        Get language.
        """
        return await self.redis.get(self._lang_key)

    @with_retry_async
    async def get_chat_stage(self,
                             chat_stage: ChatStage | str | None = None,
                             ) -> ChatStage | None:
        """
        Get chat stage.
        """
        return await self.redis.get(self._chat_stage_key)

    @with_retry_async
    async def set_chat_stage(self,
                             chat_stage: ChatStage,
                             ) -> None:
        """
        Set chat stage.
        """
        await self.redis.set(self._chat_stage_key, chat_stage, ex=self.ttl)

    @no_retry_async
    async def add_pending_message(self,
                                  sender_name: str,
                                  payload: dict | str,
                                  chat_stage: ChatStage | str | None = None,
                                  ):
        """
        Execute add pending message.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        key = self._pending_messages_key

        # Serialize payload to compact JSON.
        value = json.dumps(
            {"sender": sender_name, "payload": payload}, ensure_ascii=False)

        existing = await self._typefix(self.redis.lrange(key, 0, -1))
        if isinstance(existing, list):
            existing_strs = [
                e.decode("utf-8") if isinstance(e, bytes) else e for e in existing]
            if value in existing_strs:
                return  # Return the result to the caller.

        await self._typefix(self.redis.rpush(key, value))
        # Set TTL for the buffered pending message list.
        await self.redis.expire(key, self.ttl_buffer)

    @with_retry_async
    async def get_pending_messages(self,
                                   chat_stage: ChatStage | str | None = None,
                                   ) -> list[tuple[str, Any]]:
        """
        Get pending messages.
        """
        key = self._pending_messages_key
        items = await self._typefix(self.redis.lrange(key, 0, -1))
        result = []

        for i in items:
            if isinstance(i, bytes):
                i = i.decode("utf-8")
            obj = json.loads(i)
            result.append((obj["sender"], obj["payload"]))

        return result

    @no_retry_async
    async def pop_pending_message(self,
                                  sender_name: str,
                                  payload: Any,
                                  chat_stage: ChatStage | str | None = None,
                                  ):
        """
        Execute pop pending message.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        key = self._pending_messages_key
        value = json.dumps(
            {"sender": sender_name, "payload": payload}, ensure_ascii=False)

        await self._typefix(self.redis.lrem(key, 1, value))
