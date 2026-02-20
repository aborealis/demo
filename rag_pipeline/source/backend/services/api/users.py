from sqlmodel import Session

from models.schemas.user import UserUpdateSelf
from models.orm.user import User
from services.security import get_password_hash
from params.request_params import SessionDep

async def update_user(
    db: SessionDep,
    user_db: User,
    data_to_update: UserUpdateSelf,
) -> User:
    updated_data: dict = data_to_update.model_dump(exclude_unset=True)
    if "password" in updated_data:
        updated_data["password"] = get_password_hash(updated_data["password"])

    user_db.sqlmodel_update(updated_data)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db

