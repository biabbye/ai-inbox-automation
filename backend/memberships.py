from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import OrganizationMember


async def get_membership(
    session: AsyncSession,
    *,
    organization_id: UUID,
    user_id: UUID,
) -> OrganizationMember | None:
    return await session.scalar(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
    )