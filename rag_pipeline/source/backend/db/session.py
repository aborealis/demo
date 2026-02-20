"""Database engine and session dependency helpers."""
import os
from collections.abc import Generator
from sqlmodel import Session, create_engine

engine = create_engine(
    os.environ["DATABASE_URL"],
    echo=False,  # Disable SQLAlchemy SQL echo output.
    pool_pre_ping=True,  # Validate pooled DB connections before use.
)


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for FastAPI dependencies.
    
    This dependency is a sync generator. In async FastAPI endpoints, it is
    executed in the threadpool, and the session is closed in ``finally``.
    
    :yield: Active SQLModel ``Session`` instance for the current request."""
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
