"""API endpoints for uploading and indexing documents."""
from typing import cast
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends

from params.request_params import FileTypeTxtDep, SessionDep, UserDep, QueryOffset, QueryLimit
from dependencies.auth import get_current_user_from_token
from models.schemas.document import QueryContext, QueryKeyword, DocumentContentUpdated
from .validators.file import get_text_from_txt_file_or_400
from .validators.document import validate_document_by_id_or_404
import routes.helpers.response_constants as rc
from services.haystack.docs_indexing import index_doc_with_separator
from services.haystack.docs_search import search_document_context, search_documents_keyword
from services.haystack.docs_delete import delete_document
from services.api.document import update_document_content_in_sql, fetch_docs, get_doc_status
from services.celery_tasks.helpers.common import run_celery_task
from services.celery_tasks.indexing_tasks import vectorize_document_with_progress

router = APIRouter(
    prefix="/documents",
    tags=["Manage Documents"],
    dependencies=[Depends(get_current_user_from_token)],
)


@router.patch(
    "/update/content/{document_id}/",
    summary="Update document content by ID",
    responses=(
        rc.ERR_401_NO_TOKEN
        + rc.ERR_401_INVALID_TOKEN
        + rc.OK_200_MESSAGE_INDEXING_STARTED
    ).openapi,
)
async def update_doc(
    db: SessionDep,
    _: UserDep,
    document_id: int,
    updated_doc: DocumentContentUpdated,
) -> None:
    validate_document_by_id_or_404(db, document_id)

    is_content_changed = await update_document_content_in_sql(db, document_id, updated_doc)

    run_celery_task(
        vectorize_document_with_progress,
        document_id=document_id,
        content=updated_doc.content,
        is_content_changed=is_content_changed,
    )


@router.post(
    "/upload/multiple/",
    summary="Upload a text file and index its content",
    responses=(
        rc.ERR_401_NO_TOKEN
        + rc.ERR_401_INVALID_TOKEN
        + rc.ERR_400_INVALID_FILE_TYPE
        + rc.ERR_400_INVALID_TEXTFILE_ENCODING
        + rc.OK_200_MESSAGE_INDEXING_STARTED
    ).openapi,
)
async def upload_file_mult(
    db: SessionDep,
    current_user: UserDep,
    _: FileTypeTxtDep,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    similarity: float = 0.9,
) -> dict:
    text = get_text_from_txt_file_or_400(file)

    background_tasks.add_task(index_doc_with_separator, db, text, similarity, current_user)

    return rc.OK_200_MESSAGE_INDEXING_STARTED.response


@router.get(
    "/status/{document_id}/",
    summary="Get document indexing status",
    responses=rc.ERR_404_NO_DOCUMENT_IN_ORGANIZATION.openapi,
)
async def get_embedding_status(db: SessionDep, document_id: int) -> dict:
    return await get_doc_status(db, document_id)


@router.get(
    "/",
    summary="List documents",
    responses=(
        rc.ERR_401_NO_TOKEN
        + rc.ERR_401_INVALID_TOKEN
    ).openapi,
)
async def fetch_all_docs(
    db: SessionDep,
    _: UserDep,
    offset: QueryOffset = 0,
    limit: QueryLimit = 10,
) -> list[dict] | dict:
    return await fetch_docs(db, offset=offset, limit=limit)


@router.post(
    "/search/context/",
    summary="Search documents by semantic similarity using RAG pipeline.",
    responses=(
        rc.ERR_401_NO_TOKEN
        + rc.ERR_401_INVALID_TOKEN
        + rc.OK_200_MESSAGE_DOCUMENT_DELETED
    ).openapi,
)
async def search_context(db: SessionDep, _: UserDep, query: QueryContext) -> dict:
    return search_document_context(db, query)


@router.post(
    "/search/keyword/",
    summary="Search documents by keyword.",
    responses=(
        rc.ERR_401_NO_TOKEN
        + rc.ERR_401_INVALID_TOKEN
        + rc.OK_200_MESSAGE_DOCUMENT_DELETED
    ).openapi,
)
async def search_keyword(db: SessionDep, _: UserDep, query: QueryKeyword) -> dict:
    return cast(dict, search_documents_keyword(db, query))


@router.post(
    "/delete/{doc_id}/",
    summary="Delete document by ID.",
    responses=(
        rc.ERR_401_NO_TOKEN
        + rc.ERR_401_INVALID_TOKEN
    ).openapi,
)
async def delete(db: SessionDep, _: UserDep, doc_id: int) -> dict:
    delete_document(db, doc_id)
    return rc.OK_200_MESSAGE_DOCUMENT_DELETED.response
