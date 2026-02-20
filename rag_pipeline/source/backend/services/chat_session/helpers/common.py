from typing import TYPE_CHECKING, Protocol, Any, Type
import asyncio
import logging
from dataclasses import dataclass

from pydantic import BaseModel, ValidationError
from aiobreaker import CircuitBreakerError

from haystack import Pipeline
from haystack.dataclasses import ChatMessage
import tiktoken

from haystack_pipelines.helpers.common import serialize_chat_messages
from models.orm.chat import ChatStage, ChatPassport, ChatStatus
from services.celery_tasks.common_tasks import update_tokens
from services.common import get_caller_name
from logging_setup import LogContext
from .db_loaders import with_logging
import services.chat_session.helpers.db_loaders as load
import haystack_pipelines.initializator as pipes
import services.celery_tasks.chat_tasks as ctask

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from services.chat_session.chat_session import ChatSession
    from services.chat_session.helpers.chat_stage_manager import ChatStageManager

enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(enc.encode(text))

@dataclass
class ExpectedKeys:
    keys: list[str] | None = None
    variants_of_keys: list[list[str]] | None = None

async def translate(message: str, lang: str) -> str | None:
    logging_context = LogContext(
        callee_name=get_caller_name(2),
        caller_name=get_caller_name(3),
    ).model_dump()
    try:
        result = await asyncio.to_thread(
            pipes.TRANSLATION_PIPELINE.run,
            {"prompt": {"lang": lang, "message": message}},
        )
    except CircuitBreakerError as e:
        warn_msg = f"Operation failed: {e}"
        logger.warning(warn_msg, extra=logging_context)
        return None

    except Exception as e:
        err_msg = f"Operation failed: {e}"
        logger.error(err_msg, extra=logging_context)
        raise

    tokens_spent = result["llm"]["meta"][0]["usage"]["total_tokens"]
    run_celery_task(update_tokens, tokens_spent=tokens_spent)

    return str(result["llm"]["replies"][0])

async def detect_lang(chat_messages: list[ChatMessage]) -> str:
    logging_context = LogContext(
        callee_name=get_caller_name(2),
        caller_name=get_caller_name(3),
    ).model_dump()

    try:
        result = await asyncio.to_thread(
            pipes.LANG_DETECTION_PIPELINE.run,
            {"prompt": {"dialog": serialize_chat_messages(chat_messages)}},
        )
    except CircuitBreakerError as e:
        warn_msg = f"Operation failed: {e}"
        logger.warning(warn_msg, extra=logging_context)
        return "English"

    except Exception as e:
        err_msg = f"Operation failed: {e}"
        logger.error(err_msg, extra=logging_context)
        raise

    tokens_spent = result["llm"]["meta"][0]["usage"]["total_tokens"]
    run_celery_task(update_tokens, tokens_spent=tokens_spent)

    lang: str = result["llm"]["replies"][0]

    if not lang or len(lang.split(" ")) > 1:
        lang = "English"

    return lang

async def read_chat_stage(obj: "ChatStageManager") -> ChatStage:
    logging_context = LogContext(chat_stage=None).model_dump(exclude_unset=True)

    return await obj.memory.get_chat_stage(**logging_context) or ChatStage.ANSWERING

async def log_new_assistant_response(
    obj: "ChatStageManager",
    assistant_msg: ChatMessage,
    chat_stage: ChatStage,
) -> int:
    last_assistant_msg_idx = await obj.memory.append_message(assistant_msg, chat_stage=chat_stage)

    run_celery_task(
        ctask.log_chat_message,
        chat_passport_id=obj.chat_passport_id,
        msg_idx=last_assistant_msg_idx,
        role=assistant_msg.role,
        message=assistant_msg.text,
        chat_stage=chat_stage,
    )

    return int(last_assistant_msg_idx)

async def send_and_log_assistant_response(
    obj: "ChatStageManager",
    message: str,
    messages: list[ChatMessage],
    chat_stage: ChatStage,
) -> tuple[int, list[ChatMessage]]:
    assistant_msg = ChatMessage.from_assistant(message)
    assert assistant_msg.text is not None

    updated_messages = [*messages, assistant_msg]

    last_assistant_msg_idx = await log_new_assistant_response(obj, assistant_msg, chat_stage)

    await obj.delivery.safe_send_text(assistant_msg.text)
    return last_assistant_msg_idx, updated_messages

class CeleryTaskLike(Protocol):
    def delay(self, *args: Any, **kwargs: Any) -> Any:
        ...

def run_celery_task(celery_task: Any, *args: Any, **kwargs: Any) -> None:
    if hasattr(celery_task, "delay"):
        celery_task.delay(*args, **kwargs)
        return
    celery_task(*args, **kwargs)

@with_logging
async def update_passport_on_chat_stop(obj: "ChatSession") -> None:
    def write_db() -> None:
        with load.get_db_sync() as db:
            chat_passport = db.get(ChatPassport, obj.chat_passport_id)
            assert chat_passport is not None
            chat_passport.status = ChatStatus.ARCHIVED
            db.commit()

    await asyncio.to_thread(write_db)

async def log_chat_stage(obj: "ChatStageManager", chat_stage: ChatStage) -> None:
    await obj.memory.set_chat_stage(chat_stage=chat_stage)
    run_celery_task(
        ctask.update_chat_stage,
        chat_passport_id=obj.chat_passport_id,
        chat_stage=chat_stage,
    )
