from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID
from datetime import datetime

class TicketCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=10_000)

class TicketCreated(BaseModel):
    ticket_id: UUID
    status: Literal["received"]
    subject: str

class TicketListItem(BaseModel):
    ticket_id: UUID
    subject: str
    status: str
    created_at: datetime

class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class OrganizationCreated(BaseModel):
    organization_id: UUID
    name: str
    role: Literal["owner"]

class OrganizationListItem(BaseModel):
    organization_id: UUID
    name: str
    role: Literal["owner", "admin", "agent", "viewer"]