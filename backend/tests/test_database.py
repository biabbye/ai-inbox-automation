import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine
from models import Organization, OrganizationMember, Ticket
from tickets import create_ticket, list_tickets_for_organization
from uuid import uuid4
from memberships import get_membership
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from authorization import require_organization_member
from organizations import (
    create_organization_with_owner,
    list_organizations_for_user,
)

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

@pytest.mark.anyio
async def test_user_can_belong_to_multiple_organizations() -> None:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection)

        try:
            user_id = uuid4()
            first_organization = Organization(name="First Organization")
            second_organization = Organization(name="Second Organization")
            session.add_all([first_organization, second_organization])
            await session.flush()

            session.add_all(
                [
                    OrganizationMember(
                        organization_id=first_organization.id,
                        user_id=user_id,
                        role="owner",
                    ),
                    OrganizationMember(
                        organization_id=second_organization.id,
                        user_id=user_id,
                        role="agent",
                    ),
                ]
            )
            await session.flush()

            memberships = list(
                await session.scalars(
                    select(OrganizationMember).where(
                        OrganizationMember.user_id == user_id
                    )
                )
            )

            assert {member.organization_id for member in memberships} == {
                first_organization.id,
                second_organization.id,
            }
            assert {member.role for member in memberships} == {"owner", "agent"}
        finally:
            await session.close()

            if transaction.is_active:
                await transaction.rollback()

            await engine.dispose()

@pytest.mark.anyio
async def test_user_cannot_be_member_twice_in_same_organization() -> None:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection)

        try:
            organization = Organization(name="Test Organization")
            user_id = uuid4()
            session.add(organization)
            await session.flush()

            session.add(
                OrganizationMember(
                    organization_id=organization.id,
                    user_id=user_id,
                    role="owner",
                )
            )
            await session.flush()

            session.add(
                OrganizationMember(
                    organization_id=organization.id,
                    user_id=user_id,
                    role="agent",
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
async def test_membership_lookup_denies_access_to_another_organization() -> None:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection)

        try:
            user_id = uuid4()
            first_organization = Organization(name="First Organization")
            second_organization = Organization(name="Second Organization")
            session.add_all([first_organization, second_organization])
            await session.flush()

            session.add(
                OrganizationMember(
                    organization_id=first_organization.id,
                    user_id=user_id,
                    role="agent",
                )
            )
            await session.flush()

            allowed_membership = await get_membership(
                session,
                organization_id=first_organization.id,
                user_id=user_id,
            )
            denied_membership = await get_membership(
                session,
                organization_id=second_organization.id,
                user_id=user_id,
            )

            assert allowed_membership is not None
            assert allowed_membership.role == "agent"
            assert denied_membership is None
        finally:
            await session.close()

            if transaction.is_active:
                await transaction.rollback()

            await engine.dispose()

@pytest.mark.anyio
async def test_organization_membership_requirement_denies_cross_org_access() -> None:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection)

        try:
            user_id = uuid4()
            allowed_organization = Organization(name="Allowed Organization")
            denied_organization = Organization(name="Denied Organization")
            session.add_all([allowed_organization, denied_organization])
            await session.flush()

            session.add(
                OrganizationMember(
                    organization_id=allowed_organization.id,
                    user_id=user_id,
                    role="agent",
                )
            )
            await session.flush()

            membership = await require_organization_member(
                organization_id=allowed_organization.id,
                user_id=user_id,
                session=session,
            )

            assert membership.role == "agent"

            with pytest.raises(HTTPException) as error:
                await require_organization_member(
                    organization_id=denied_organization.id,
                    user_id=user_id,
                    session=session,
                )

            assert error.value.status_code == 403
        finally:
            await session.close()

            if transaction.is_active:
                await transaction.rollback()

            await engine.dispose()

@pytest.mark.anyio
async def test_creating_an_organization_creates_an_owner_membership() -> None:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection)

        try:
            owner_user_id = uuid4()

            organization = await create_organization_with_owner(
                session,
                owner_user_id=owner_user_id,
                name="SupportFlow Demo",
            )

            membership = await session.scalar(
                select(OrganizationMember).where(
                    OrganizationMember.organization_id == organization.id,
                    OrganizationMember.user_id == owner_user_id,
                )
            )

            assert membership is not None
            assert membership.role == "owner"
        finally:
            await session.close()

            if transaction.is_active:
                await transaction.rollback()

            await engine.dispose()

@pytest.mark.anyio
async def test_organization_list_is_scoped_to_current_user() -> None:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection)

        try:
            user_id = uuid4()
            other_user_id = uuid4()

            first_organization = Organization(name="First Organization")
            second_organization = Organization(name="Second Organization")
            hidden_organization = Organization(name="Hidden Organization")
            session.add_all(
                [first_organization, second_organization, hidden_organization]
            )
            await session.flush()

            session.add_all(
                [
                    OrganizationMember(
                        organization_id=first_organization.id,
                        user_id=user_id,
                        role="owner",
                    ),
                    OrganizationMember(
                        organization_id=second_organization.id,
                        user_id=user_id,
                        role="agent",
                    ),
                    OrganizationMember(
                        organization_id=hidden_organization.id,
                        user_id=other_user_id,
                        role="owner",
                    ),
                ]
            )
            await session.flush()

            organizations = await list_organizations_for_user(
                session,
                user_id=user_id,
            )

            assert {
                (organization.id, membership.role)
                for organization, membership in organizations
            } == {
                (first_organization.id, "owner"),
                (second_organization.id, "agent"),
            }
        finally:
            await session.close()

            if transaction.is_active:
                await transaction.rollback()

            await engine.dispose()