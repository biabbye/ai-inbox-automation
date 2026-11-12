from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi.testclient import TestClient

import main
from authorization import require_organization_member
from database import get_session
from main import app
from models import OrganizationMember, Ticket


def test_ticket_list_requires_authentication() -> None:
    client = TestClient(app)

    response = client.get(f"/organizations/{uuid4()}/tickets")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Missing or invalid authentication credentials."
    }

def test_ticket_list_returns_tickets_for_an_authorized_member(
    monkeypatch,
) -> None:
    organization_id = uuid4()
    user_id = uuid4()
    ticket_id = uuid4()
    session = object()

    ticket = Ticket(
        id=ticket_id,
        organization_id=organization_id,
        subject="Cannot access my account",
        body="I need help signing in.",
        status="received",
        created_at=datetime.now(UTC),
    )

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

    list_tickets_mock = AsyncMock(return_value=[ticket])
    monkeypatch.setattr(
        main,
        "list_tickets_for_organization",
        list_tickets_mock,
    )

    app.dependency_overrides[require_organization_member] = (
        override_membership
    )
    app.dependency_overrides[get_session] = override_session

    try:
        client = TestClient(app)
        response = client.get(
            f"/organizations/{organization_id}/tickets"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["ticket_id"] == str(ticket_id)
    assert payload[0]["subject"] == "Cannot access my account"
    assert payload[0]["status"] == "received"

    list_tickets_mock.assert_awaited_once_with(
        session,
        organization_id=organization_id,
    )