
from typing import Callable, Awaitable, Any
from uuid import UUID
from collections import deque
import asyncio
import logging
import json

from redis import RedisError

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from services.storage.chat_redis import RedisChatMemoryFastAPI
from models.orm.chat import ChatStage
from logging_setup import LogContext, log_extra
from project_settings import MAX_SEND_TIME_BEFORE_RETRY

logger = logging.getLogger(__name__)


class WebSocketDeliveryManager:

    def __init__(
        self,
        websocket: WebSocket,
        memory: RedisChatMemoryFastAPI,
        chat_passport_id: UUID,
    ):
        self.websocket = websocket
        self.memory = memory
        self.chat_passport_id = chat_passport_id
        self.pending_messages: deque = deque(maxlen=50)
        self._pending_set: set[tuple[str, Any]] = set()

    def ws_connected(self) -> bool:
        return (
            self.websocket.client_state == WebSocketState.CONNECTED
            and self.websocket.application_state == WebSocketState.CONNECTED
        )

    def _log_if_buffer_is_full(self,
                               caller_name: str | None = None,
                               chat_stage: ChatStage | None = None) -> None:
        """
        Execute log if buffer is full.

        :param chat_stage: Current chat stage used for logging and state handling.
        """
        warn_msg = (
            "Pending messages buffer full at final retry. Oldest message will be dropped: {}"
        ).format(self.pending_messages[0][1] if self.pending_messages else None)

        if (
            self.pending_messages.maxlen is not None
            and len(self.pending_messages) >= self.pending_messages.maxlen
        ):
            logger.warning(
                warn_msg,
                extra=log_extra(
                    event="chat.websocket.buffer_overflow",
                    chat_passport_id=self.chat_passport_id,
                    caller_name=caller_name,
                    chat_stage=chat_stage,
                ),
            )

    def _append_pending_key(self, key: tuple[str, Any]) -> None:
        """
        Execute append pending key.
        """
        if (
            self.pending_messages.maxlen is not None
            and len(self.pending_messages) >= self.pending_messages.maxlen
            and self.pending_messages
        ):
            dropped = self.pending_messages[0]
            self._pending_set.discard(dropped)

        self.pending_messages.append(key)
        self._pending_set.add(key)

    async def safe_send(
        self,
        payload: str | dict[str, str] | None,
        sender: Callable[[Any], Awaitable[None]],
        *,
        retry_count: int = 3,
        use_buffer_on_fail: bool = True,
        backoff_base: float = 0.5,
        caller_name: str | None = None,
        chat_stage: ChatStage | None = None,
    ) -> bool:
        """
        Execute safe send.

        :param chat_stage: Current chat stage used for logging and state handling.
        :return: ``True`` when the condition is satisfied, otherwise ``False``.
        """
        if payload is None:
            return False

        for attempt in range(retry_count):
            if not self.ws_connected():
                if use_buffer_on_fail:
                    key = (
                        sender.__name__,
                        json.dumps(
                            payload,
                            sort_keys=True,
                            # Use compact separators to reduce payload size.
                            separators=(",", ":"),
                            ensure_ascii=False,
                            # Serialize unsupported objects through `str`.
                            default=str,
                        )
                    )
                    if key not in self._pending_set:
                        self._append_pending_key(key)
                        self._log_if_buffer_is_full(caller_name, chat_stage)

                    await self.memory.add_pending_message(
                        sender_name=sender.__name__,
                        payload=payload,
                        chat_stage=chat_stage,
                    )

                await asyncio.sleep(backoff_base * (attempt + 1))
                continue

            try:
                await asyncio.wait_for(sender(payload), timeout=MAX_SEND_TIME_BEFORE_RETRY)
                await self.memory.pop_pending_message(
                    sender_name=sender.__name__,
                    payload=payload,
                    chat_stage=chat_stage,
                )
                return True

            except asyncio.TimeoutError as e:
                logger.warning(
                    f"Operation failed: {e}",
                    extra=log_extra(
                        event="chat.websocket.send_timeout",
                        chat_passport_id=self.chat_passport_id,
                        caller_name=caller_name,
                        chat_stage=chat_stage,
                    ),
                )
                if attempt < retry_count - 1:
                    await asyncio.sleep(backoff_base * (attempt + 1))
                    continue
                break

            except RuntimeError as e:
                logger.error(
                    f"Operation failed: {e}",
                    extra=log_extra(
                        event="chat.websocket.send_runtime_error",
                        chat_passport_id=self.chat_passport_id,
                        caller_name=caller_name,
                        chat_stage=chat_stage,
                    ),
                )
                if attempt < retry_count - 1:
                    await asyncio.sleep(backoff_base * (attempt + 1))

        if use_buffer_on_fail:
            await self.memory.add_pending_message(
                sender_name=sender.__name__,
                payload=payload,
                chat_stage=chat_stage,
            )
            self._log_if_buffer_is_full()

        return False

    async def flush_pending_messages(self) -> None:
        """Flush buffered pending messages after reconnection."""
        logging_context = LogContext(
            chat_stage=None,
        ).model_dump(exclude_unset=True)

        try:
            pending_from_redis = await self.memory.get_pending_messages(chat_stage=None)

            for sender_name, payload in pending_from_redis:
                key = (sender_name, json.dumps(payload)
                       if isinstance(payload, dict) else payload)
                if key not in self._pending_set:
                    self._append_pending_key(key)

            while self.pending_messages and self.ws_connected():
                sender_name, payload = self.pending_messages.popleft()
                self._pending_set.remove((sender_name, payload))
                sender = getattr(self.websocket, sender_name)
                try:
                    if isinstance(payload, str) and sender_name == "send_json":
                        payload = json.loads(payload)
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON payload in pending queue: {e}"
                    logger.warning(
                        error_msg,
                        extra=log_extra(
                            event="chat.websocket.flush.invalid_json",
                            context=logging_context,
                            chat_passport_id=self.chat_passport_id,
                        ),
                    )
                    payload = dict()

                try:
                    await asyncio.wait_for(sender(payload), timeout=MAX_SEND_TIME_BEFORE_RETRY)
                    await self.memory.pop_pending_message(
                        sender_name=sender_name,
                        payload=payload,
                        chat_stage=None,
                    )

                except (RuntimeError, asyncio.TimeoutError) as e:
                    logger.warning(
                        f"Operation failed: {e}",
                        extra=log_extra(
                            event="chat.websocket.flush.send_failed",
                            context=logging_context,
                            chat_passport_id=self.chat_passport_id,
                        ),
                    )
                    self.pending_messages.appendleft((sender_name, payload))
                    self._pending_set.add((sender_name, payload))
                    break
        except RedisError as e:
            error_msg = f"Operation failed: {e}"
            logger.warning(
                error_msg,
                extra=log_extra(
                    event="chat.websocket.flush.redis_unavailable",
                    context=logging_context,
                    chat_passport_id=self.chat_passport_id,
                ),
            )

    async def safe_send_text(self, text: str) -> bool:
        return await self.safe_send(
            text,
            self.websocket.send_text,
        )

    async def safe_send_json(self, data: dict) -> bool:
        return await self.safe_send(
            data,
            self.websocket.send_json,
        )
