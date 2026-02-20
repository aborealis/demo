from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, event, JSON, Index, UniqueConstraint, text
from sqlmodel import SQLModel, Field, Column


class ChatStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Sources(str, Enum):
    WEB = "web"
    TELEGRAM = "telegram"
    EMAIL = "email"


class ChatStage(str, Enum):
    ANSWERING = "answering"
    TEST = "test"


def datetime_now() -> datetime:
    return datetime.now(timezone.utc)


def with_auto_update_timestamp(cls: type[SQLModel]) -> type[SQLModel]:
    if not hasattr(cls, "_timestamp_registered"):

        @event.listens_for(cls, "before_update")
        def update_timestamp(_: Any, __: Any, target: Any) -> None:
            target.updated_at = datetime.now(timezone.utc)

        cls._timestamp_registered = True  # pylint: disable=protected-access
    return cls


@with_auto_update_timestamp
class ChatPassport(SQLModel, table=True):
    __tablename__ = "chat_passport"  # pyright: ignore[reportIncompatibleMethodOverride]
    __table_args__ = (Index("idx_passport_user_created", "user_ref", "created_at"), {"schema": "public"})

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_ref: str | None = Field(index=True, nullable=True)
    pipeline_name: str = Field(index=True)
    pipeline_version: str = Field(max_length=50)
    language: str | None = Field(default=None, max_length=50)
    source: Sources | None = Field(default=None, max_length=32)
    status: ChatStatus = Field(default=ChatStatus.ACTIVE)
    search_queries: list[str] | None = Field(sa_column=Column(JSON), default_factory=list)
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime = Field(
        default_factory=datetime_now,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


class ChatLog(SQLModel, table=True):
    __tablename__ = "chat_log"  # pyright: ignore[reportIncompatibleMethodOverride]
    __table_args__ = (
        UniqueConstraint("chat_passport_id", "msg_idx", name="ux_chat_log_passp_msg_idx"),
        Index("idx_chat_log_passp_role", "chat_passport_id", "role"),
        {"schema": "public"},
    )

    id: int | None = Field(default=None, primary_key=True)
    chat_passport_id: UUID = Field(foreign_key="public.chat_passport.id", ondelete="CASCADE", index=True)
    stage: ChatStage = Field(default=ChatStage.ANSWERING)
    msg_idx: int = Field(index=True)
    role: str = Field(index=True)
    message: str
    created_at: datetime = Field(default_factory=datetime_now)


@with_auto_update_timestamp
class ChatSnapshot(SQLModel, table=True):
    __tablename__ = "chat_snapshot"  # pyright: ignore[reportIncompatibleMethodOverride]
    __table_args__ = (Index("idx_snapshot_updated", "updated_at"), {"schema": "public"})

    chat_passport_id: UUID = Field(
        foreign_key="public.chat_passport.id",
        ondelete="CASCADE",
        primary_key=True,
    )
    rolling_summary: str
    msg_idx_summary_cutoff: int
    chat_stage: ChatStage | None = Field(default=None)
    updated_at: datetime = Field(
        default_factory=datetime_now,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )


@with_auto_update_timestamp
class UserContext(SQLModel, table=True):
    __tablename__ = "user_context"  # pyright: ignore[reportIncompatibleMethodOverride]

    id: int | None = Field(default=None, primary_key=True)
    chat_passport_id: UUID | None = Field(
        foreign_key="public.chat_passport.id",
        default=None,
        ondelete="SET NULL",
    )
    content: str
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime = Field(
        default_factory=datetime_now,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()")),
    )
