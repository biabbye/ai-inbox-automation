from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi.testclient import TestClient

import main
from authorization import require_organization_member
from database import get_session
from main import app
from models import OrganizationMember, Ticket


def test_ticket_create_requires_authentication() -> None:
    client = TestClient(app)

    response = client.post(
        f"/organizations/{uuid4()}/tickets",
        json={
            "subject": "Cannot access my account",
            "body": "I need help signing in.",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Missing or invalid authentication credentials."
    }


def test_ticket_create_persists_for_an_authorized_member(
    monkeypatch,
) -> None:
    organization_id = uuid4()
    user_id = uuid4()
    ticket_id = uuid4()

    class FakeTransaction:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

    class FakeSession:
        def begin(self) -> FakeTransaction:
            return FakeTransaction()

    session = FakeSession()

    async def override_membership() -> OrganizationMember:
        return OrganizationMember(
            id=uuid4(),
            organization_id=organization_id,
            user_id=user_id,
            role="agent",
            created_at=datetime.now(UTC),
        )

    async def override_session():
        yield session

    create_ticket_mock = AsyncMock(
        return_value=Ticket(
            id=ticket_id,
            organization_id=organization_id,
            subject="Cannot access my account",
            body="I need help signing in.",
            status="received",
            created_at=datetime.now(UTC),
        )
    )
    monkeypatch.setattr(
        main,
        "create_ticket",
        create_ticket_mock,
        raising=False,
    )

    app.dependency_overrides[require_organization_member] = (
        override_membership
    )
    app.dependency_overrides[get_session] = override_session

    try:
        client = TestClient(app)
        response = client.post(
            f"/organizations/{organization_id}/tickets",
            json={
                "subject": "Cannot access my account",
                "body": "I need help signing in.",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json() == {
        "ticket_id": str(ticket_id),
        "status": "received",
        "subject": "Cannot access my account",
    }

    create_ticket_mock.assert_awaited_once_with(
        session,
        organization_id=organization_id,
        subject="Cannot access my account",
        body="I need help signing in.",
    )