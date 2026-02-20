from sqlmodel import Field as SQLModelField
from sqlmodel import SQLModel


class BaseUser(SQLModel):
    username: str = SQLModelField(unique=True, index=True)
    name: str = SQLModelField(index=True)


class UserPublic(BaseUser):
    id: int


class UserUpdateSelf(SQLModel):
    name: str | None = None
    password: str | None = None
