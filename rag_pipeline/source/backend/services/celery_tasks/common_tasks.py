import logging
from typing import Any, cast

from sqlalchemy import text
from sqlmodel import Session

from models.orm.chat import ChatStage
from .helpers.common import celery_db_task

logger = logging.getLogger(__name__)


@celery_db_task(task_name="chat.update_tokens")
def update_tokens(
    db: Session,
    tokens_spent: int,
    chat_stage: ChatStage | str | None = None,
) -> None:
    stmt = text(
        """
        INSERT INTO public.tokens (id, tokens_spent)
        VALUES (1, :delta)
        ON CONFLICT (id)
        DO UPDATE SET
          tokens_spent = public.tokens.tokens_spent + EXCLUDED.tokens_spent,
          updated_at = NOW()
        """
    ).bindparams(delta=int(tokens_spent))

    db.exec(cast(Any, stmt))

    logger.info("tokens spent", extra={"in this task": tokens_spent})
