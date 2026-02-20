from datetime import datetime, timezone
import logging

from aiobreaker import CircuitBreakerError
from haystack import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlmodel import select

from models.orm.user import User
from models.orm.document import DocumentDB, DocStatus
from params.request_params import SessionDep
from services.chat_session.helpers.common import count_tokens
from services.celery_tasks.helpers.common import run_celery_task
from services.celery_tasks.common_tasks import update_tokens
from services.celery_tasks.helpers.indexing import filter_documents_with_retry, delete_documents_with_retry
from logging_setup import LogContext
from services.common import get_caller_name
import haystack_pipelines.initializator as pipes

logger = logging.getLogger(__name__)


def return_duplicates(
    existing_documents: list[DocumentDB],
    new_texts: list[str],
    similarity: float = 0.8,
) -> tuple[list[tuple[DocumentDB, str]], list[str]]:
    if not new_texts:
        return [], []

    if not existing_documents:
        return [], new_texts.copy()

    old_texts = [doc.content for doc in existing_documents]

    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(old_texts + new_texts)

    n_old = len(old_texts)
    old_vecs = tfidf[:n_old]  # type: ignore
    new_vecs = tfidf[n_old:]  # type: ignore

    sim_matrix = cosine_similarity(new_vecs, old_vecs)

    duplicates: list[tuple[DocumentDB, str]] = []
    unique_texts: list[str] = []

    for i, new_text in enumerate(new_texts):
        similarities = sim_matrix[i]
        best_idx: int = similarities.argmax()
        best_score: float = similarities[best_idx]

        if best_score >= similarity:
            duplicates.append((existing_documents[best_idx], new_text))
        else:
            unique_texts.append(new_text)

    return duplicates, unique_texts


def index_doc_with_separator(
    db: SessionDep,
    long_text: str,
    similarity: float,
    current_user: User,
):
    logging_context = LogContext(
        callee_name=get_caller_name(2),
        caller_name=get_caller_name(3),
    ).model_dump()

    new_texts = [
        txt.strip("\n").strip(" ")
        for txt in long_text.split("~~~~~~~~~~")
        if txt.strip("\n").strip(" ")
    ]

    existing_documents = db.exec(select(DocumentDB)).all()

    duplicates, unique_texts = return_duplicates(list(existing_documents), new_texts, similarity)

    chunk_ids_to_delete: list[str] = []
    chunks_to_reindex: list[Document] = []

    for old_document, text_to_update in duplicates:
        old_document.content = text_to_update
        db.add(old_document)
        db.commit()
        db.refresh(old_document)

        filters = {
            "field": "meta.parent_doc_id",
            "operator": "==",
            "value": old_document.id,
        }

        chunks_to_reindex += filter_documents_with_retry(filters=filters)
        chunk_ids_to_delete += [str(chunk.id) for chunk in chunks_to_reindex]

    chunks_to_index: list[Document] = []
    time_now = datetime.now(timezone.utc).isoformat()

    for i, content in enumerate(unique_texts):
        document_db = DocumentDB(
            name=f"{time_now} ({i + 1})",
            updated_by=current_user.name,
            content=content,
            status=DocStatus.READY,
        )

        db.add(document_db)
        db.commit()
        db.refresh(document_db)

        assert document_db.id is not None
        chunks_to_index.append(
            Document(
                content=content,
                id=str(document_db.id),
                meta={"parent_doc_id": str(document_db.id)},
            )
        )

    try:
        if chunks_to_reindex:
            delete_documents_with_retry(chunk_ids_to_delete)
            pipes.INDEXING_PIPELINE.run({"splitter": {"documents": chunks_to_reindex}})

            tokens_spent = sum([count_tokens(c.content) for c in chunks_to_reindex if c.content])
            run_celery_task(update_tokens, tokens_spent=tokens_spent)

        if chunks_to_index:
            pipes.INDEXING_PIPELINE.run({"splitter": {"documents": chunks_to_index}})

            tokens_spent = sum([count_tokens(c.content) for c in chunks_to_index if c.content])
            run_celery_task(update_tokens, tokens_spent=tokens_spent)

    except CircuitBreakerError as e:
        warn_msg = f"Operation failed: {e}"
        logger.warning(warn_msg, extra=logging_context)
        return

    except Exception as e:
        err_msg = f"Operation failed: {e}"
        logger.warning(err_msg, extra=logging_context)
        raise
