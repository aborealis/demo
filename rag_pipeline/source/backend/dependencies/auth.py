from typing import Annotated, cast

import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlmodel import Session

from services.security import SECRET_KEY, ALGORITHM
from models.schemas.auth import DecodedToken
from models.orm import User
from db.session import get_db
import routes.helpers.response_constants as rc


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user_from_token(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    user_id = None
    user = None
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(DecodedToken(**payload).sub)
    except (InvalidTokenError, ValidationError, TypeError):
        rc.ERR_401_INVALID_TOKEN.raise_exception()

    if user_id:
        user = db.get(User, user_id)

    if not user:
        rc.ERR_401_INVALID_TOKEN.raise_exception()

    assert user is not None
    return cast(User, user)
