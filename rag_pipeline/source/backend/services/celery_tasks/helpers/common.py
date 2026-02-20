"""
Общие функции для celery задач
"""
from contextlib import contextmanager
from typing import Callable, Any, cast, Mapping
from functools import wraps
import inspect
import hashlib

# Сторонние модули
import logfire
from celery import Task
import logging
from sqlalchemy import text

# Собственные модули
from db.session import engine
from sqlmodel import Session
from services.celery_app import celery_app
from logging_setup import LogContext
from services.common import get_caller_name
from sqlalchemy.exc import (
    OperationalError,
    DBAPIError,
    DisconnectionError
)

logger = logging.getLogger(__name__)


def run_celery_task(
    celery_task: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Запускает задачу Celery
    """
    _celery_task = cast(Task, celery_task)
    _celery_task.delay(*args, **kwargs)


@contextmanager
def get_db():
    """
    Открывает новую синхронную сессию работы с
    БД для каждой celery задачи.
    """
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


def hash_to_bigint(value: str) -> int:
    """Преобразуем UUID/chat_id в BIGINT для pg_advisory_xact_lock"""
    return int(hashlib.sha256(value.encode()).hexdigest(), 16) % (2**63)


def celery_db_task(task_name: str, use_chat_queue: bool = False):
    """
    Декоратор для Celery задач с автоматическим управлением DB-сессией
    и PostgreSQL advisory lock для последовательности задач одного чата.

    :param task_name: имя задачи Celery
    :param use_chat_queue: если True, используем pg_advisory_xact_lock по chat_passport_id
    """
    def decorator(func: Callable[..., Any]):
        @celery_app.task(
            name=task_name,
            autoretry_for=(OperationalError, DBAPIError, DisconnectionError),
            retry_kwargs={'max_retries': 3, 'countdown': 5},
            retry_backoff=True,
            retry_jitter=True,
            bind=True
        )
        @wraps(func)
        def wrapper(self: Task, *args: Any, **kwargs: Any) -> Any:
            signature = inspect.signature(func)

            with get_db() as db:
                # Добавляем db в args перед биндингом
                bound_args = signature.bind_partial(db, *args, **kwargs)
                bound_args.apply_defaults()
                args_with_names = bound_args.arguments

                callee_name = func.__name__
                caller_name = get_caller_name(2)
                chat_passport_id = args_with_names.get("chat_passport_id")

                context = LogContext(
                    chat_passport_id=chat_passport_id,
                    caller_name=caller_name,
                    callee_name=callee_name,
                    chat_stage=args_with_names.get("chat_stage"),
                ).model_dump()

                try:
                    with db.begin():
                        # PostgreSQL advisory lock для последовательности задач чата
                        if chat_passport_id and use_chat_queue:
                            lock_key = hash_to_bigint(str(chat_passport_id))
                            lock_params: Mapping[str, Any] = {"key": lock_key}
                            logger.info(
                                f"Acquiring lock for chat {chat_passport_id}, key={lock_key}")
                            db.exec(
                                text(
                                    "SELECT pg_advisory_xact_lock(:key)"
                                ).bindparams(**lock_params)  # type: ignore
                            )

                        return func(db, *args, **kwargs)
                except Exception as e:
                    error_message = f"Ошибка в селери задаче {task_name}: {e}"
                    logger.error(error_message, extra=context, exc_info=True)
                    logfire.error(error_message)
                    raise

        return wrapper

    return decorator
