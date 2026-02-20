from datetime import datetime, timezone

from sqlmodel import select, func

from models.orm.document import DocumentDB, DocStatus
from models.schemas.document import DocumentContentUpdated
from params.request_params import SessionDep
from redis.asyncio import Redis as RedisAsync
import project_settings as proj_settings
import routes.helpers.response_constants as rc


async def fetch_docs(db: SessionDep,
                     offset: int = 0,
                     limit: int = 10,
                     ) -> dict:
    """
    Execute fetch docs.

    :param db: Database session.
    """

    stmt1 = select(func.count()).select_from(DocumentDB)

    stmt2 = (
        select(DocumentDB)
        .order_by(DocumentDB.updated_at.desc())  # type: ignore
        .offset(offset)
        .limit(limit)
    )

    with db:
        total_count = db.exec(stmt1).one()
        results = db.exec(stmt2).all()

        documents = []
        for doc in results:
            doc_dict = doc.model_dump()
            documents.append(doc_dict)

        documents.sort(key=lambda item: item["updated_at"], reverse=True)

        return {
            "total_count": total_count,
            "offset": offset,
            "documents": documents
        }


async def update_document_content_in_sql(db: SessionDep,
                                         document_id: int,
                                         updated_doc: DocumentContentUpdated
                                         ) -> bool:
    """
    Execute update document content in sql.

    :param db: Database session.
    :return: ``True`` when the condition is satisfied, otherwise ``False``.
    """
    existing_doc = db.get(DocumentDB, document_id)
    assert existing_doc is not None  # Pylance compliance

    is_content_changed = (
        updated_doc.content is not None
        and existing_doc.content != updated_doc.content
    )

    updated_data: dict = DocumentContentUpdated(
        name=updated_doc.name,
        content=updated_doc.content,
    ).model_dump(exclude_none=True)

    updated_data["updated_at"] = datetime.now(
        timezone.utc).replace(tzinfo=None)
    updated_data["status"] = DocStatus.QUEUED

    existing_doc.sqlmodel_update(updated_data)
    db.add(existing_doc)
    db.commit()
    db.refresh(existing_doc)

    return is_content_changed


async def get_doc_status(db: SessionDep, document_id: int) -> dict:
    """
    Get doc status.
    """
    existing_doc = db.get(DocumentDB, document_id)
    if not existing_doc:
        rc.ERR_404_NO_DOCUMENT_IN_ORGANIZATION.raise_exception()

    assert existing_doc is not None  # Pylance compliance
    # The same SQLAlchemy session may be reused across requests in tests.
    # Refresh to avoid returning stale status after Celery updated the row.
    db.refresh(existing_doc)
    if existing_doc.status == DocStatus.READY:
        return {
            "status": DocStatus.READY,
            "progress": 100
        }

    redis = await RedisAsync.from_url(proj_settings.REDIS_URL, decode_responses=True)
    progress = await redis.get(f"indexing:{document_id}:progress")
    progress = float(progress) if progress else 0
    status = DocStatus.QUEUED if progress < 100 else DocStatus.READY

    return {
        "status": status,
        "progress": progress,
    }
