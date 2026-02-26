from contextlib import contextmanager
import pytest
from pytest import MonkeyPatch
from sqlmodel import Session

from project_settings import REDIS_URL_TEST
from fixtures.common import engine_tests


@pytest.fixture(scope="function", autouse=True)
def celery_app():
    from services.celery_app import celery_app

    celery_app.conf.update(
        broker_url=REDIS_URL_TEST,
        result_backend=REDIS_URL_TEST,
        task_always_eager=True,
        task_eager_propagates=True,
    )

    yield celery_app


@pytest.fixture(autouse=True)
def patch_celery_get_db(monkeypatch: MonkeyPatch):
    """Patch celery get db."""
    import services.celery_tasks.helpers.common as celery_common

    @contextmanager
    def get_test_db():
        db = Session(engine_tests)
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(celery_common, "get_db", get_test_db)


@pytest.fixture(autouse=True)
def patch_chat_session_get_db_async(monkeypatch: MonkeyPatch):
    """Patch chat session get db async."""
    import services.chat_session.helpers.db_loaders as db_loader_module

    @contextmanager
    def get_db_sync_tests():
        db = Session(engine_tests)
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(db_loader_module, "get_db_sync", get_db_sync_tests)
