from params.request_params import SessionDep
from models.orm.document import DocumentDB
import routes.helpers.response_constants as rc
from services.celery_tasks.helpers.indexing import filter_documents_with_retry, delete_documents_with_retry


def delete_document(db: SessionDep,
                    doc_id: int):
    """
    Delete document.
    
    :param db: Database session.
    """
    document = db.get(DocumentDB, doc_id)
    if not document:
        rc.ERR_404_NO_DOCUMENT_IN_ORGANIZATION.raise_exception()

    filters = {
        "field": "meta.parent_doc_id",
        "operator": "==",
        "value": doc_id
    }

    chunks = filter_documents_with_retry(filters=filters)
    chunk_ids_to_delete = [chunk.id for chunk in chunks]
    if chunk_ids_to_delete:
        delete_documents_with_retry(chunk_ids_to_delete)

    if document:
        db.delete(document)
        db.commit()
