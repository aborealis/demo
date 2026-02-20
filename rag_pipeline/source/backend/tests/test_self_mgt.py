from fastapi.testclient import TestClient
from models.orm.user import User


class TestLogin:
    """Test suite for login."""

    def test_200(self, client: TestClient, fake_user: User):
        response = client.post(
            "/api/v1/auth/login/",
            data={"username": fake_user.username, "password": "secret"}
        )
        assert response.status_code == 200

    def test_invalid_password_401(self, client: TestClient, fake_user: User):
        response = client.post(
            "/api/v1/auth/login/",
            data={"username": fake_user.username, "password": "wrong"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid password"}

    def test_invalid_username_401(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/login/",
            data={"username": "wrong user", "password": "wrong"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid username"}


class TestMeGet:
    """Test suite for me get."""

    def test_401(self, client: TestClient):
        """Test 401."""
        response = client.get("/api/v1/me/")
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_200(self,
                 client: TestClient,
                 hdr_user: dict[str, str],
                 ):
        """Test 200."""
        response = client.get("/api/v1/me/", headers=hdr_user)
        assert response.status_code == 200
        assert response.json()["username"]


class TestMePatch:
    """Test suite for me patch."""

    def test_401(self, client: TestClient):
        """Test 401."""
        response = client.patch("/api/v1/me/", json={})
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_200(self,
                 client: TestClient,
                 hdr_user: dict[str, str],
                 ):
        """Test 200."""
        response = client.patch("/api/v1/me/", headers=hdr_user,
                                json={"name": "new"})
        assert response.status_code == 200
        assert response.json()["name"] == "new"
