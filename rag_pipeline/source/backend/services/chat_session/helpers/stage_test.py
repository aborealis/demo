from typing import TYPE_CHECKING
import asyncio
import logging
import re

from aiobreaker import CircuitBreakerError
from haystack.dataclasses import ChatMessage

from models.orm.chat import ChatStage
from services.chat_constants import DEFAULT_CHAT_NO_ANSWER_MESSAGE
from services.celery_tasks.helpers.common import run_celery_task
from logging_setup import LogContext, log_extra
from services.common import get_caller_name
import haystack_pipelines.initializator as pipes
import services.chat_session.helpers.common as cmn
import services.celery_tasks.chat_tasks as ctask

if TYPE_CHECKING:
    from services.chat_session.helpers.chat_stage_manager import ChatStageManager

logger = logging.getLogger(__name__)


async def process_inbox_stage_test(
    obj: "ChatStageManager",
    chat_stage: ChatStage,
    messages: list[ChatMessage],
    lang: str,
) -> int | None:
    logging_context = LogContext(
        callee_name=get_caller_name(2),
        caller_name=get_caller_name(3),
    ).model_dump()

    logger.debug(
        f"STAGE: {chat_stage}",
        extra=log_extra(event="chat.test.enter", context=logging_context),
    )

    try:
        pipeline_result = await asyncio.to_thread(
            pipes.ONE_REQUEST_PIPELINE.run,
            {"llm": {"messages": messages}},
        )
    except CircuitBreakerError as e:
        warn_msg = f"Operation failed: {e}"
        logger.warning(
            warn_msg,
            extra=log_extra(
                event="chat.test.circuit_open",
                context=logging_context,
            ),
        )
        return None

    except Exception as e:
        err_msg = f"Operation failed: {e}"
        logger.error(
            err_msg,
            extra=log_extra(
                event="chat.test.failed",
                context=logging_context,
            ),
        )
        raise

    assistant_msg: ChatMessage = pipeline_result["llm"]["replies"][0]
    tokens_spent = assistant_msg.meta["usage"]["total_tokens"]
    run_celery_task(ctask.update_tokens, tokens_spent=tokens_spent)

    assistant_msg_text = _strip_think_block(assistant_msg.text or "")
    if assistant_msg_text != (assistant_msg.text or ""):
        assistant_msg = ChatMessage.from_assistant(assistant_msg_text)

    if not assistant_msg.text:
        no_answer_message = await cmn.translate(DEFAULT_CHAT_NO_ANSWER_MESSAGE, lang)

        if no_answer_message is None:
            no_answer_message = DEFAULT_CHAT_NO_ANSWER_MESSAGE

        assistant_msg = ChatMessage.from_assistant(no_answer_message)
        assert assistant_msg.text is not None

    last_assistant_msg_idx = await cmn.log_new_assistant_response(obj, assistant_msg, chat_stage)

    await obj.delivery.safe_send_text(assistant_msg.text)

    return last_assistant_msg_idx


def _strip_think_block(text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return cleaned.strip()
