from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Organization, OrganizationMember


async def create_organization_with_owner(

    session: AsyncSession,
    *,
    owner_user_id: UUID,
    name: str,
) -> Organization:
    organization = Organization(name=name)
    session.add(organization)
    await session.flush()

    session.add(
        OrganizationMember(
            organization_id=organization.id,
            user_id=owner_user_id,
            role="owner",
        )
    )
    await session.flush()

    return organization


async def list_organizations_for_user(
    session: AsyncSession,
    *,
    user_id: UUID,
) -> list[tuple[Organization, OrganizationMember]]:
    result = await session.execute(
        select(Organization, OrganizationMember)
        .join(
            OrganizationMember,
            OrganizationMember.organization_id == Organization.id,
        )
        .where(OrganizationMember.user_id == user_id)
        .order_by(Organization.name)
    )

    return list(result.tuples())
