from typing import Any
from uuid import UUID
from collections import deque
import asyncio
import logging

from fastapi import WebSocket, WebSocketDisconnect
from redis.exceptions import RedisError

from services.storage.chat_redis import RedisChatMemoryFastAPI
from services.chat_constants import DEFAULT_CHAT_ERROR_MESSAGE
from services.celery_app import celery_app
from logging_setup import LogContext
from .helpers.common import update_passport_on_chat_stop
from .helpers.websocket_delivery_manager import WebSocketDeliveryManager
from .helpers.chat_stage_manager import ChatStageManager
from project_settings import (
    IS_DEBUG,
    is_app_under_test,
    IDLE_TIMEOUT,
    MAX_SEND_FREQ,
    MAX_MESSAGES_TO_MEASURE_SEND_LIMIT,
    MAX_BUFFERED_OUTGOING_MESSAGES,
    SEND_TIME_WINDOW,
)
import services.chat_session.helpers.load_previous_session as recovery

logger = logging.getLogger(__name__)


class ChatSession:
    def __init__(
        self,
        websocket: WebSocket,
        memory: RedisChatMemoryFastAPI,
        chat_passport_id: UUID,
        is_test_mode: bool,
    ):
        self.websocket = websocket
        self.memory = memory
        self.chat_passport_id = chat_passport_id
        self.is_test_mode = is_test_mode
        self.pending_messages: deque = deque(
            maxlen=MAX_BUFFERED_OUTGOING_MESSAGES)
        self._pending_set: set[tuple[str, Any]] = set()
        self.delivery = WebSocketDeliveryManager(
            websocket,
            memory=memory,
            chat_passport_id=chat_passport_id,
        )
        self.chat_stage_manager = ChatStageManager(
            memory=memory,
            chat_passport_id=chat_passport_id,
            delivery=self.delivery,
            is_test_mode=is_test_mode,
        )
        self._message_timestamps: deque[float] = deque(
            maxlen=MAX_MESSAGES_TO_MEASURE_SEND_LIMIT)

    def _rate_limit_ok(self) -> bool:
        now = asyncio.get_event_loop().time()
        window = SEND_TIME_WINDOW
        limit = MAX_SEND_FREQ * window

        self._message_timestamps.append(now)

        recent = [t for t in self._message_timestamps if now - t < window]
        return len(recent) <= limit

    async def on_connected(self) -> None:
        await self.delivery.flush_pending_messages()

    async def start_accepting(self) -> None:
        try:
            await self._load_previous_session()
        except Exception as e:
            logger.exception(e, exc_info=True)
            await self.delivery.safe_send_text(DEFAULT_CHAT_ERROR_MESSAGE)

        logging_context = LogContext(chat_stage=self.chat_stage_manager.chat_stage).model_dump(
            exclude_unset=True
        )

        while True:
            try:
                user_msg = await asyncio.wait_for(self.websocket.receive_text(), timeout=IDLE_TIMEOUT)

                if user_msg == "STOP":
                    await update_passport_on_chat_stop(self)
                    break

                is_valid, error_msg = self._validate_message(user_msg)
                if not is_valid:
                    await self.delivery.safe_send_text(f"Validation error: {error_msg}")
                    continue

                if not self._rate_limit_ok():
                    await self.delivery.safe_send_text("Too many messages. Slow down.")
                    continue

                inbox_size = await self.memory.get_inbox_size()
                if inbox_size > 50:
                    await self.delivery.safe_send_text("System busy. Please wait.")
                    continue

                await self.memory.add_to_inbox(user_msg, **logging_context)

                inbox_lock_acquired = await self.memory.lock.try_start_processing_inbox(
                    **logging_context,
                )
                if inbox_lock_acquired:
                    asyncio.create_task(
                        self.chat_stage_manager.process_inbox())

            except asyncio.TimeoutError:
                await self.websocket.close(code=1001)
                break

            except WebSocketDisconnect:
                break

            except RedisError:
                await self.delivery.safe_send_text("Temporary memory error. Try again later.")
                continue

            except Exception as e:
                logger.exception(e, exc_info=True)
                await self.delivery.safe_send_text(DEFAULT_CHAT_ERROR_MESSAGE)

    def _validate_message(self, text: str) -> tuple[bool, str]:
        if len(text) > 5000:
            return False, "Message is too long (max 5000 characters)"

        if not text.strip():
            return False, "Message cannot be empty"

        dangerous_patterns = ["<script>", "javascript:", "onload="]
        text_lower = text.lower()
        if any(pattern in text_lower for pattern in dangerous_patterns):
            return False, "Message contains unsafe content"

        return True, ""

    async def _load_previous_session(self) -> None:
        chat_stage = await self.memory.get_chat_stage() or self.chat_stage_manager.chat_stage

        logging_context = LogContext(
            chat_stage=chat_stage).model_dump(exclude_unset=True)

        (
            chat_summary,
            user_context,
            last_msg_index,
            messages,
            lang,
            prev_search_queries,
        ) = await asyncio.gather(
            self.memory.get_summary(**logging_context),
            self.memory.context.get_user_context(**logging_context),
            self.memory.get_last_message_idx(**logging_context),
            self.memory.get_messages(**logging_context),
            self.memory.get_language(**logging_context),
            self.memory.closure.get_search_queries(**logging_context),
        )

        incomplete_message_history = any(
            not val for val in [chat_summary, last_msg_index, messages]
        )

        incomplete_chat_passport_data = any(
            not val for val in [lang, prev_search_queries])

        if incomplete_message_history:
            await recovery.load_and_set_message_history(self, **logging_context)

        if incomplete_chat_passport_data:
            await recovery.load_and_set_lang_and_search_q(self, chat_stage)

        if not user_context:
            await recovery.load_and_set_user_context(self, **logging_context)

        if IS_DEBUG:
            chat_summary = await self.memory.get_summary(**logging_context)
            last_msg_index = await self.memory.get_last_message_idx(**logging_context)
            prev_search_queries = await self.memory.closure.get_search_queries(**logging_context)
            user_context = await self.memory.context.get_user_context(**logging_context)

            logger.debug("LOAD_PREV_SESSION")
            logger.debug("├ CHAT SUMMARY: %s", chat_summary)
            logger.debug("├ LAST MSG INDEX: %s", last_msg_index)
            logger.debug("├ PREV SEARCH QUERIES: %s", prev_search_queries)
            logger.debug("└ USER CONTEXT: %s", user_context)

    async def on_closure(self) -> None:
        if not is_app_under_test():
            return

        while True:
            if not self.has_pending_tasks_for_chat():
                break
            await asyncio.sleep(0.1)

    def has_pending_tasks_for_chat(self) -> bool:
        inspect = celery_app.control.inspect()
        active = inspect.active() or {}
        reserved = inspect.reserved() or {}
        scheduled = inspect.scheduled() or {}

        for worker_tasks in (active, reserved, scheduled):
            for tasks in worker_tasks.values():
                for task in tasks:
                    kwargs = task.get("kwargs", {})
                    args = task.get("args", [])

                    if isinstance(kwargs, dict) and kwargs.get("chat_passport_id") == self.chat_passport_id:
                        return True

                    if self.chat_passport_id in args:
                        return True

        return False
