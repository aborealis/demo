from uuid import UUID
import asyncio
import logging


from services.storage.chat_redis import RedisChatMemoryFastAPI
from models.orm.chat import ChatStage
from .stage_new_message_adding import process_inbox_stage_adding, send_greeting
from .stage_answering import process_inbox_stage_answering
from .stage_test import process_inbox_stage_test
from services.celery_tasks.helpers.common import run_celery_task
from services.common import get_caller_name
from logging_setup import LogContext, log_extra
from services.chat_constants import DEFAUL_CIRCUIT_BREAKER_MSG
from .websocket_delivery_manager import WebSocketDeliveryManager
import services.celery_tasks.chat_tasks as ctask

logger = logging.getLogger(__name__)

ALLOWABLE_TRANSITIONS = {
    "inbox_stage_adding": [ChatStage.ANSWERING, ChatStage.TEST],
    ChatStage.ANSWERING: [ChatStage.ANSWERING, ChatStage.TEST],
    ChatStage.TEST: [ChatStage.TEST],
}


class ChatStageManager:
    def __init__(
        self,
        memory: RedisChatMemoryFastAPI,
        chat_passport_id: UUID,
        delivery: WebSocketDeliveryManager,
        is_test_mode: bool,
    ):
        self.chat_stage = "inbox_stage_adding"
        self.memory = memory
        self.chat_passport_id = chat_passport_id
        self.delivery = delivery
        self.is_test_mode = is_test_mode

    def _is_next_stage_valid(self, next_stage: str) -> bool:
        return next_stage in ALLOWABLE_TRANSITIONS.get(self.chat_stage, [])

    def set_next_stage(self, next_state: str) -> None:
        if not self._is_next_stage_valid(next_state):
            error_msg = f"Invalid state transition: {self.chat_stage} → {next_state}"
            context = LogContext(
                chat_passport_id=self.chat_passport_id,
                caller_name=get_caller_name(2),
                callee_name=get_caller_name(1),
                chat_stage=self.chat_stage,
            ).model_dump()
            logger.error(
                error_msg,
                extra=log_extra(
                    event="chat.stage_transition.invalid",
                    context=context,
                    from_stage=self.chat_stage,
                    to_stage=next_state,
                ),
            )
            self.chat_stage = ChatStage.ANSWERING
        else:
            self.chat_stage = next_state

    async def process_inbox(self) -> None:
        chat_stage: ChatStage | str = "inbox_stage_adding"
        logging_context = LogContext(
            chat_stage=chat_stage).model_dump(exclude_unset=True)

        async with self.memory.lock.acquired_processing_inbox():
            last_assistant_msg_idx = await self.memory.get_last_message_idx(chat_stage=chat_stage)

            chat_stage, messages, lang = await process_inbox_stage_adding(self)
            self.set_next_stage(chat_stage)

            await send_greeting(self, messages, lang, chat_stage=chat_stage)

            if self.chat_stage == ChatStage.ANSWERING:
                result = await process_inbox_stage_answering(obj=self, messages=messages, lang=lang)

                if result is None:
                    await self.delivery.safe_send_text(DEFAUL_CIRCUIT_BREAKER_MSG)
                    return

                chat_stage, last_assistant_msg_idx, messages = result
                self.set_next_stage(chat_stage)

            elif self.chat_stage == ChatStage.TEST:
                last_assistant_msg_idx = await process_inbox_stage_test(
                    obj=self,
                    chat_stage=ChatStage.TEST,
                    messages=messages,
                    lang=lang,
                )

                if last_assistant_msg_idx is None:
                    return

            if not self.delivery.ws_connected():
                logger.info(
                    "Connection closed",
                    extra=log_extra(event="chat.websocket.closed"),
                )
                return

            logging_context = LogContext(
                chat_stage=chat_stage).model_dump(exclude_unset=True)

            logger.info(
                "CHAT: last_assistant_msg_idx: %s %% %s",
                last_assistant_msg_idx,
                self.memory.window_size,
                extra=log_extra(
                    event="chat.summary_window.checkpoint",
                    context=logging_context,
                ),
            )

            if last_assistant_msg_idx % self.memory.window_size == 0:
                logger.info(
                    "CHAT: RUN UPDATE SUMMARY",
                    extra=log_extra(
                        event="chat.summary.update.enqueued",
                        context=logging_context,
                    ),
                )
                run_celery_task(
                    ctask.update_summary_task,
                    chat_passport_id=self.chat_passport_id,
                    idx_summary_cutoff=last_assistant_msg_idx,
                    chat_stage=chat_stage,
                )

                logger.info(
                    "CHAT: RUN UPDATE USER CONTEXT",
                    extra=log_extra(
                        event="chat.user_context.update.enqueued",
                        context=logging_context,
                    ),
                )
                run_celery_task(
                    ctask.update_user_context,
                    chat_passport_id=self.chat_passport_id,
                    chat_stage=chat_stage,
                )

        if await self.memory.inbox_not_empty(**logging_context):
            is_llm_available = await self.memory.lock.try_start_processing_inbox(**logging_context)
            if is_llm_available:
                asyncio.create_task(self.process_inbox())
