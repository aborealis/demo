from sqlmodel import select

from models.orm.document import DocumentDB
from params.request_params import SessionDep
import routes.helpers.response_constants as rc


def validate_document_by_id_or_404(
    db: SessionDep,
    document_id: int,
) -> None:
    """
    Validate document by id or 404.
    
    :param db: Database session.
    """
    existing_document = db.exec(
        select(DocumentDB)
        .where(DocumentDB.id == document_id)
    ).first()

    if not existing_document:
        rc.ERR_404_NO_DOCUMENT_IN_ORGANIZATION.raise_exception()
