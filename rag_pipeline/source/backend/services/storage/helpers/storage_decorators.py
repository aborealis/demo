
from typing import Any, Callable, Union, NoReturn, TypeVar, Awaitable
import logging
import inspect
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    RetryCallState,
)
import json
from functools import wraps

from redis.exceptions import (
    RedisError,
    ConnectionError,
    TimeoutError,
    ClusterDownError,
    TryAgainError,
    BusyLoadingError,
    AuthenticationError,
    ResponseError,
)
from logging_setup import LogContext

from services.common import get_caller_name

logger = logging.getLogger(__name__)

T = TypeVar("T")

TransientErrors = (
    ConnectionError,
    TimeoutError,
    BusyLoadingError,
    ClusterDownError,
    TryAgainError,
)

TransientErrorsType = Union[
    ConnectionError,
    TimeoutError,
    BusyLoadingError,
    ClusterDownError,
    TryAgainError,
]

CriticalErrors = (
    AuthenticationError,
    ResponseError,
)


def _is_transient_error(exc: BaseException) -> bool:
    if isinstance(exc, (AuthenticationError, ResponseError)):
        return False

    return isinstance(exc, (
        ConnectionError,
        TimeoutError,
        BusyLoadingError,
        ClusterDownError,
        TryAgainError,
    ))


def log_and_raise_exception(error_msg: str,
                            context: LogContext,
                            e: RedisError | KeyError | json.JSONDecodeError | ValueError
                            ) -> NoReturn:
    """
    Execute log and raise exception.
    """
    logger.exception(error_msg, extra=context.model_dump())
    raise e


def with_retry(is_async: bool = True):
    def decorator(func: Callable[..., Any]):

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any):
            return await _execute(func, args, kwargs, is_async=True)

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any):
            return _execute(func, args, kwargs, is_async=False)

        def _execute(
            func: Callable[..., Any],
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
            is_async: bool
        ) -> T | Awaitable[T]:
            callee_name = func.__name__
            caller_name = get_caller_name(1 if is_async else 2)

            signature = inspect.signature(func)
            bound_args = signature.bind_partial(*args, **kwargs)
            bound_args.apply_defaults()
            args_with_names = bound_args.arguments
            chat_passport_id = (
                args[0].chat_passport_id
                if len(args) and hasattr(args[0], "chat_passport_id")
                else None
            )

            context = LogContext(
                # args[0] = self
                chat_passport_id=chat_passport_id,
                caller_name=caller_name,
                callee_name=callee_name,
                chat_stage=args_with_names.get("chat_stage"),
            )

            def before_sleep_with_context(
                retry_state: RetryCallState
            ) -> None:
                exc = (
                    retry_state.outcome.exception()
                    if retry_state.outcome
                    else None
                )

                error_message = str(exc) if exc else "Transient Redis error"

                logger.warning(
                    error_message,
                    extra=context.model_dump(),
                )

            redis_retry = retry(
                retry=retry_if_exception(_is_transient_error),
                stop=stop_after_attempt(3),
                wait=wait_exponential(
                    multiplier=0.5,
                    min=0.5,
                    max=5,
                ),
                before_sleep=before_sleep_with_context,
                reraise=True,
            )

            @redis_retry
            async def async_call():
                try:
                    return await func(*args, **kwargs)
                except CriticalErrors as e:
                    error_msg = f"Operation failed: {e}"
                    log_and_raise_exception(error_msg, context, e)

            @redis_retry
            def sync_call():
                try:
                    return func(*args, **kwargs)
                except CriticalErrors as e:
                    error_msg = f"Operation failed: {e}"
                    log_and_raise_exception(error_msg, context, e)

            return async_call() if is_async else sync_call()

        return async_wrapper if is_async else sync_wrapper

    return decorator


def no_retry(is_async: bool = True):
    """
    Execute no retry.
    """

    def decorator(func: Callable[..., Any]):

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any):
            callee_name = func.__name__
            caller_name = get_caller_name(4)

            signature = inspect.signature(func)
            bound_args = signature.bind_partial(*args, **kwargs)
            bound_args.apply_defaults()
            # OrderedDict {arg_name: value}
            args_with_names = bound_args.arguments

            # Build logging context for error reporting.
            context = LogContext(
                # args[0] == self
                chat_passport_id=args[0].chat_passport_id,
                caller_name=caller_name,
                callee_name=callee_name,
                chat_stage=args_with_names.get("chat_stage"),
            )

            try:
                return func(*args, **kwargs)

            except RedisError as e:
                error_msg = f"Operation failed: {e}"
                log_and_raise_exception(error_msg, context, e)

        if is_async:
            async def async_wrapper(*args: Any, **kwargs: Any):
                return await sync_wrapper(*args, **kwargs)
            return async_wrapper

        return sync_wrapper

    return decorator
