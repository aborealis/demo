"""Module description."""
import pytest
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from uuid import UUID
import statistics
from contextlib import ExitStack

from fastapi.testclient import TestClient
from sqlmodel import Session, select
from celery.result import allow_join_result
from sqlalchemy import text

from services.celery_tasks.chat_tasks import update_tokens
from models.orm.tokens import TokenStats
from conftest import register_required_chat_components
from services.celery_tasks.helpers.common import celery_db_task


@celery_db_task(task_name="test.update_tokens", use_chat_queue=True)
def update_tokens_with_queue(db: Session,
                             tokens_spent: int,
                             chat_passport_id: UUID,
                             ):
    """Update tokens with queue."""
    db.exec(
        text(
            """
            INSERT INTO public.tokens (id, tokens_spent)
            VALUES (1, :delta)
            ON CONFLICT (id)
            DO UPDATE SET
              tokens_spent = public.tokens.tokens_spent + EXCLUDED.tokens_spent,
              updated_at = NOW()
            """
        ).bindparams(delta=int(tokens_spent))
    )


MAX_CONNECTIONS_PER_ORG = 200
MAX_SEND_FREQ = 200


class TestConcurrentConnections:
    """Test suite for concurrent connections."""

    @pytest.mark.parametrize("connections", [100, 150, 200])
    def test_celery(self,
                    connections: int,
                    ):
        """Test celery."""

        def fire():
            return update_tokens.apply_async(kwargs={
                "tokens_spent": 70,
            })

        start = perf_counter()

        with ThreadPoolExecutor(max_workers=connections) as executor:
            futures = [executor.submit(fire) for _ in range(connections)]

        results = [f.result() for f in futures]

        with allow_join_result():
            for r in results:
                r.get(timeout=30)

        latency_sec = perf_counter() - start

        assert latency_sec < 3

    @pytest.mark.parametrize("connections", [100, 150, 200])
    def test_websocket(self,
                       db_tests: Session,
                       monkeypatch: pytest.MonkeyPatch,
                       connections: int,
                       client: TestClient,
                       ):
        """Test websocket."""
        import services.chat_session.chat_session as chat_session
        monkeypatch.setattr(chat_session, "MAX_SEND_FREQ", 200)
        monkeypatch.setattr(chat_session, "SEND_TIME_WINDOW", 1)

        register_required_chat_components(db_tests)

        chat_passports = []
        for _ in range(connections):
            response = client.post(
                "/api/v1/chat/init/",
                json={"source": "web"})
            passport = response.json()["chat_passport_id"]
            chat_passports.append(passport)

        assert len(chat_passports)

        with ExitStack() as stack:
            websockets = [
                stack.enter_context(
                    client.websocket_connect(
                        f"/api/v1/chat/ws?chat_passport_id={passport}"
                    )
                )
                for passport in chat_passports
            ]


            starts = []
            ends = []

            for ws in websockets:
                starts.append(perf_counter())
                ws.send_text("Alex")
            for ws in websockets:
                ws.receive_text()
                ws.receive_text()  # Fake LLM Reply #1
                ends.append(perf_counter())

            latencies = [end - start for end, start in zip(ends, starts)]

        median_latency = statistics.median(latencies)
        assert median_latency < 3


class TestLocks:
    """Test suite for locks."""

    def test_advisory_lock_race(self,
                                valid_chat_passport_id: UUID,
                                db_tests: Session,
                                monkeypatch: pytest.MonkeyPatch,
                                ):
        """Test advisory lock race."""

        import services.chat_session.chat_session as chat_session
        monkeypatch.setattr(chat_session, "MAX_SEND_FREQ", 200)
        monkeypatch.setattr(chat_session, "SEND_TIME_WINDOW", 1)

        connections = 100
        row = db_tests.exec(select(TokenStats)).first()
        initial_tokens = row.tokens_spent if row is not None else 0

        def fire():
            return update_tokens_with_queue.apply_async(
                kwargs=dict(
                    tokens_spent=70,
                    chat_passport_id=valid_chat_passport_id,
                )
            )

        with ThreadPoolExecutor(max_workers=connections) as executor:
            futures = [executor.submit(fire) for _ in range(connections)]

        results = [f.result() for f in futures]

        for r in results:
            with allow_join_result():
                r.get(timeout=20)

        db_tests.expire_all()
        token_stats = db_tests.exec(select(TokenStats)).first()

        expected = initial_tokens + 70 * connections
        assert token_stats is not None
        assert token_stats.tokens_spent == expected
