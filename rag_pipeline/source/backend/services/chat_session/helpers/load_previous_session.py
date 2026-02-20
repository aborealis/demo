from typing import TYPE_CHECKING, cast, Optional
from collections.abc import Sequence
import asyncio
import logging

from haystack.dataclasses import ChatMessage
from sqlmodel import select
from sqlmodel.sql.expression import SelectOfScalar

from models.orm.chat import ChatLog, ChatSnapshot, ChatStage, UserContext, ChatPassport
from logging_setup import LogContext
from .db_loaders import with_logging
from services.common import get_caller_name
import services.chat_session.helpers.db_loaders as load

if TYPE_CHECKING:
    from services.chat_session.chat_session import ChatSession

logger = logging.getLogger(__name__)


async def _copy_message_from_sql_to_redis(
    obj: "ChatSession",
    msg: ChatLog,
    chat_stage: ChatStage | str | None = None,
) -> None:
    try:
        if msg.role == "user":
            message = ChatMessage.from_user(msg.message)
        elif msg.role == "assistant":
            message = ChatMessage.from_assistant(msg.message)
        else:
            raise ValueError(f"Unsupported role in chat log: {msg.role}")
        await obj.memory.append_message(message, chat_stage=chat_stage)
    except ValueError as e:
        logging_context = LogContext(
            chat_passport_id=obj.chat_passport_id,
            chat_stage=chat_stage,
            callee_name=get_caller_name(2),
            caller_name=get_caller_name(3),
        ).model_dump()
        error_msg = f"SQL sync to Redis failed: {e}"
        logger.error(error_msg, extra=logging_context, exc_info=True)


@with_logging
async def _load_snapshot_from_sql(
    obj: "ChatSession",
    chat_stage: ChatStage | str | None = None,
) -> ChatSnapshot | None:
    stmt: SelectOfScalar = (
        select(ChatSnapshot).where(
            ChatSnapshot.chat_passport_id == obj.chat_passport_id)
    )

    snapshot: ChatSnapshot = await asyncio.to_thread(load.load_db_first, stmt)

    return snapshot


@with_logging
async def _load_messages_after_cutoff_index(
    obj: "ChatSession",
    snapshot: ChatSnapshot,
    chat_stage: ChatStage | str | None = None,
) -> Sequence[ChatLog]:
    stmt: SelectOfScalar = (
        select(ChatLog)
        .where(ChatLog.chat_passport_id == obj.chat_passport_id)
        .where(ChatLog.msg_idx > snapshot.msg_idx_summary_cutoff)
    )

    old_messages: Sequence[ChatLog] = await asyncio.to_thread(load.load_db_all, stmt)

    return old_messages


@with_logging
async def _load_all_messages(
    obj: "ChatSession",
    chat_stage: ChatStage | str | None,
) -> Sequence[ChatLog]:
    stmt: SelectOfScalar = (
        select(ChatLog)
        .where(ChatLog.chat_passport_id == obj.chat_passport_id)
        .order_by(ChatLog.msg_idx)
    )

    old_messages: Sequence[ChatLog] = await asyncio.to_thread(load.load_db_all, stmt)

    return old_messages


@with_logging
async def load_and_set_message_history(
    obj: "ChatSession",
    chat_stage: ChatStage | str | None,
) -> None:
    logging_context = LogContext(chat_stage=obj.chat_stage_manager.chat_stage).model_dump(
        exclude_unset=True
    )

    old_messages = None
    snapshot = await _load_snapshot_from_sql(obj, **logging_context)

    logging_context = LogContext(
        chat_stage=(
            snapshot.chat_stage if snapshot else obj.chat_stage_manager.chat_stage)
    ).model_dump(exclude_unset=True)

    if snapshot:
        await obj.memory.set_summary_idx_cutoff_and_stage(
            summary=snapshot.rolling_summary,
            msg_idx_summary_cutoff=snapshot.msg_idx_summary_cutoff,
            **logging_context,
        )

        await obj.memory.set_start_msg_index(snapshot.msg_idx_summary_cutoff, **logging_context)

        old_messages = await _load_messages_after_cutoff_index(obj, snapshot, **logging_context)

    else:
        old_messages = await _load_all_messages(obj, **logging_context)

        if old_messages:
            for msg in old_messages:
                await _copy_message_from_sql_to_redis(
                    obj,
                    msg,
                    chat_stage=logging_context["chat_stage"],
                )

        await obj.memory.set_chat_stage(chat_stage=ChatStage.ANSWERING)


@with_logging
async def load_and_set_user_context(
    obj: "ChatSession",
    chat_stage: ChatStage | str | None = None,
) -> None:
    logging_context = LogContext(
        chat_stage=chat_stage).model_dump(exclude_unset=True)

    stmt: SelectOfScalar = (
        select(UserContext).where(
            UserContext.chat_passport_id == obj.chat_passport_id)
    )

    user_context = await asyncio.to_thread(load.load_db_first, stmt)
    user_context = cast(Optional[UserContext], user_context)

    if user_context:
        await obj.memory.context.set_user_context(user_context.content, **logging_context)


@with_logging
async def load_and_set_lang_and_search_q(
    obj: "ChatSession",
    chat_stage: ChatStage | str | None = None,
) -> None:
    logging_context = LogContext(
        chat_stage=chat_stage).model_dump(exclude_unset=True)

    existing_passport = await asyncio.to_thread(
        load.get_db_object,
        obj=ChatPassport,
        obj_id=obj.chat_passport_id,
    )
    existing_passport = cast(Optional[ChatPassport], existing_passport)

    if existing_passport:
        lang = existing_passport.language
        await obj.memory.set_language(lang or "", **logging_context)

    if existing_passport and existing_passport.search_queries:
        await obj.memory.closure.set_search_queries(
            existing_passport.search_queries,
            **logging_context,
        )
