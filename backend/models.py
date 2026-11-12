from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)

class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

class OrganizationMember(Base):
    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_organization_members_organization_id_user_id",
        ),
        CheckConstraint(
            "role IN ('owner', 'admin', 'agent', 'viewer')",
            name="ck_organization_members_role",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="received",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
