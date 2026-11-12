from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from uuid import uuid4

import main
from auth import get_current_user_id
from database import get_session
from models import Organization, OrganizationMember
from main import app


def test_create_organization_requires_authentication() -> None:
    client = TestClient(app)

    response = client.post(
        "/organizations",
        json={"name": "SupportFlow Demo"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Missing or invalid authentication credentials."
    }

def test_create_organization_returns_created_organization_for_authenticated_user(
    monkeypatch,
) -> None:
    user_id = uuid4()
    organization_id = uuid4()


    class FakeTransaction:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

    class FakeSession:
        def begin(self) -> FakeTransaction:
            return FakeTransaction()

    fake_session = FakeSession()

    async def override_current_user_id():
        return user_id

    async def override_session():
        yield fake_session

    create_organization_mock = AsyncMock(
        return_value=Organization(
            id=organization_id,
            name="SupportFlow Demo",
        )
    )
    monkeypatch.setattr(
        main,
        "create_organization_with_owner",
        create_organization_mock,
    )

    app.dependency_overrides[get_current_user_id] = (
        override_current_user_id
    )
    app.dependency_overrides[get_session] = override_session

    try:
        client = TestClient(app)
        response = client.post(
            "/organizations",
            json={"name": "SupportFlow Demo"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json() == {
        "organization_id": str(organization_id),
        "name": "SupportFlow Demo",
        "role": "owner",
    }

    create_organization_mock.assert_awaited_once_with(
        fake_session,
        owner_user_id=user_id,
        name="SupportFlow Demo",
    )

def test_organization_list_requires_authentication() -> None:
    client = TestClient(app)

    response = client.get("/organizations")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Missing or invalid authentication credentials."
    }


def test_organization_list_returns_organizations_for_authenticated_user(
    monkeypatch,
) -> None:
    user_id = uuid4()
    organization_id = uuid4()
    session = object()

    organization = Organization(
        id=organization_id,
        name="SupportFlow Demo",
    )
    membership = OrganizationMember(
        id=uuid4(),
        organization_id=organization_id,
        user_id=user_id,
        role="owner",
    )

    async def override_current_user_id():
        return user_id

    async def override_session():
        yield session

    list_organizations_mock = AsyncMock(
        return_value=[(organization, membership)]
    )
    monkeypatch.setattr(
        main,
        "list_organizations_for_user",
        list_organizations_mock,
        raising=False,
    )

    app.dependency_overrides[get_current_user_id] = (
        override_current_user_id
    )
    app.dependency_overrides[get_session] = override_session

    try:
        client = TestClient(app)
        response = client.get("/organizations")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [
        {
            "organization_id": str(organization_id),
            "name": "SupportFlow Demo",
            "role": "owner",
        }
    ]

    list_organizations_mock.assert_awaited_once_with(
        session,
        user_id=user_id,
    )