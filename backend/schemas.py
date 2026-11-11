from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID

class TicketCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=10_000)

class TicketCreated(BaseModel):
    ticket_id: UUID
    status: Literal["received"]
    subject: str