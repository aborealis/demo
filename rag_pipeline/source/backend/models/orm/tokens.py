from datetime import datetime, timezone

from sqlalchemy import DateTime, text
from sqlmodel import SQLModel, Field, Column


def datetime_now() -> datetime:
    return datetime.now(timezone.utc)


class TokenStats(SQLModel, table=True):
    __tablename__ = "tokens"  # pyright: ignore[reportIncompatibleMethodOverride]
    __table_args__ = {"schema": "public"}

    id: int = Field(default=1, primary_key=True)
    tokens_spent: int = Field(default=0)
    updated_at: datetime = Field(
        default_factory=datetime_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("NOW()"),
        ),
    )
