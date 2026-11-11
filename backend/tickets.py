from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Ticket


async def create_ticket(
    session: AsyncSession,
    *,
    organization_id: UUID,
    subject: str,
    body: str,
) -> Ticket:
    ticket = Ticket(
        organization_id=organization_id,
        subject=subject,
        body=body,
    )

    session.add(ticket)
    await session.flush()

    return ticket

async def list_tickets_for_organization(
    session: AsyncSession,
    *,
    organization_id: UUID,
) -> list[Ticket]:
    result = await session.scalars(
        select(Ticket)
        .where(Ticket.organization_id == organization_id)
        .order_by(Ticket.created_at.desc())
    )

    return list(result)