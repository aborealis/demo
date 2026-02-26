import pytest
from pytest import MonkeyPatch

from project_settings import REDIS_URL_TEST


@pytest.fixture(autouse=True)
def set_test_redis_environment(monkeypatch: MonkeyPatch):
    """Set test redis environment."""
    import services.storage.helpers.async_redis_manager as async_redis_manager
    import services.storage.helpers.sync_redis_manager as sync_redis_manager
    import services.storage.chat_redis as chat_redis
    import services.celery_tasks.helpers.indexing as indexing_tasks
    import project_settings as proj_settings

    monkeypatch.setattr(async_redis_manager, "CHAT_WINDOW_SIZE", 8)
    monkeypatch.setattr(sync_redis_manager, "CHAT_WINDOW_SIZE", 8)

    monkeypatch.setattr(chat_redis, "REDIS_URL", REDIS_URL_TEST)
    monkeypatch.setattr(chat_redis, "CHAT_WINDOW_SIZE", 8)
    monkeypatch.setattr(indexing_tasks, "REDIS_URL", REDIS_URL_TEST)
    monkeypatch.setattr(proj_settings, "REDIS_URL", REDIS_URL_TEST)
