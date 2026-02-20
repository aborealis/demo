from enum import Enum
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


def datetime_now() -> datetime:
    return datetime.now(timezone.utc)


class DocStatus(str, Enum):
    READY = "ready"
    QUEUED = "queued"
    FAILED = "failed"


class DocumentDB(SQLModel, table=True):
    """SQLModel entity for stored source documents."""
    __tablename__ = "documents"  # pyright: ignore[reportIncompatibleMethodOverride]
    __table_args__ = {"schema": "public"}
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime_now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime_now, nullable=False)
    updated_by: str = Field(index=True)
    content: str = ""
    status: DocStatus = Field(default=DocStatus.QUEUED)
