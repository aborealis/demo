from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from params.request_params import SessionDep
from dependencies.chat_websocket import get_connection_manager, MultipleConnectionManager
from models.schemas.chat import ChatPassportGetOrCreate, InitResponsePublic
from services.storage.chat_redis import RedisChatMemoryFastAPI, get_chat_memory_fastapi
from services.chat_session.chat_session import ChatSession
from services.chat_constants import TEST_CHAT_HTML
import routes.helpers.response_constants as rc
import routes.validators.chat as validate
import services.api.chat as service

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/test/")
async def get() -> HTMLResponse:
    return HTMLResponse(TEST_CHAT_HTML)


@router.post(
    "/init/",
    summary="Initialize chat session",
    responses=rc.ERR_400_INVALID_CHAT_PASSPORT_ID.openapi,
)
async def init_chat(db: SessionDep, chat_passport_in: ChatPassportGetOrCreate) -> InitResponsePublic:
    if not chat_passport_in.id:
        user_ref = chat_passport_in.user_ref or f"anon:{uuid.uuid4()}"
        return service.create_chat_passport(db, user_ref, chat_passport_in)

    validate.check_chat_passport_or_400(db, chat_passport_in.id)

    return InitResponsePublic(
        chat_passport_id=chat_passport_in.id,
        ws_url=f"/api/v1/chat/ws?chat_passport_id={chat_passport_in.id}",
    )


@router.websocket("/ws")
async def websocket_endpoint(
    db: SessionDep,
    websocket: WebSocket,
    conn_manager: Annotated[MultipleConnectionManager, Depends(get_connection_manager)],
    chat_passport_id: uuid.UUID,
    is_test_mode: bool = False,
) -> None:
    with db:
        if not await service.is_valid_db_state(db, chat_passport_id):
            await websocket.close(code=1008)
            return

    await conn_manager.connect(websocket)
    memory: RedisChatMemoryFastAPI = await get_chat_memory_fastapi(chat_passport_id)
    session = ChatSession(
        websocket=websocket,
        memory=memory,
        chat_passport_id=chat_passport_id,
        is_test_mode=is_test_mode,
    )

    await session.on_connected()

    try:
        await session.start_accepting()
    except WebSocketDisconnect:
        pass
    finally:
        await session.on_closure()
        await conn_manager.disconnect(websocket)
