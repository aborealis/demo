from typing import Protocol, Any
from uuid import UUID
import pytest
import pytest_asyncio
from pytest import MonkeyPatch
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from sqlmodel import Session
from haystack.dataclasses import ChatMessage

from models.orm.chat import ChatStage
from services.chat_constants import SUMMARY_PROMPT, GREETING_PROMPT
from services.storage.chat_redis import get_chat_memory_fastapi
from services.storage.helpers.async_redis_manager import RedisChatMemoryFastAPI


def register_required_chat_components(db_tests: Session):
    """Register required chat components."""
    _ = db_tests


@pytest.fixture
def valid_chat_passport_id(db_tests: Session, client: TestClient) -> str:
    """Valid chat passport id."""

    register_required_chat_components(db_tests)

    response = client.post(
        "/api/v1/chat/init/",
        json={"source": "web"})
    return response.json()["chat_passport_id"]


@pytest.fixture(autouse=True)
def fake_chat_stage(monkeypatch: MonkeyPatch):
    """Fake chat stage."""
    import services.chat_session.helpers.common as chat_session_helpers_common_module

    async def fake_read_chat_stage(*args: Any, **kwargs: Any):
        return ChatStage.TEST

    monkeypatch.setattr(
        chat_session_helpers_common_module,
        "read_chat_stage",
        fake_read_chat_stage
    )


class FakeChatMessage(ChatMessage):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._meta = {"usage": {"total_tokens": 0}}


@pytest.fixture(autouse=True)
def fake_llm_one_request_pipeline(monkeypatch: MonkeyPatch):
    """Fake llm one request pipeline."""
    import haystack_pipelines.initializator as initializator_module

    class FakeLLMPipeline:
        def __init__(self) -> None:
            self.counter_reply = 0
            self.counter_summary = 0

        def run(self, *args: Any) -> dict:
            messages: list[ChatMessage] | None = (
                args[0]
                .get("llm", {})
                .get("messages", [])
            )

            if not messages:
                return {"llm": {"replies": [FakeChatMessage.from_assistant("Fake reply to empty messages")]}}

            messages_texts: list[str] = [m.text for m in messages if m.text]

            if any(SUMMARY_PROMPT in t for t in messages_texts):
                self.counter_summary += 1
                return {"llm": {"replies": [FakeChatMessage.from_assistant(f"Fake summary #{self.counter_summary}")]} }

            elif any(GREETING_PROMPT.replace("{{ lang }}", "English") in t for t in messages_texts):
                return {"llm": {"replies": [FakeChatMessage.from_assistant("Fake greeting")]}}

            self.counter_reply += 1
            return {"llm": {"replies": [FakeChatMessage.from_assistant(f"Fake LLM response #{self.counter_reply}")]} }

    monkeypatch.setattr(
        initializator_module, "ONE_REQUEST_PIPELINE",
        FakeLLMPipeline()
    )


@pytest.fixture(autouse=True)
def fake_llm_user_context(monkeypatch: MonkeyPatch):
    """Fake llm user context."""
    import haystack_pipelines.initializator as initializator_module

    class FakeLLMPipeline:
        def __init__(self) -> None:
            self.counter_user_context = 0

        def run(self, *args: Any) -> dict:
            self.counter_user_context += 1
            return {
                "llm": {
                    "replies": [f"Fake user context #{self.counter_user_context}"],
                    "meta": [{"usage": {"total_tokens": 0}}]
                }
            }

    monkeypatch.setattr(
        initializator_module, "USER_CONTEXT_PIPELINE",
        FakeLLMPipeline()
    )


@pytest.fixture(autouse=True)
def fake_llm_langdetection_pipeline(monkeypatch: MonkeyPatch):
    """Fake llm langdetection pipeline."""
    import haystack_pipelines.initializator as pipes

    class FakeLLMPipeline:
        def __init__(self) -> None:
            self.counter_summary = 0
            self.counter_user_context = 0

        def run(self, *args: Any) -> dict:
            return {
                "llm": {
                    "replies": ["English"],
                    "meta": [{"usage": {"total_tokens": 0}}]
                }
            }

    monkeypatch.setattr(
        pipes, "LANG_DETECTION_PIPELINE",
        FakeLLMPipeline()
    )


class WebSocketLike(Protocol):
    async def send_text(self, data: str) -> None: ...
    async def close(self) -> None: ...


class ChatMemoryLike(Protocol):
    async def buffer_outgoing(
        self,
        chat_passport_id: Any,
        payload: Any,
    ) -> None: ...


@pytest_asyncio.fixture
async def fake_memory(valid_chat_passport_id: UUID):
    """Fake memory."""
    return await get_chat_memory_fastapi(valid_chat_passport_id)


@pytest.fixture
def fake_websocket():
    ws = AsyncMock()
    ws.send_text = AsyncMock()
    ws.close = AsyncMock()
    return ws


@pytest.fixture
def chat_session_test(
    fake_websocket: AsyncMock,
    fake_memory: RedisChatMemoryFastAPI,
    valid_chat_passport_id: UUID,
):
    from services.chat_session.chat_session import ChatSession
    return ChatSession(
        websocket=fake_websocket,
        memory=fake_memory,
        chat_passport_id=valid_chat_passport_id,
        is_test_mode=True,
    )
