"""
API-эндпоинты для аутентификации и авторизации пользователей
"""
from fastapi import APIRouter

from models.orm.user import User
from models.schemas.auth import Token
import services.api.auth as service
from services.security import verify_password
from params.request_params import FormLoginData, SessionDep
import routes.helpers.response_constants as rc


router = APIRouter(prefix="/auth",
                   tags=["Authenticate Users"],)


@router.post("/login/",
             summary="Authenticate a user and return a token",
             responses=(
                 rc.ERR_401_INVALID_USERNAME
                 + rc.ERR_401_INVALID_PASSWORD
             ).openapi)
async def login_for_user(db: SessionDep,
                         form_data: FormLoginData,
                         ) -> Token:
    """Возвращает временный токен пользователя по логину и паролю из формы"""
    user: User | None = await service.get_user(db, form_data.username)
    if not user:
        rc.ERR_401_INVALID_USERNAME.raise_exception()

    assert user is not None  # Pylint compliant
    if not verify_password(form_data.password, user.password):
        rc.ERR_401_INVALID_PASSWORD.raise_exception()

    return await service.login_and_issue_token(user)
