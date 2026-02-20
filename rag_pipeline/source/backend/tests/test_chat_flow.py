from typing import cast, TYPE_CHECKING, Any
from uuid import UUID

import pytest
from unittest.mock import AsyncMock
from sqlmodel import Session, select
from fastapi.testclient import TestClient
from services.storage.chat_redis import get_chat_memory_celery
from models.orm.chat import ChatLog, UserContext, ChatSnapshot
from tests.helpers.common import extract_redis_content

if TYPE_CHECKING:
    from services.chat_session.chat_session import ChatSession


class TestRedisIO:
    """Test suite for redis i o."""

    def test_right_redis_db(self, valid_chat_passport_id: UUID):
        """Test right redis db."""
        memory = get_chat_memory_celery(valid_chat_passport_id)
        assert memory.redis.connection_pool.connection_kwargs['db'] == 15

    def test_right_sql_db(self,
                          client: TestClient,
                          db_tests: Session,
                          valid_chat_passport_id: UUID,
                          set_env_variable: Any,
                          ):
        """Test right sql db."""
        ws_url = f"/api/v1/chat/ws?chat_passport_id={valid_chat_passport_id}"

        with client.websocket_connect(ws_url) as websocket:
            for i, msg in enumerate(["Alex", "Bob"]):
                websocket.send_text(msg)
                websocket.receive_text()
                if i == 0:
                    websocket.receive_text()

        result = db_tests.exec(
            select(ChatLog)
        ).all()

        result = [r.message for r in result]
        assert result == ['Alex', 'Fake LLM response #1',
                          'Bob', 'Fake LLM response #2']

    def test_write_first_interaction(self,
                                     valid_chat_passport_id: UUID,
                                     client: TestClient,
                                     set_env_variable: Any,
                                     ):
        """Test write first interaction."""
        memory = get_chat_memory_celery(valid_chat_passport_id)

        ws_url = f"/api/v1/chat/ws?chat_passport_id={valid_chat_passport_id}"

        memory.redis.flushdb()
        with client.websocket_connect(ws_url) as websocket:
            for i, msg in enumerate(["hello1", "hello2", "hello3"]):
                websocket.send_text(msg)
                websocket.receive_text()
                if i == 0:
                    websocket.receive_text()

        result = cast(dict, extract_redis_content(memory))

        assert len(result["messages"]) == 6
        assert result["summary"] is None

        assert result["messages"][1] == (
            '{"role": "assistant", "content": "Fake LLM response #1"}',
            2.0
        )

        memory.redis.flushdb()
        with client.websocket_connect(ws_url) as websocket:
            for msg in ["hello4", "hello5"]:
                websocket.send_text(msg)
                _ = websocket.receive_text()

        result = cast(dict, extract_redis_content(memory))

        assert len(result["messages"]) == 2
        assert result["summary"] == 'Fake summary #1'
        assert result["msg_idx"] == 10

    def test_write_continue(self,
                            valid_chat_passport_id: UUID,
                            client: TestClient,
                            set_env_variable: Any,
                            ):
        """Test write continue."""
        memory = get_chat_memory_celery(valid_chat_passport_id)

        ws_url = f"/api/v1/chat/ws?chat_passport_id={valid_chat_passport_id}"

        memory.redis.flushdb()
        with client.websocket_connect(ws_url) as websocket:
            for i, msg in enumerate(["hello1", "hello2", "hello3"]):
                websocket.send_text(msg)
                websocket.receive_text()
                if i == 0:
                    websocket.receive_text()

        memory.redis.flushdb()
        with client.websocket_connect(ws_url) as websocket:
            websocket.send_text("hello4")
            _ = websocket.receive_text()

        result = cast(dict, extract_redis_content(memory))
        assert result["messages"] == []
        assert result["summary"] == 'Fake summary #1'
        assert result["msg_idx"] == 8

        with client.websocket_connect(ws_url) as websocket:
            for msg in ["hello5", "hello6", "hello7", "hello8"]:
                websocket.send_text(msg)
                _ = websocket.receive_text()

        result = cast(dict, extract_redis_content(memory))
        assert result["messages"] == []
        assert result["summary"] == 'Fake summary #2'
        assert result["msg_idx"] == 16

        with client.websocket_connect(ws_url) as websocket:
            websocket.send_text("hello9")
            _ = websocket.receive_text()

        result = cast(dict, extract_redis_content(memory))
        assert len(result["messages"]) == 2
        assert result["summary"] == 'Fake summary #2'
        assert result["msg_idx"] == 18

        with client.websocket_connect(ws_url) as websocket:
            websocket.send_text("hello10")
            _ = websocket.receive_text()

        result = cast(dict, extract_redis_content(memory))
        assert len(result["messages"]) == 4
        assert result["summary"] == 'Fake summary #2'
        assert result["msg_idx"] == 20

    def test_write_context(self,
                           valid_chat_passport_id: UUID,
                           client: TestClient,
                           db_tests: Session,
                           set_env_variable: Any,
                           ):
        """Test write context."""
        memory = get_chat_memory_celery(valid_chat_passport_id)

        ws_url = f"/api/v1/chat/ws?chat_passport_id={valid_chat_passport_id}"

        memory.redis.flushdb()
        with client.websocket_connect(ws_url) as websocket:
            for i, msg in enumerate(["hello1", "hello2", "hello3", "hello4"]):
                websocket.send_text(msg)
                websocket.receive_text()
                if i == 0:
                    websocket.receive_text()

        result = cast(dict, extract_redis_content(memory))
        assert result["user_context"] == "Fake user context #1"

        result = db_tests.exec(
            select(UserContext)
            .where(UserContext.chat_passport_id == valid_chat_passport_id)
        ).first()

        assert result is not None
        assert result.content == "Fake user context #1"

    def test_write_summary(self,
                           valid_chat_passport_id: UUID,
                           client: TestClient,
                           db_tests: Session,
                           set_env_variable: Any,
                           ):
        """Test write summary."""
        memory = get_chat_memory_celery(valid_chat_passport_id)

        ws_url = f"/api/v1/chat/ws?chat_passport_id={valid_chat_passport_id}"

        memory.redis.flushdb()
        with client.websocket_connect(ws_url) as websocket:
            for i, msg in enumerate(["hello1", "hello2", "hello3", "hello4"]):
                websocket.send_text(msg)
                websocket.receive_text()
                if i == 0:
                    websocket.receive_text()

        result = cast(dict, extract_redis_content(memory))
        assert result["summary"] == "Fake summary #1"

        result = db_tests.get(ChatSnapshot, valid_chat_passport_id)

        assert result is not None
        assert result.rolling_summary == "Fake summary #1"


class TestLoops:
    """Test suite for loops."""

    def test_multiple_user_messages(self,
                                    valid_chat_passport_id: UUID,
                                    client: TestClient,
                                    set_env_variable: Any,
                                    ):
        """Test multiple user messages."""
        memory = get_chat_memory_celery(valid_chat_passport_id)

        ws_url = f"/api/v1/chat/ws?chat_passport_id={valid_chat_passport_id}"

        memory.redis.flushdb()
        with client.websocket_connect(ws_url) as websocket:
            for msg in ["hello1", "hello2", "hello3"]:
                websocket.send_text(msg)
            websocket.receive_text()

        result = cast(dict, extract_redis_content(memory))
        assert result["messages"][:2] == [
            ('{"role": "user", "content": "hello1"}', 1.0),
            ('{"role": "user", "content": "hello2"}', 2.0),
        ]

        result = [r for r in result["messages"]
                  if "Fake" in r[0]][0]
        reply_message, message_index = result
        assert "Fake" in reply_message
        assert message_index > 2


class TestUnits:
    @pytest.mark.asyncio
    async def test_safe_send_buffers_on_send_failure(
        self,
        chat_session_test: "ChatSession",
    ):
        """Test safe send buffers on send failure."""
        chat_passport_id = chat_session_test.chat_passport_id

        chat_session_test.websocket.send_text = AsyncMock(
            side_effect=RuntimeError("connection lost")
        )
        await chat_session_test.delivery.safe_send_text("hello")

        pending = await chat_session_test.memory.get_pending_messages(chat_passport_id)
        assert len(pending) == 1
        assert pending[0] == ('AsyncMock', 'hello')
