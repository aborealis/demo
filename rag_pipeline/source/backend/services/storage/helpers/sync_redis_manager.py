from typing import Optional, cast
from uuid import UUID
import logging

from redis import Redis as RedisSync
from haystack.dataclasses import ChatMessage

from models.orm.chat import ChatStage
from .storage_root_class import BaseChatMemory
from .storage_decorators import with_retry
from logging_setup import LogContext
from project_settings import CHAT_WINDOW_SIZE, DEFAULT_TTL_SECONDS
from services.chat_constants import SYSTEM_PROMPT_CHAT_INIT

logger = logging.getLogger(__name__)
with_retry_sync = with_retry(is_async=False)


class RedisChatMemoryCelery(BaseChatMemory):
    """Base class for Redis-backed chat memory operations."""

    def __init__(self,
                 redis: RedisSync,
                 chat_passport_id: UUID,
                 window_size: int = CHAT_WINDOW_SIZE,
                 ttl_seconds: int = DEFAULT_TTL_SECONDS,
                 ):
        super().__init__(chat_passport_id, window_size=window_size)
        self.chat_passport_id = chat_passport_id
        self.redis = redis
        self.ttl = ttl_seconds

    @with_retry_sync
    def set_user_context(self,
                         message: str,
                         chat_stage: ChatStage | str | None = None,
                         ):
        """
        Store user context.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        self.redis.set(
            self._user_context_key,
            message,
            ex=self.ttl,
        )

    @with_retry_sync
    def get_user_context(self,
                         chat_stage: ChatStage | str | None = None,
                         ) -> Optional[ChatMessage]:
        """
        Get user context.
        """
        message = cast(str, self.redis.get(self._user_context_key))
        if not message:
            return None
        return ChatMessage.from_system(message)

    @with_retry_sync
    def get_messages_until(self,
                           until_message_idx: int,
                           chat_stage: ChatStage | None = None,
                           ) -> list[ChatMessage]:
        """
        Get messages until.
        """
        raw = cast(list[str], self.redis.zrangebyscore(
            self._messages_key,
            min=0,
            max=until_message_idx,
        ))

        return [
            self._deserialize_message(r, chat_stage=chat_stage)
            for r in raw
        ]

    @with_retry_sync
    def trim_messages_until(self,
                            until_message_idx: int,
                            chat_stage: ChatStage | None = None,
                            ) -> None:
        """
        Trim messages until.

        :param until_message_idx: Message index boundary.
        :param chat_stage: Current chat stage used for logging and state handling.
        """
        self.redis.zremrangebyscore(
            self._messages_key,
            min=0,
            max=until_message_idx,
        )

    @with_retry_sync
    def get_last_message_idx_for_tests(
        self,
        chat_stage: ChatStage | None = None,
    ) -> int:
        """
        Get last message idx for tests.
        """
        key = self._message_idx_key
        index = cast(int, self.redis.get(key))
        return int(index) if index else 0

    @with_retry_sync
    def get_messages_for_tests(self,
                               chat_stage: ChatStage | None = None,
                               ) -> list[tuple[str, str]]:
        """
        Get messages for tests.
        """
        messages_key = self._messages_key
        return cast(
            list[tuple[str, str]],
            self.redis.zrange(messages_key, 0, -1, withscores=True))

    @with_retry_sync
    def get_messages(self,
                     chat_stage: ChatStage | None = None,
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

        user_context: ChatMessage = self.get_user_context(**logging_context)

        if user_context:
            messages.append(user_context)

        summary = self.get_summary(**logging_context)
        if summary:
            messages.append(
                ChatMessage.from_system(
                    f"Conversation summary so far:\n{summary}"
                )
            )

        raw = cast(list[str], self.redis.zrange(self._messages_key, 0, -1))

        for r in raw:
            messages.append(
                self._deserialize_message(r, chat_stage))

        return messages

    @with_retry_sync
    def read_inbox_for_tests(
        self,
        chat_stage: ChatStage | None = None,
    ):
        """
        Read inbox for tests.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        return self.redis.lrange(self._inbox_key, 0, -1)

    @with_retry_sync
    def set_summary_idx_cutoff_and_stage(
        self,
        summary: str,
        idx_summary_cutoff: int,
        chat_stage: ChatStage | None = None,
    ) -> None:
        """
        Set summary idx cutoff and stage.
        """
        pipe = self.redis.pipeline()

        pipe.set(self._summary_key, summary, ex=self.ttl)
        pipe.set(self._summary_until_key,
                 idx_summary_cutoff, ex=self.ttl)

        pipe.execute()

    @with_retry_sync
    def get_summary(self,
                    chat_stage: ChatStage | None = None,
                    ) -> Optional[str]:
        key = self._summary_key
        return cast(Optional[str], self.redis.get(key))
