from uuid import UUID
from sqlmodel import Session, select
from fastapi.testclient import TestClient
import pytest
from starlette.websockets import WebSocketDisconnect
from conftest import register_required_chat_components


class TestWebsocket:
    """Test suite for websocket."""

    def test_chat_passport_issue(self,
                                 db_tests: Session,
                                 client: TestClient):
        """Test chat passport issue."""
        register_required_chat_components(db_tests)

        response = client.post(
            "/api/v1/chat/init/",
            json={
                "source": "web",
            }
        )

        new_valid_chat_passport_id = response.json()["chat_passport_id"]

        assert type(UUID(new_valid_chat_passport_id)) is UUID

        response = client.post(
            "/api/v1/chat/init/",
            json={
                "id": new_valid_chat_passport_id,
                "source": "web",
            }
        )

        assert response.json()[
            "chat_passport_id"] == new_valid_chat_passport_id

        response = client.post("/api/v1/chat/init/",
                               json={"source": "web1"})
        assert response.status_code == 422

    def test_rejected_websocket_connection(self,
                                           client: TestClient,
                                           valid_chat_passport_id: str,
                                           ):
        """Test rejected websocket connection."""
        ws_url = "/api/v1/chat/ws?chat_passport_id=000"
        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect(ws_url) as websocket:
                websocket.send_text("STOP")

        assert exc.value.code == 1008

    def test_websocket_basic_message_flow(self,
                                          client: TestClient,
                                          valid_chat_passport_id: UUID,
                                          ):
        """Test websocket basic message flow."""
        ws_url = f"/api/v1/chat/ws?chat_passport_id={valid_chat_passport_id}"

        with client.websocket_connect(ws_url) as websocket:
            websocket.send_text("Hello")
            response1 = websocket.receive_text()
            response2 = websocket.receive_text()

        assert response1 == "Fake greeting"
        assert response2 == "Fake LLM response #1"


class TestChatFlow:
    """Test suite for chat flow."""

    def test_websocket_multiple_messages(self,
                                         client: TestClient,
                                         valid_chat_passport_id: UUID,
                                         ):
        """Test websocket multiple messages."""

        ws_url = f"/api/v1/chat/ws?chat_passport_id={valid_chat_passport_id}"

        messages = ["Hello", "How are you?", "I'm Bob",
                    "I love programming!", "Tell me a joke"]

        with client.websocket_connect(ws_url) as websocket:
            responses = []
            for msg in messages:
                websocket.send_text(msg)
                responses.append(websocket.receive_text())

        assert responses == [
            "Fake greeting",
            "Fake LLM response #1",
            "Fake LLM response #2",
            "Fake LLM response #3",
            "Fake LLM response #4",
        ]
