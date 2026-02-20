import time
import logging
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from aiobreaker import CircuitBreakerError
from redis import Redis as RedisSync
from haystack import Document
from haystack.document_stores.errors import DocumentStoreError
from sqlalchemy.exc import OperationalError

from project_settings import REDIS_URL
from services.common import get_caller_name
from logging_setup import LogContext
from services.storage.helpers.storage_decorators import with_retry
from project_settings import DEFAULT_TTL_SECONDS
import haystack_pipelines.initializator as pipes

logger = logging.getLogger(__name__)
with_retry_sync = with_retry(is_async=False)

document_store_retry = retry(
    retry=retry_if_exception_type((DocumentStoreError, OperationalError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)


@document_store_retry
def filter_documents_with_retry(filters: dict):
    """
    Execute filter documents with retry.
    """
    return pipes.DOCUMENT_STORE.filter_documents(filters)


@document_store_retry
def delete_documents_with_retry(chunk_ids_to_delete: list[str]):
    pipes.DOCUMENT_STORE.delete_documents(chunk_ids_to_delete)


@document_store_retry
def search_documents_with_retry(data: dict) -> dict | None:
    logging_context = LogContext(
        callee_name=get_caller_name(2),
        caller_name=get_caller_name(3),
    ).model_dump()

    try:
        return pipes.CHAT_SEARCH_PIPELINE.run(data)
    except CircuitBreakerError as e:
        warn_msg = f"Operation failed: {e}"
        logger.warning(warn_msg, extra=logging_context)
        return None

    except Exception as e:
        err_msg = f"Operation failed: {e}"
        logger.error(err_msg, extra=logging_context)
        raise


class RedisIndexingManager:
    def __init__(self, document_id: int) -> None:
        self.document_id = document_id
        self.redis = RedisSync.from_url(REDIS_URL, decode_responses=True)
        self.ttl = DEFAULT_TTL_SECONDS

    @property
    def _progress_key(self) -> str:
        return f"indexing:{self.document_id}:progress"

    @with_retry_sync
    def set_upload_progress(self, progress: int):
        """
        Store upload progress.
        """
        key = self._progress_key
        self.redis.set(key, str(progress), ex=self.ttl)


def split_document(content: str,
                   document_id: int,
                   ) -> list[Document] | None:
    """
    Execute split document.
    """
    try:
        doc = Document(
            content=content,
            id=str(document_id),
            meta={
                "parent_doc_id": str(document_id),
            }
        )

        split_result = pipes.SPLIT_PIPELINE.run(
            {"splitter": {"documents": [doc]}})
        chunks: list[Document] = split_result["splitter"]["documents"]
        return chunks

    except Exception as e:
        logging_context = LogContext(
            callee_name=get_caller_name(2),
            caller_name=get_caller_name(3)
        ).model_dump()
        logging_context["document_id"] = document_id

        error_msg = f"Operation failed: {e}"
        logger.error(error_msg, extra=logging_context, exc_info=True)

        return None


def embed_chunks_with_progress(sync_memory: RedisIndexingManager,
                               chunks_to_index: list[Document],
                               document_id: int,
                               batch_size: int = 64,
                               ) -> bool:
    """
    Execute embed chunks with progress.

    :return: ``True`` when the condition is satisfied, otherwise ``False``.
    """
    logging_context = LogContext(
        callee_name=get_caller_name(2),
        caller_name=get_caller_name(3)
    ).model_dump()
    logging_context["document_id"] = document_id

    try:
        total_chunks = len(chunks_to_index)
        processed = 0
        last_redis_update = 0.0

        for i in range(0, total_chunks, batch_size):
            batch = chunks_to_index[i:i + batch_size]
            pipes.EMBEDDING_PIPELINE.run({"embedder": {"documents": batch}})

            processed += len(batch)
            progress = round(processed / max(total_chunks, 1) * 100, 2)
            now = time.monotonic()
            if (now - last_redis_update) >= 0.5 or processed >= total_chunks:
                sync_memory.set_upload_progress(progress)
                last_redis_update = now

        return True

    except CircuitBreakerError as e:
        warn_msg = f"Operation failed: {e}"
        logger.warning(warn_msg, extra=logging_context)
        return False

    except Exception as e:
        chunk_ids_to_delete = [str(chunk.id) for chunk in chunks_to_index]
        pipes.DOCUMENT_STORE.delete_documents(chunk_ids_to_delete)

        error_msg = f"Operation failed: {e}"
        logger.error(error_msg, extra=logging_context, exc_info=True)

        return False
