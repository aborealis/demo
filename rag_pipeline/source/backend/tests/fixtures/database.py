import pytest
from pytest import MonkeyPatch
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session

from db.session import get_db
from fixtures.common import engine_tests


@pytest.fixture
def db_tests():
    """Db tests."""

    with Session(engine_tests) as session:
        yield session
        session.rollback()
        session.close()


@pytest.fixture
def client(db_tests: Session):
    """Client."""
    from main import app
    import main

    monkeypatch = MonkeyPatch()
    monkeypatch.setattr(main, "init_database", lambda: None)

    def override_get_db():
        yield db_tests

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    monkeypatch.undo()


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Setup database."""
    SQLModel.metadata.create_all(bind=engine_tests)
    yield
    SQLModel.metadata.drop_all(bind=engine_tests)
    engine_tests.dispose()
