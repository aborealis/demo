from uuid import UUID
import json

from haystack.dataclasses import ChatMessage
from project_settings import CHAT_WINDOW_SIZE
from logging_setup import LogContext

from models.orm.chat import ChatStage
from services.common import get_caller_name
from .storage_decorators import (
    log_and_raise_exception,
    TransientErrors,
    CriticalErrors,
)


class BaseChatMemory:
    """Base class for Redis-backed chat memory operations."""

    def __init__(self,
                 chat_passport_id: UUID,
                 window_size: int = CHAT_WINDOW_SIZE,
                 key_prefix: str = "chat",
                 ):
        self.chat_passport_id = chat_passport_id
        self.window_size = window_size
        self.prefix = key_prefix
        self.TransientErrors = TransientErrors
        self.CriticalErrors = CriticalErrors

    def _serialize_message(self, message: ChatMessage) -> str:
        """
        Serialize message.
        """
        return json.dumps(
            {
                "role": message.role,
                "content": message.text,
            },
            ensure_ascii=False,
        )

    def _deserialize_message(self,
                             raw: str,
                             chat_stage: ChatStage | None = None
                             ) -> ChatMessage:
        """
        Deserialize message.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        # Build logging context for error reporting.
        context = LogContext(
            chat_passport_id=self.chat_passport_id,
            caller_name=get_caller_name(2),
            callee_name=get_caller_name(1),
            chat_stage=chat_stage,
        )

        try:
            data = json.loads(raw)
            role = data["role"]
            content = data["content"]

            if role == "system":
                return ChatMessage.from_user(content)
            if role == "user":
                return ChatMessage.from_user(content)
            if role == "assistant":
                return ChatMessage.from_assistant(content)

            error_msg = f"Invalid chat role: {role}"
            raise ValueError(error_msg)

        except (KeyError, ValueError, json.JSONDecodeError) as e:
            error_msg = "Failed to deserialize chat message from storage"
            log_and_raise_exception(error_msg, context, e)

    @property
    def _messages_key(self) -> str:
        return f"{self.prefix}:{self.chat_passport_id}:messages"

    @property
    def _inbox_key(self) -> str:
        return f"{self.prefix}:{self.chat_passport_id}:inbox"

    @property
    def _summary_key(self) -> str:
        return f"{self.prefix}:{self.chat_passport_id}:summary"

    @property
    def _message_idx_key(self) -> str:
        return f"{self.prefix}:{self.chat_passport_id}:message_idx"

    @property
    def _summary_until_key(self) -> str:
        return f"{self.prefix}:{self.chat_passport_id}:summary_until"

    @property
    def _user_context_key(self) -> str:
        return f"{self.prefix}:{self.chat_passport_id}:user_context"

    @property
    def _lock_key(self) -> str:
        return f"{self.prefix}:{self.chat_passport_id}:lock"

    @property
    def _processing_key(self) -> str:
        return f"{self.prefix}:{self.chat_passport_id}:processing"

    @property
    def _chat_stage_key(self) -> str:
        return f"{self.prefix}:{self.chat_passport_id}:chat_stage"

    @property
    def _lang_key(self) -> str:
        return f"{self.prefix}:{self.chat_passport_id}:lang"

    @property
    def _bot_shortname_key(self) -> str:
        return f"{self.prefix}:{self.chat_passport_id}:bot_shortname"

    @property
    def _search_queries_key(self) -> str:
        return f"{self.prefix}:{self.chat_passport_id}:search_queries"

    @property
    def _pending_messages_key(self) -> str:
        return f"{self.prefix}:{self.chat_passport_id}:pending"
