"""API endpoints for managing your account."""
from fastapi import APIRouter

from models.orm.user import User
from models.schemas.user import UserPublic, UserUpdateSelf
from params.request_params import UserDep, SessionDep
import services.api.users as service
import routes.helpers.response_constants as rc

router = APIRouter(prefix="/me", tags=["Manage Your Account"])


@router.get(
    "/",
    summary="Get information about your account",
    responses=(
        rc.ERR_401_NO_TOKEN
        + rc.ERR_401_INVALID_TOKEN
        + rc.ERR_500_INVALID_USER_FORMAT
    ).openapi,
)
async def read_users_me(_: SessionDep, current_user: UserDep) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.patch(
    "/",
    summary="Update your account data",
    responses=(
        rc.ERR_401_NO_TOKEN
        + rc.ERR_401_INVALID_TOKEN
        + rc.ERR_500_INVALID_USER_FORMAT
    ).openapi,
)
async def update_user_self(
    db: SessionDep,
    current_user: UserDep,
    user_to_update: UserUpdateSelf,
) -> UserPublic:
    updated_user: User = await service.update_user(db, current_user, user_to_update)
    return UserPublic.model_validate(updated_user)
