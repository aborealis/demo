from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from db.session import get_db
from models.orm.user import User
from dependencies.auth import get_current_user_from_token
from dependencies.documents import validate_file_type_txt

SessionDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[User, Depends(get_current_user_from_token)]
FileTypeTxtDep = Annotated[str, Depends(validate_file_type_txt)]
FormLoginData = Annotated[OAuth2PasswordRequestForm, Depends()]

QueryOffset = Annotated[int, Query(
    ge=0,
    description="Offset for getting the next set of data",
    examples=[0],
)]
QueryLimit = Annotated[int, Query(
    le=100,
    description="Maximum number of elements in the response",
    examples=[100],
)]
