import logging

from sqlmodel import Session, select

from models.orm.document import DocStatus, DocumentDB
from services.celery_tasks.common_tasks import update_tokens
from services.celery_tasks.helpers.common import run_celery_task, celery_db_task
from services.chat_session.helpers.common import count_tokens
from .helpers.indexing import (
    RedisIndexingManager,
    filter_documents_with_retry,
    delete_documents_with_retry,
    split_document,
    embed_chunks_with_progress,
)

logger = logging.getLogger(__name__)


@celery_db_task(task_name="indexing.update_document_content")
def vectorize_document_with_progress(
    db: Session,
    document_id: int,
    content: str | None,
    is_content_changed: bool,
) -> None:
    filters = {"field": "meta.parent_doc_id", "operator": "==", "value": document_id}

    existing_doc: DocumentDB = db.exec(
        select(DocumentDB).where(DocumentDB.id == document_id)
    ).one()

    sync_memory = RedisIndexingManager(document_id)

    if not is_content_changed:
        sync_memory.set_upload_progress(100)
        existing_doc.status = DocStatus.READY
        return

    if not content:
        sync_memory.set_upload_progress(100)
        existing_doc.status = DocStatus.READY
        return

    sync_memory.set_upload_progress(0)

    chunks_to_delete = filter_documents_with_retry(filters)
    chunk_ids_to_delete = [str(chunk.id) for chunk in chunks_to_delete]
    delete_documents_with_retry(chunk_ids_to_delete)

    chunks_to_index = split_document(content, document_id)
    if chunks_to_index is None:
        sync_memory.set_upload_progress(100)
        existing_doc.status = DocStatus.FAILED
        return

    if len(chunks_to_index) == 0:
        sync_memory.set_upload_progress(100)
        existing_doc.status = DocStatus.READY
        return

    is_success = embed_chunks_with_progress(sync_memory, chunks_to_index, document_id)

    if not is_success:
        sync_memory.set_upload_progress(100)
        existing_doc.status = DocStatus.FAILED
        return

    tokens_spent = count_tokens(content)
    run_celery_task(update_tokens, tokens_spent=tokens_spent)

    sync_memory.set_upload_progress(100)
    existing_doc.status = DocStatus.READY
