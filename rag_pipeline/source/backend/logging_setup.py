"""Project logging configuration and helper structures."""
from __future__ import annotations

from typing import Any, Final
import logging
import sys
from uuid import UUID
import json
from pydantic import BaseModel
from colorama import Fore, Back, Style
from models.orm.chat import ChatStage
from project_settings import IS_DEBUG


# Build logging context for error reporting.
class LogContext(BaseModel):
    chat_passport_id: UUID | None = None
    caller_name: str | None = "-"  # Default when caller name is unavailable.
    callee_name: str | None = "-"  # Default when callee name is unavailable.
    chat_stage: ChatStage | str | None = None


def log_extra(
    *,
    event: str,
    context: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Execute log extra.
    """
    payload: dict[str, Any] = {}
    if context:
        payload.update(context)

    payload["event"] = event
    payload.update({k: v for k, v in kwargs.items() if v is not None})
    return payload


LOGGING_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

_COLORS: Final[dict[str, str]] = {
    "DEBUG": Fore.LIGHTBLUE_EX,
    "INFO": Fore.LIGHTGREEN_EX,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Back.RED + Fore.WHITE,
}
_RESET: Final[str] = f"{Fore.RESET}{Back.RESET}{Style.RESET_ALL}"

_STANDARD_ATTRS = set(logging.LogRecord(
    name="", level=0, pathname="", lineno=0,
    msg="", args=(), exc_info=None
).__dict__.keys())

_GRAYED_LOGGERS = [
    "uvicorn",
    "urllib3",
    "httpx",
    "haystack.core.pipeline",
]

_STOP_JSON_KEYS = [
    "message",
    "color_message",
    "component_name",
    "query",
    "data",
]


class JsonColoredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, self.datefmt)

        levelname = record.levelname
        if levelname in _COLORS:
            levelname = f"{_COLORS[levelname]}{levelname}{_RESET}"

        module_color = Fore.WHITE + Style.BRIGHT
        message_color = ""
        if any(key in record.name for key in _GRAYED_LOGGERS):
            module_color = Fore.LIGHTBLACK_EX
            message_color = Fore.LIGHTBLACK_EX

        JSON_SAFE_TYPES = (
            str,
            int,
            float,
            bool,
            UUID,
            ChatStage,
            type(None),
            dict,
            # set,
            # list,
            # tuple,
        )
        extra_data = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _STANDARD_ATTRS
            and isinstance(value, JSON_SAFE_TYPES)
            and key not in _STOP_JSON_KEYS
        }

        extra_json = (
            json.dumps(extra_data, ensure_ascii=False, default=str)
            if extra_data
            else ""
        )

        return (
            f"{timestamp} | "
            f"{levelname} | "
            f"{module_color}{record.name}{_RESET} | "
            f"{message_color}{record.getMessage()}{_RESET} "
            f"{Fore.GREEN}{extra_json}{_RESET}"
        ).strip()


def setup_logging() -> None:
    level = logging.DEBUG if IS_DEBUG else logging.WARNING

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonColoredFormatter(datefmt=LOGGING_DATE_FORMAT))

    logging.basicConfig(
        level=level,
        handlers=[handler],
        force=True
    )

    muted_loggers = (
        "sqlalchemy.engine",
        "sqlalchemy.pool",
        "haystack_integrations.document_stores",
        "watchfiles",
        "httpcore.http11",
    )
    for logger_name in muted_loggers:
        muted_logger = logging.getLogger(logger_name)
        muted_logger.disabled = True
        muted_logger.propagate = False
