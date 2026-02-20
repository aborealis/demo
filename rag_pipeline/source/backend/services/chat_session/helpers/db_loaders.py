from uuid import UUID
from typing import Any, Callable, Awaitable, TypeVar
from contextlib import contextmanager
from functools import wraps
import logging
import inspect

from sqlmodel import Session
from sqlmodel.sql.expression import SelectOfScalar
from sqlalchemy.exc import SQLAlchemyError

from db.session import engine
from logging_setup import LogContext
from services.common import get_caller_name

logger = logging.getLogger(__name__)

T = TypeVar("T")


def load_with_logging():
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            callee_name = func.__name__
            caller_name = get_caller_name(2)

            signature = inspect.signature(func)
            bound_args = signature.bind_partial(*args, **kwargs)
            bound_args.apply_defaults()
            args_with_names = bound_args.arguments

            context = LogContext(
                chat_passport_id=getattr(args[0], "chat_passport_id", None),
                caller_name=caller_name,
                callee_name=callee_name,
                chat_stage=args_with_names.get("chat_stage"),
            ).model_dump()

            try:
                return await func(*args, **kwargs)

            except SQLAlchemyError as e:
                sql_text = getattr(e, "statement", None) or "placeholder SQL"
                logger.exception(
                    f"Database load failed: {sql_text}",
                    extra=context
                )
                raise

        return wrapper

    return decorator


with_logging = load_with_logging()


def load_db_first(statement: SelectOfScalar):
    with get_db_sync() as db:
        return db.exec(statement).first()


def load_db_all(statement: SelectOfScalar):
    with get_db_sync() as db:
        return db.exec(statement).all()


def get_db_object(obj: type[Any], obj_id: int | UUID) -> Any:
    """
    Get db object.
    """
    with get_db_sync() as db:
        return db.get(obj, obj_id)


@contextmanager
def get_db_sync():
    """
    Get db sync.
    """
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
