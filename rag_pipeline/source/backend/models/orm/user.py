from models.schemas.user import BaseUser
from sqlmodel import Field


class User(BaseUser, table=True):
    __tablename__ = "users"  # pyright: ignore[reportIncompatibleMethodOverride]
    __table_args__ = {"schema": "public"}

    id: int | None = Field(default=None, primary_key=True)
    password: str
