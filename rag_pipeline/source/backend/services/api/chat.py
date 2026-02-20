import uuid

from params.request_params import SessionDep
from models.orm.chat import ChatPassport, ChatStatus
from services.chat_constants import MAIN_CHAT_PIPELINE_NAME, MAIN_CHAT_PIPELINE_VERSION
from models.schemas.chat import ChatPassportGetOrCreate, InitResponsePublic
import routes.validators.chat as validate


async def is_valid_db_state(db: SessionDep, chat_passport_id: uuid.UUID) -> bool:
    return validate.is_valid_chat_passport(db, chat_passport_id)


def create_chat_passport(
    db: SessionDep,
    user_ref: str,
    chat_passport_in: ChatPassportGetOrCreate,
) -> InitResponsePublic:
    passport_id = uuid.uuid4()
    passport = ChatPassport(
        id=passport_id,
        user_ref=user_ref,
        pipeline_name=MAIN_CHAT_PIPELINE_NAME,
        pipeline_version=MAIN_CHAT_PIPELINE_VERSION,
        source=chat_passport_in.source,
        status=ChatStatus.ACTIVE,
    )
    db.add(passport)
    db.commit()

    return InitResponsePublic(
        chat_passport_id=passport_id,
        ws_url=(f"/api/v1/chat/ws?chat_passport_id={passport_id}"),
    )
