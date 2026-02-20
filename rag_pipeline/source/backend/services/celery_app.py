from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger
import logging

from project_settings import REDIS_URL, REDIS_URL_BACKEND
from logging_setup import JsonColoredFormatter, LOGGING_DATE_FORMAT
from project_settings import IS_DEBUG

celery_app = Celery(
    "tasks",
    broker=REDIS_URL,  # Redis broker
    backend=REDIS_URL_BACKEND,  # Use Redis as the Celery result backend.
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(
    ["services.celery_tasks"],
    related_name="chat_tasks",
)
celery_app.autodiscover_tasks(
    ["services.celery_tasks"],
    related_name="indexing_tasks",
)
celery_app.autodiscover_tasks(
    ["services.celery_tasks"],
    related_name="common_tasks",
)


def _apply_console_structured_formatter(logger: logging.Logger) -> None:
    """
    Execute apply console structured formatter.
    """
    fmt = JsonColoredFormatter(datefmt=LOGGING_DATE_FORMAT)

    level = logging.INFO if IS_DEBUG else logging.WARNING
    logger.setLevel(level)

    for handler in logger.handlers:
        handler.setFormatter(fmt)
        handler.setLevel(level)


@after_setup_logger.connect
def _configure_celery_root_logger(logger: logging.Logger, *args: object, **kwargs: object) -> None:
    """
    Execute configure celery root logger.
    """
    _apply_console_structured_formatter(logger)


@after_setup_task_logger.connect
def _configure_celery_task_logger(logger: logging.Logger, *args: object, **kwargs: object) -> None:
    """
    Execute configure celery task logger.
    """
    _apply_console_structured_formatter(logger)

    for name in logging.root.manager.loggerDict:
        if name.startswith('services.celery_tasks'):
            child_logger = logging.getLogger(name)
            _apply_console_structured_formatter(child_logger)
