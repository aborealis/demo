import logging
import os

from sqlmodel import Session, select

from db.session import engine
from models.orm.user import User
from models.orm.document import DocumentDB
from services.haystack.docs_indexing import index_doc_with_separator
import db.init_db_constants as cst

logger = logging.getLogger(__name__)


def init_default_user() -> User:
    with Session(engine) as db:
        user_exists: User | None = db.exec(
            select(User).where(User.username == cst.APP_ADMIN_USERNAME)
        ).first()
        if user_exists:
            logger.info("User %s is already registered",
                        cst.APP_ADMIN_USERNAME)
            return user_exists

        user = User(
            username=cst.APP_ADMIN_USERNAME,
            password=cst.APP_ADMIN_HASHED_PASSWORD,
            name=cst.APP_ADMIN_NAME,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("User added: %s",
                    cst.APP_ADMIN_USERNAME)
        return user


def init_seed_documents(default_user: User) -> None:
    with Session(engine) as db:
        existing_document = db.exec(select(DocumentDB.id).limit(1)).first()
        if existing_document is not None:
            logger.info("documents are already added")
            return

        seed_path = os.path.join("db", "structured_dialogues.txt")
        if not os.path.exists(seed_path):
            logger.warning("No documents to load from: %s", seed_path)
            return

        with open(seed_path, "r", encoding="utf-8") as f:
            long_text = f.read()

        index_doc_with_separator(
            db=db,
            long_text=long_text,
            similarity=0.9,
            current_user=default_user,
        )
        logger.info("Documents are added")


def init_database() -> None:
    user = init_default_user()
    init_seed_documents(user)
