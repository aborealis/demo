from pydantic import BaseModel
from models.orm.chat import Sources
from uuid import UUID


class ChatPassportGetOrCreate(BaseModel):
    id: UUID | None = None
    source: Sources
    user_ref: str | None = None


class InitResponsePublic(BaseModel):
    chat_passport_id: UUID
    ws_url: str
