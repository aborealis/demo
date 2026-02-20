from typing import TYPE_CHECKING
import asyncio
import logging

from aiobreaker import CircuitBreakerError
from haystack.dataclasses import ChatMessage

import haystack_pipelines.initializator as pipes
from logging_setup import LogContext, log_extra
from models.orm.chat import ChatStage
from services.chat_constants import GREETING_PROMPT
from services.celery_tasks.helpers.common import run_celery_task
from .common import detect_lang, read_chat_stage
from services.celery_tasks.common_tasks import update_tokens
import services.celery_tasks.chat_tasks as ctask
from services.common import get_caller_name

if TYPE_CHECKING:
    from services.chat_session.helpers.chat_stage_manager import ChatStageManager

logger = logging.getLogger(__name__)


async def process_inbox_stage_adding(
    obj: "ChatStageManager",
) -> tuple[ChatStage, list[ChatMessage], str]:
    chat_stage: ChatStage = await read_chat_stage(obj)

    logging_context = LogContext(chat_stage=chat_stage).model_dump(exclude_unset=True)

    usr_messages = await obj.memory.drain_inbox(**logging_context)
    await obj.memory.clear_processing(**logging_context)

    for text in usr_messages:
        user_msg = ChatMessage.from_user(text)
        user_msg_idx = await obj.memory.append_message(user_msg, **logging_context)

        run_celery_task(
            ctask.log_chat_message,
            chat_passport_id=obj.chat_passport_id,
            msg_idx=user_msg_idx,
            role=user_msg.role,
            message=user_msg.text,
            chat_stage=chat_stage,
        )

    messages = await obj.memory.get_messages(**logging_context)

    lang = await obj.memory.get_language()

    if not lang:
        chat_messages = [ChatMessage.from_user(m) for m in usr_messages]
        lang = await detect_lang(chat_messages)
        logger.info(
            "DEBUG: language %s",
            lang,
            extra=log_extra(
                event="chat.lang_detected",
                context=logging_context,
                language=lang,
            ),
        )
        if obj.is_test_mode:
            await obj.delivery.safe_send_json({"message": f"language detected: {lang}"})

        await obj.memory.set_language(lang, **logging_context)

        run_celery_task(
            ctask.set_chat_language,
            chat_passport_id=obj.chat_passport_id,
            lang=lang,
        )

    return (chat_stage, messages, lang)


async def send_greeting(
    obj: "ChatStageManager",
    messages: list[ChatMessage],
    lang: str,
    chat_stage: ChatStage | str | None = None,
) -> None:
    logging_context = LogContext(chat_stage=chat_stage).model_dump(exclude_unset=True)

    assistent_messages = [m for m in messages if m.role == "assistant"]
    summary = await obj.memory.get_summary(**logging_context)

    if not assistent_messages and not summary:
        prompt = GREETING_PROMPT.replace("{{ lang }}", lang)
        try:
            pipeline_result = await asyncio.to_thread(
                pipes.ONE_REQUEST_PIPELINE.run,
                {"llm": {"messages": [ChatMessage.from_system(prompt)]}},
            )
        except CircuitBreakerError as e:
            logging_context["calee"] = get_caller_name(2)
            logging_context["caller"] = get_caller_name(3)
            warn_msg = f"Operation failed: {e}"
            logger.warning(
                warn_msg,
                extra=log_extra(
                    event="chat.greeting.circuit_open",
                    context=logging_context,
                ),
            )
            return

        except Exception as e:
            logging_context["calee"] = get_caller_name(2)
            logging_context["caller"] = get_caller_name(3)
            err_msg = f"Operation failed: {e}"
            logger.error(
                err_msg,
                extra=log_extra(
                    event="chat.greeting.failed",
                    context=logging_context,
                ),
            )
            raise

        greeting: ChatMessage = pipeline_result["llm"]["replies"][0]

        tokens_spent = greeting.meta["usage"]["total_tokens"]
        run_celery_task(update_tokens, tokens_spent=tokens_spent)

        if greeting.text:
            await obj.delivery.safe_send_text(greeting.text)
