from datetime import timedelta
import pytest
from sqlmodel import Session

from models.orm.user import User
from services.security import get_password_hash, create_access_token


@pytest.fixture
def fake_user(db_tests: Session) -> User:
    """Fake user."""
    user = User(
        username="fake_user",
        name="Regular User",
        password=get_password_hash("secret"),
    )

    db_tests.add(user)
    db_tests.commit()
    db_tests.refresh(user)

    return user


@pytest.fixture
def fake_manager(db_tests: Session) -> User:
    """Fake manager."""
    user = User(
        username="fake_manager",
        name="Manager",
        password=get_password_hash("secret"),
    )

    db_tests.add(user)
    db_tests.commit()
    db_tests.refresh(user)
    return user


@pytest.fixture
def fake_unassigned_manager(db_tests: Session) -> User:
    """Fake unassigned manager."""
    user = User(
        username="fake__unnasigned_manager",
        name="Manager without organzation",
        password=get_password_hash("secret"),
    )

    db_tests.add(user)
    db_tests.commit()
    db_tests.refresh(user)
    return user


@pytest.fixture
def fake_admin(db_tests: Session) -> User:
    """Fake admin."""

    user = User(
        username="fake_admin",
        name="Admin",
        password=get_password_hash("secret"),
    )

    db_tests.add(user)
    db_tests.commit()
    db_tests.refresh(user)

    return user


def auth_headers(user: User):
    """Auth headers."""
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def hdr_user(fake_user: User) -> dict[str, str]:
    """Hdr user."""
    return auth_headers(fake_user)


@pytest.fixture
def hdr_manager(fake_manager: User) -> dict:
    """Hdr manager."""
    return auth_headers(fake_manager)


@pytest.fixture
def hdr_admin(fake_admin: User) -> dict:
    """Hdr admin."""
    return auth_headers(fake_admin)
