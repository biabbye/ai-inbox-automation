from uuid import uuid4

from fastapi.testclient import TestClient

from auth import get_current_user_id
from main import app


def test_me_requires_an_authorization_header() -> None:
    client = TestClient(app)

    response = client.get("/me")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Missing or invalid authentication credentials."
    }


def test_me_returns_the_verified_user_id() -> None:
    user_id = uuid4()

    async def override_current_user_id():
        return user_id

    app.dependency_overrides[get_current_user_id] = override_current_user_id

    try:
        client = TestClient(app)
        response = client.get("/me")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"user_id": str(user_id)}