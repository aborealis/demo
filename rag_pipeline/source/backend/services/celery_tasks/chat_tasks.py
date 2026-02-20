from uuid import UUID
from datetime import datetime, timezone
import logging

from aiobreaker import CircuitBreakerError
from haystack.dataclasses import ChatMessage
from sqlmodel import Session, select

from models.orm.chat import ChatSnapshot, ChatLog, UserContext, ChatStage, ChatPassport, ChatStatus
from services.storage.chat_redis import get_chat_memory_celery
from services.chat_constants import SUMMARY_PROMPT
from services.celery_tasks.helpers.common import celery_db_task, run_celery_task
from services.celery_tasks.common_tasks import update_tokens
from logging_setup import LogContext
import haystack_pipelines.initializator as pipes
from services.common import get_caller_name

logger = logging.getLogger(__name__)


@celery_db_task(task_name="chat.update_chat_stage", use_chat_queue=True)
def update_chat_stage(db: Session, chat_passport_id: UUID, chat_stage: ChatStage) -> None:
    existing_chat_snapshot = db.exec(
        select(ChatSnapshot).where(ChatSnapshot.chat_passport_id == chat_passport_id)
    ).first()

    if not existing_chat_snapshot:
        new_snapshot = ChatSnapshot(
            chat_passport_id=chat_passport_id,
            rolling_summary="",
            msg_idx_summary_cutoff=0,
            chat_stage=chat_stage,
            updated_at=datetime.now(tz=timezone.utc),
        )
        db.add(new_snapshot)
    else:
        existing_chat_snapshot.chat_stage = chat_stage


@celery_db_task(task_name="chat.log_chat_message", use_chat_queue=True)
def log_chat_message(
    db: Session,
    chat_passport_id: UUID,
    msg_idx: int,
    role: str,
    message: str,
    chat_stage: ChatStage,
) -> None:
    new_record = ChatLog(
        chat_passport_id=chat_passport_id,
        stage=chat_stage,
        msg_idx=msg_idx,
        role=role,
        message=message,
    )
    db.add(new_record)


@celery_db_task(task_name="chat.update_summary", use_chat_queue=True)
def update_summary_task(
    db: Session,
    chat_passport_id: UUID,
    idx_summary_cutoff: int,
    chat_stage: ChatStage | None = None,
) -> None:
    logging_context = LogContext(chat_stage=chat_stage).model_dump(exclude_unset=True)

    sync_memory = get_chat_memory_celery(chat_passport_id)

    messages: list[ChatMessage] = sync_memory.get_messages_until(
        idx_summary_cutoff,
        **logging_context,
    )

    if len(messages) < 4:
        return

    summary_messages = [ChatMessage.from_system(SUMMARY_PROMPT)]

    existing_summary = sync_memory.get_summary(**logging_context)
    if existing_summary:
        summary_messages.append(ChatMessage.from_user(f"Existing summary:\n{existing_summary}"))

    summary_messages.append(ChatMessage.from_user("\n".join(f"{m.role}: {m.text}" for m in messages)))

    try:
        result: ChatMessage = pipes.ONE_REQUEST_PIPELINE.run({"llm": {"messages": summary_messages}})[
            "llm"
        ]["replies"][0]

    except CircuitBreakerError as e:
        logging_context["calee"] = get_caller_name(2)
        logging_context["caller"] = get_caller_name(3)
        warn_msg = f"Operation failed: {e}"
        logger.warning(warn_msg, extra=logging_context)
        return

    except Exception as e:
        logging_context["calee"] = get_caller_name(2)
        logging_context["caller"] = get_caller_name(3)
        err_msg = f"Operation failed: {e}"
        logger.error(err_msg, extra=logging_context)
        raise

    tokens_spent = result.meta["usage"]["total_tokens"]
    run_celery_task(update_tokens, tokens_spent=tokens_spent, **logging_context)

    new_summary: str | None = result.text
    if not new_summary:
        return

    sync_memory.set_summary_idx_cutoff_and_stage(new_summary.strip(), idx_summary_cutoff, **logging_context)

    snapshot = db.get(ChatSnapshot, chat_passport_id)

    if snapshot:
        snapshot.rolling_summary = new_summary.strip()
        snapshot.msg_idx_summary_cutoff = idx_summary_cutoff
        snapshot.updated_at = datetime.now(tz=timezone.utc)

    else:
        snapshot = ChatSnapshot(
            chat_passport_id=chat_passport_id,
            rolling_summary=new_summary.strip(),
            msg_idx_summary_cutoff=idx_summary_cutoff,
            updated_at=datetime.now(tz=timezone.utc),
        )
        db.add(snapshot)

    sync_memory.trim_messages_until(until_message_idx=idx_summary_cutoff, **logging_context)


@celery_db_task(task_name="chat.update_user_context", use_chat_queue=True)
def update_user_context(
    db: Session,
    chat_passport_id: UUID,
    chat_stage: ChatStage | None = None,
) -> None:
    logging_context = LogContext(chat_stage=chat_stage).model_dump(exclude_unset=True)

    sync_memory = get_chat_memory_celery(chat_passport_id)

    user_context = sync_memory.get_user_context(**logging_context) or ChatMessage.from_system(
        "No user profile data yet."
    )

    messages: list[ChatMessage] = sync_memory.get_messages(**logging_context)
    user_messages = [m.text for m in messages if m.role == "user" and m.text is not None]

    try:
        result: dict = pipes.USER_CONTEXT_PIPELINE.run(
            {"prompt": {"user_context": user_context, "messages": user_messages}}
        )

    except CircuitBreakerError as e:
        logging_context["calee"] = get_caller_name(2)
        logging_context["caller"] = get_caller_name(3)
        warn_msg = f"Operation failed: {e}"
        logger.warning(warn_msg, extra=logging_context)
        return

    except Exception as e:
        logging_context["calee"] = get_caller_name(2)
        logging_context["caller"] = get_caller_name(3)
        err_msg = f"Operation failed: {e}"
        logger.error(err_msg, extra=logging_context)
        raise

    tokens_spent = result["llm"]["meta"][0]["usage"]["total_tokens"]
    run_celery_task(update_tokens, tokens_spent=tokens_spent, **logging_context)

    new_user_context: str = result["llm"]["replies"][0]

    if not new_user_context:
        return

    sync_memory.set_user_context(new_user_context, **logging_context)

    user_context_db = db.exec(
        select(UserContext).where(UserContext.chat_passport_id == chat_passport_id)
    ).first()

    if user_context_db:
        user_context_db.content = new_user_context

    else:
        user_context_db = UserContext(
            chat_passport_id=chat_passport_id,
            content=new_user_context,
            updated_at=datetime.now(tz=timezone.utc),
        )
        db.add(user_context_db)


@celery_db_task(task_name="chat.set_chat_language", use_chat_queue=True)
def set_chat_language(
    db: Session,
    chat_passport_id: UUID,
    lang: str,
    chat_stage: ChatStage | str | None = None,
) -> None:
    existing_passport = db.get(ChatPassport, chat_passport_id)
    if not existing_passport:
        return

    existing_passport.language = lang


@celery_db_task(task_name="chat.set_chat_status_completed", use_chat_queue=True)
def set_chat_status_completed(
    db: Session,
    chat_passport_id: UUID,
    chat_stage: ChatStage | str | None = None,
) -> None:
    existing_passport = db.get(ChatPassport, chat_passport_id)
    if not existing_passport:
        return

    existing_passport.status = ChatStatus.COMPLETED


@celery_db_task(task_name="chat.add_new_search_query", use_chat_queue=True)
def add_search_query_to_chat_passport(
    db: Session,
    chat_passport_id: UUID,
    search_query: str,
    chat_stage: ChatStage | str | None = None,
) -> None:
    existing_passport = db.get(ChatPassport, chat_passport_id)
    if not existing_passport:
        return

    search_queries = existing_passport.search_queries or []
    search_queries.append(search_query)
    existing_passport.search_queries = search_queries
