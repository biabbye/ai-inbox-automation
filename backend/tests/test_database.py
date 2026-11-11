import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine
from models import Organization, Ticket
from tickets import create_ticket, list_tickets_for_organization
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_database_connection() -> None:

    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))

        assert result.scalar_one() == 1
    finally:
        await engine.dispose()


@pytest.mark.anyio
async def test_ticket_persists_for_an_organization() -> None:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection)

        try:
            organization = Organization(name="Test Organization")
            session.add(organization)
            await session.flush()

            ticket = await create_ticket(
                session,
                organization_id=organization.id,
                subject="Cannot access my account",
                body="I need help signing in.",
            )

            saved_ticket = await session.scalar(
                select(Ticket).where(Ticket.id == ticket.id)
            )

            assert saved_ticket is not None
            assert saved_ticket.organization_id == organization.id
            assert saved_ticket.subject == "Cannot access my account"
        finally:
            await session.close()
            await transaction.rollback()
            await engine.dispose()

@pytest.mark.anyio
async def test_ticket_rejects_unknown_organization() -> None:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection)

        try:
            session.add(
                Ticket(
                    organization_id=uuid4(),
                    subject="Test ticket",
                    body="This organization does not exist.",
                )
            )

            with pytest.raises(IntegrityError):
                await session.flush()
        finally:
            await session.close()

            if transaction.is_active:
                await transaction.rollback()

            await engine.dispose()

@pytest.mark.anyio
async def test_ticket_list_is_scoped_to_organization() -> None:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection)

        try:
            first_organization = Organization(name="First Organization")
            second_organization = Organization(name="Second Organization")
            session.add_all([first_organization, second_organization])
            await session.flush()

            first_ticket = await create_ticket(
                session,
                organization_id=first_organization.id,
                subject="First organization ticket",
                body="Visible only to the first organization.",
            )
            await create_ticket(
                session,
                organization_id=second_organization.id,
                subject="Second organization ticket",
                body="Must not appear in the first list.",
            )

            tickets = await list_tickets_for_organization(
                session,
                organization_id=first_organization.id,
            )

            assert len(tickets) == 1
            assert tickets[0].id == first_ticket.id
            assert tickets[0].organization_id == first_organization.id
        finally:
            await session.close()

            if transaction.is_active:
                await transaction.rollback()

            await engine.dispose()