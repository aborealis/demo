import uuid
from typing import cast

from params.request_params import SessionDep
from models.orm.chat import ChatPassport, ChatStatus
import routes.helpers.response_constants as rc


def is_valid_chat_passport(db: SessionDep, chat_passport_id: uuid.UUID) -> bool:
    existing_passport = db.get(ChatPassport, chat_passport_id)
    if not existing_passport:
        return False
    return cast(bool, existing_passport.status == ChatStatus.ACTIVE)


def check_chat_passport_or_400(db: SessionDep, chat_passport_id: uuid.UUID) -> None:
    if not is_valid_chat_passport(db, chat_passport_id):
        rc.ERR_400_INVALID_CHAT_PASSPORT_ID.raise_exception()
