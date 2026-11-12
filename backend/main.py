from uuid import uuid4, UUID
from typing import Annotated
from fastapi import FastAPI, status, Depends

from schemas import (
    OrganizationCreate,
    OrganizationCreated,
    TicketCreate,
    TicketCreated,
    TicketListItem,
    OrganizationListItem,
)
from auth import get_current_user_id
from sqlalchemy.ext.asyncio import AsyncSession

from authorization import require_organization_member
from database import get_session
from models import OrganizationMember
from tickets import create_ticket, list_tickets_for_organization
from organizations import (
    create_organization_with_owner,
    list_organizations_for_user,
)

app = FastAPI()


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/me")
async def get_current_user(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, UUID]:
    return {"user_id": user_id}

@app.post(
    "/organizations",
    status_code=status.HTTP_201_CREATED,
    response_model=OrganizationCreated,
)
async def create_organization(
    organization: OrganizationCreate,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrganizationCreated:
    async with session.begin():
        created_organization = await create_organization_with_owner(
            session,
            owner_user_id=user_id,
            name=organization.name,
        )

    return OrganizationCreated(
        organization_id=created_organization.id,
        name=created_organization.name,
        role="owner",
    )

@app.post(
    "/organizations/{organization_id}/tickets",
    status_code=status.HTTP_201_CREATED,
    response_model=TicketCreated,
)
async def create_organization_ticket(
    organization_id: UUID,
    ticket: TicketCreate,
    _member: Annotated[
        OrganizationMember,
        Depends(require_organization_member),
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TicketCreated:
    async with session.begin():
        created_ticket = await create_ticket(
            session,
            organization_id=organization_id,
            subject=ticket.subject,
            body=ticket.body,
        )

    return TicketCreated(
        ticket_id=created_ticket.id,
        status=created_ticket.status,
        subject=created_ticket.subject,
    )

@app.get(
    "/organizations/{organization_id}/tickets",
    response_model=list[TicketListItem],
)
async def get_organization_tickets(
    organization_id: UUID,
    _member: Annotated[
        OrganizationMember,
        Depends(require_organization_member),
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[TicketListItem]:
    tickets = await list_tickets_for_organization(
        session,
        organization_id=organization_id,
    )

    return [
        TicketListItem(
            ticket_id=ticket.id,
            subject=ticket.subject,
            status=ticket.status,
            created_at=ticket.created_at,
        )
        for ticket in tickets
    ]

@app.get(
    "/organizations",
    response_model=list[OrganizationListItem],
)
async def get_organizations(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[OrganizationListItem]:
    organizations = await list_organizations_for_user(
        session,
        user_id=user_id,
    )

    return [
        OrganizationListItem(
            organization_id=organization.id,
            name=organization.name,
            role=membership.role,
        )
        for organization, membership in organizations
    ]

@app.post(
    "/tickets",
    status_code=status.HTTP_201_CREATED,
    response_model=TicketCreated,
)
async def create_ticket(ticket: TicketCreate) -> TicketCreated:
    return TicketCreated(
        ticket_id=uuid4(),
        status="received",
        subject=ticket.subject,
    )