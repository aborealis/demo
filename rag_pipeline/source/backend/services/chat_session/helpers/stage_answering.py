from typing import TYPE_CHECKING
from typing import cast
import asyncio
import logging
import re

from aiobreaker import CircuitBreakerError
from haystack.dataclasses import ChatMessage

import haystack_pipelines.initializator as pipes
from models.orm.chat import ChatStage
from models.schemas.document import QueryContext
from services.celery_tasks.helpers.common import run_celery_task
from services.celery_tasks.common_tasks import update_tokens
from services.celery_tasks.helpers.indexing import search_documents_with_retry
from logging_setup import LogContext, log_extra
from services.common import get_caller_name
import services.chat_session.helpers.common as cmn
import services.celery_tasks.chat_tasks as ctask

if TYPE_CHECKING:
    from services.chat_session.helpers.chat_stage_manager import ChatStageManager

logger = logging.getLogger(__name__)
NO_ANSWER_TEST_MODE_MESSAGE = "The answer is not found, You are now switched to the test mode"


async def process_inbox_stage_answering(
    obj: "ChatStageManager",
    messages: list[ChatMessage],
    lang: str,
) -> tuple[ChatStage, int, list[ChatMessage]] | None:
    logging_context = LogContext(chat_stage=ChatStage.ANSWERING).model_dump(exclude_unset=True)

    logger.info(
        "ENTER STAGE: %s",
        ChatStage.ANSWERING,
        extra=log_extra(event="chat.answering.enter", context=logging_context),
    )

    llm_answer = _build_search_request(messages)
    logger.info(
        "├ NEW SEARCH QUERY: %s",
        llm_answer["search_query"],
        extra=log_extra(
            event="chat.search_query.created",
            context=logging_context,
        ),
    )

    is_repeating_query = await _is_repeating_search_query(obj, llm_answer)
    if is_repeating_query is None:
        return None

    if is_repeating_query:
        text_to_reply = await cmn.translate(
            "Sample text.",
            lang=lang,
        )
        if text_to_reply is None:
            return None

        (last_assistant_msg_idx, updated_messages) = await cmn.send_and_log_assistant_response(
            obj=obj,
            message=text_to_reply,
            messages=messages,
            chat_stage=ChatStage.ANSWERING,
        )

        await cmn.log_chat_stage(obj, ChatStage.TEST)
        if obj.is_test_mode:
            await obj.delivery.safe_send_json(
                {
                    "message": "RAG Search finished. You are now switched to the chat mode"
                }
            )

        logger.info(
            "└ NEXT_STAGE [repeated search query]: %s",
            ChatStage.TEST,
            extra=log_extra(
                event="chat.stage_switched",
                context=logging_context,
                from_stage=ChatStage.ANSWERING,
                to_stage=ChatStage.TEST,
                reason="repeated_search_query",
            ),
        )
        return (ChatStage.TEST, last_assistant_msg_idx, updated_messages)

    await obj.memory.closure.add_search_query(llm_answer["search_query"], **logging_context)
    run_celery_task(
        ctask.add_search_query_to_chat_passport,
        obj.chat_passport_id,
        search_query=llm_answer["search_query"],
    )

    contexts = await search_chunks(obj, query=QueryContext(query=llm_answer["search_query"], top_k=5))

    assistant_text: str
    if not contexts:
        return await _switch_to_test_with_no_answer(obj, messages)
    else:
        if obj.is_test_mode:
            await _send_found_contexts_as_system_message(obj, contexts)

        try:
            result = await asyncio.to_thread(
                pipes.ANSWER_FORMULATION_PIPELINE.run,
                {
                    "prompt": {
                        "search_query": llm_answer["search_query"],
                        "search_intent": llm_answer["search_intent"],
                        "contexts": contexts,
                        "lang": lang,
                    }
                },
            )
        except CircuitBreakerError as e:
            logging_context["calee"] = get_caller_name(2)
            logging_context["caller"] = get_caller_name(3)
            warn_msg = f"Operation failed: {e}"
            logger.warning(
                warn_msg,
                extra=log_extra(
                    event="chat.answer_generation.circuit_open",
                    context=logging_context,
                ),
            )
            return None
        except Exception as e:
            logging_context["calee"] = get_caller_name(2)
            logging_context["caller"] = get_caller_name(3)
            err_msg = f"Operation failed: {e}"
            logger.error(
                err_msg,
                extra=log_extra(
                    event="chat.answer_generation.failed",
                    context=logging_context,
                ),
            )
            raise

        tokens_spent = result["llm"]["meta"][0]["usage"]["total_tokens"]
        if obj.is_test_mode:
            await obj.delivery.safe_send_json({"tokens": tokens_spent})
        run_celery_task(update_tokens, tokens_spent=tokens_spent)

        assistant_text = result["llm"]["replies"][0]

    assistant_text = _strip_think_block(assistant_text)
    if assistant_text.strip().upper() == "HANDOFF":
        return await _switch_to_test_with_no_answer(obj, messages)

    (last_assistant_msg_idx, updated_messages) = await cmn.send_and_log_assistant_response(
        obj,
        message=assistant_text,
        messages=messages,
        chat_stage=ChatStage.ANSWERING,
    )

    await cmn.log_chat_stage(obj, ChatStage.TEST)
    if obj.is_test_mode:
        await obj.delivery.safe_send_json(
            {
                "message": "RAG Search finished. You are now switched to the chat mode"
            }
        )

    logger.info(
        "└ NEXT_STAGE [answer given]: %s",
        ChatStage.TEST,
        extra=log_extra(
            event="chat.stage_switched",
            context=logging_context,
            from_stage=ChatStage.ANSWERING,
            to_stage=ChatStage.TEST,
            reason="answer_given",
        ),
    )

    return (ChatStage.TEST, last_assistant_msg_idx, updated_messages)


def _build_search_request(messages: list[ChatMessage]) -> dict[str, str]:
    user_messages = [m.text for m in messages if m.role == "user" and m.text]
    latest_message = user_messages[-1] if user_messages else ""
    return {
        "search_query": latest_message,
        "search_intent": latest_message,
    }


async def _is_repeating_search_query(
    obj: "ChatStageManager",
    llm_answer: dict[str, str],
) -> bool | None:
    logging_context = LogContext(chat_stage=ChatStage.ANSWERING).model_dump(exclude_unset=True)

    search_query_history: list[str] = await obj.memory.closure.get_search_queries(**logging_context) or []
    logger.info(
        "├ OLD SEARCH QUERIES: %s",
        search_query_history,
        extra=log_extra(
            event="chat.search_query.history_loaded",
            context=logging_context,
        ),
    )

    if not search_query_history:
        return False

    try:
        result = await asyncio.to_thread(
            pipes.SEARCH_QUERIES_COMPARISON_PIPELINE.run,
            {
                "prompt": {
                    "search_queries": search_query_history,
                    "search_query": llm_answer["search_query"],
                }
            },
        )
    except CircuitBreakerError as e:
        logging_context["calee"] = get_caller_name(2)
        logging_context["caller"] = get_caller_name(3)
        warn_msg = f"Operation failed: {e}"
        logger.warning(
            warn_msg,
            extra=log_extra(
                event="chat.search_query.comparison.circuit_open",
                context=logging_context,
            ),
        )
        return None
    except Exception as e:
        logging_context["calee"] = get_caller_name(2)
        logging_context["caller"] = get_caller_name(3)
        err_msg = f"Operation failed: {e}"
        logger.error(
            err_msg,
            extra=log_extra(
                event="chat.search_query.comparison.failed",
                context=logging_context,
            ),
        )
        raise

    tokens_spent = result["llm"]["meta"][0]["usage"]["total_tokens"]
    if obj.is_test_mode:
        await obj.delivery.safe_send_json({"tokens": tokens_spent})
    run_celery_task(update_tokens, tokens_spent=tokens_spent)

    comparison: str = result["llm"]["replies"][0]
    return comparison.lower() == "repeat"


async def search_chunks(
    obj: "ChatStageManager",
    query: QueryContext,
) -> list[str]:
    result = await asyncio.to_thread(
        search_documents_with_retry,
        {
            "query_embedder": {"text": query.query},
            "retriever": {
                "top_k": query.top_k,
            },
        },
    )

    if result is None:
        return []

    tokens_spent = cmn.count_tokens(query.query)
    await obj.delivery.safe_send_json({"tokens": tokens_spent})
    run_celery_task(update_tokens, tokens_spent=tokens_spent)

    return cast(list[str], result["context_extractor"]["contexts"])


def _strip_think_block(text: str) -> str:
    """
    Execute strip think block.
    """
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return cleaned.strip()


async def _switch_to_test_with_no_answer(
    obj: "ChatStageManager",
    messages: list[ChatMessage],
) -> tuple[ChatStage, int, list[ChatMessage]]:
    await obj.delivery.safe_send_text(NO_ANSWER_TEST_MODE_MESSAGE)
    if obj.is_test_mode:
        await obj.delivery.safe_send_json({"message": NO_ANSWER_TEST_MODE_MESSAGE})

    await cmn.log_chat_stage(obj, ChatStage.TEST)
    last_assistant_msg_idx = await obj.memory.get_last_message_idx(
        chat_stage=ChatStage.ANSWERING
    ) or 0

    logger.info(
        "└ NEXT_STAGE [no answer found]: %s",
        ChatStage.TEST,
        extra=log_extra(
            event="chat.stage_switched",
            from_stage=ChatStage.ANSWERING,
            to_stage=ChatStage.TEST,
            reason="answer_not_found",
        ),
    )
    return (ChatStage.TEST, last_assistant_msg_idx, messages)


async def _send_found_contexts_as_system_message(
    obj: "ChatStageManager",
    contexts: list[str],
) -> None:
    logger.info(
        "Found contexts were sent to client in test mode",
        extra=log_extra(
            event="chat.contexts_sent",
            chunks_count=len(contexts),
        ),
    )
    await obj.delivery.safe_send_json(
        {
            "message": "The bot has found the following text chunks with similar semantic meaning:",
            "chunks": contexts,
        }
    )
