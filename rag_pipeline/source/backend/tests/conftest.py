import sys
from pathlib import Path

TESTS_DIR = Path(__file__).parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

pytest_plugins = [
    "fixtures.document_store",
    "fixtures.database",
    "fixtures.redis_env",
    "fixtures.celery_and_chat_db",
    "fixtures.users",
    "fixtures.files",
    "fixtures.chat",
]


def register_required_chat_components(db_tests):
    from fixtures.chat import register_required_chat_components as _register
    return _register(db_tests)
