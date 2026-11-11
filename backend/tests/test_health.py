from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_ticket_returns_created_response() -> None:
    response = client.post(
        "/tickets",
        json={
            "subject": "Comanda mea întârzie",
            "body": "Comanda plasată săptămâna trecută nu a sosit.",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["status"] == "received"
    assert data["subject"] == "Comanda mea întârzie"
    assert "ticket_id" in data


def test_create_ticket_rejects_empty_subject() -> None:
    response = client.post(
        "/tickets",
        json={
            "subject": "",
            "body": "Am nevoie de ajutor.",
        },
    )

    assert response.status_code == 422