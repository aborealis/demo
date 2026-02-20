"""Module description."""
import pytest
from uuid import UUID
from fastapi.testclient import TestClient
from services.storage.chat_redis import get_chat_memory_celery
from tests.helpers.common import extract_redis_content


@pytest.mark.asyncio
async def test_ws_rate_limit(valid_chat_passport_id: UUID,
                             monkeypatch: pytest.MonkeyPatch,
                             client: TestClient,
                             ):
    """Test ws rate limit."""

    import services.chat_session.chat_session as chat_session
    monkeypatch.setattr(chat_session, "MAX_SEND_FREQ", 2)
    monkeypatch.setattr(chat_session, "SEND_TIME_WINDOW", 1)

    memory = get_chat_memory_celery(valid_chat_passport_id)
    memory.redis.flushdb()

    ws_url = f"/api/v1/chat/ws?chat_passport_id={valid_chat_passport_id}"

    with client.websocket_connect(ws_url) as websocket:
        websocket.send_text("msg1")
        websocket.receive_text()
        websocket.receive_text()  # Fake LLM Response 1
        websocket.send_text("msg2")
        websocket.receive_text()  # Fake LLM Response 2
        websocket.send_text("msg3")
        try:
            reply3 = websocket.receive_text()
        except Exception:
            reply3 = None

    result = extract_redis_content(memory)
    messages: list[tuple[str, int]] = result["messages"]

    assert messages is not None

    messages_as_str = " ".join([m[0] for m in messages])
    assert "msg1" in messages_as_str
    assert "msg2" in messages_as_str
    assert "msg3" not in messages_as_str

    assert reply3 is not None
    assert "Too many messages. Slow down" in reply3
