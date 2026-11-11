from uuid import uuid4

from fastapi import FastAPI, status

from schemas import TicketCreate, TicketCreated

app = FastAPI()


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

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