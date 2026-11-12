from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user_id
from database import get_session
from memberships import get_membership
from models import OrganizationMember


async def require_organization_member(
    organization_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrganizationMember:
    membership = await get_membership(
        session,
        organization_id=organization_id,
        user_id=user_id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this organization.",
        )

    return membership