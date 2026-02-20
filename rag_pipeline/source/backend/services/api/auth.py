from datetime import timedelta
from typing import cast

from sqlalchemy.orm import Session
from sqlalchemy import select

from models.orm.user import User
from models.schemas.auth import Token
from services.security import create_access_token
from project_settings import ACCESS_TOKEN_EXPIRE_MINUTES


async def get_user(db: Session, username: str) -> User | None:
    stmt = select(User).filter_by(username=username)
    return cast(User | None, db.scalar(stmt))


async def login_and_issue_token(user: User) -> Token:
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
