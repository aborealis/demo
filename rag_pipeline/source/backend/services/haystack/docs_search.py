import logging

from aiobreaker import CircuitBreakerError
from haystack import Document
from sqlmodel import select, func

from haystack_pipelines.initializator import SEARCH_PIPELINE
from models.schemas.document import QueryContext, QueryKeyword
from models.orm.document import DocumentDB
from params.request_params import SessionDep
from services.chat_session.helpers.common import count_tokens
from services.celery_tasks.helpers.common import run_celery_task
from services.celery_tasks.common_tasks import update_tokens
from logging_setup import LogContext
from services.common import get_caller_name

logger = logging.getLogger(__name__)


def search_document_context(db: SessionDep, query: QueryContext) -> dict:
    logging_context = LogContext(
        callee_name=get_caller_name(2),
        caller_name=get_caller_name(3),
    ).model_dump()

    try:
        pipeline_result: dict = SEARCH_PIPELINE.run(
            {
                "query_embedder": {"text": query.query},
                "retriever": {"top_k": query.top_k},
            }
        )

    except CircuitBreakerError as e:
        warn_msg = f"Operation failed: {e}"
        logger.warning(warn_msg, extra=logging_context)
        return {"total_count": query.top_k, "offset": 0, "documents": []}

    except Exception as e:
        err_msg = f"Operation failed: {e}"
        logger.warning(err_msg, extra=logging_context)
        raise

    tokens_spent = count_tokens(query.query)
    run_celery_task(update_tokens, tokens_spent=tokens_spent)

    chunks: list[Document] = pipeline_result["retriever"]["documents"]
    chunks.sort(key=lambda x: x.score if x.score else 0.0, reverse=True)

    doc_ids = list(
        {
            int(chunk.meta["parent_doc_id"])
            for chunk in chunks
            if chunk.meta.get("parent_doc_id", None)
        }
    )

    stmt = select(DocumentDB).where(DocumentDB.id.in_(doc_ids))  # type: ignore
    results = db.exec(stmt)

    documents = []
    for doc in results:
        documents.append(doc.model_dump())

    return {"total_count": query.top_k, "offset": 0, "documents": documents}


def search_documents_keyword(db: SessionDep, query: QueryKeyword):
    stmt1 = (
        select(func.count())
        .select_from(DocumentDB)
        .where(DocumentDB.content.ilike(f"%{query.query}%"))  # type:ignore
    )

    stmt2 = (
        select(DocumentDB)
        .where(DocumentDB.content.ilike(f"%{query.query}%"))  # type:ignore
        .offset(query.offset)
        .limit(query.limit)
    )

    total_count = db.exec(stmt1).one()
    results = db.exec(stmt2)

    documents = []
    for doc in results:
        documents.append(doc.model_dump())

    return {"total_count": total_count, "offset": 0, "documents": documents}
