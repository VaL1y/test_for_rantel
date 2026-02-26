from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import VALID_TRANSITIONS
from app.db.postgres import get_db
from app.models.ticket import Ticket
from app.models.client import Client
from app.models.enums import TicketStatus
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketOut,
    TicketStatusUpdate,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    data: TicketCreate,
    session: AsyncSession = Depends(get_db),
):
    client = await session.get(Client, data.client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    ticket = Ticket(
        client_id=data.client_id,
        subject=data.subject,
        priority=data.priority,
        status=TicketStatus.new,
    )

    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    return ticket

@router.get("/{ticket_id}", response_model=TicketOut)
async def get_ticket(
    ticket_id: int,
    session: AsyncSession = Depends(get_db),
):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    return ticket

@router.get("/", response_model=list[TicketOut])
async def list_tickets(
    status: TicketStatus | None = None,
    operator_id: int | None = None,
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
):
    stmt = select(Ticket)

    if status:
        stmt = stmt.where(Ticket.status == status)

    if operator_id:
        stmt = stmt.where(Ticket.operator_id == operator_id)

    stmt = stmt.limit(limit).offset(offset)

    result = await session.execute(stmt)
    return result.scalars().all()

@router.patch("/{ticket_id}", response_model=TicketOut)
async def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    session: AsyncSession = Depends(get_db),
):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(ticket, key, value)

    await session.commit()
    await session.refresh(ticket)
    return ticket

@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: int,
    session: AsyncSession = Depends(get_db),
):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    await session.delete(ticket)
    await session.commit()

@router.patch("/{ticket_id}/status", response_model=TicketOut)
async def change_status(
    ticket_id: int,
    data: TicketStatusUpdate,
    session: AsyncSession = Depends(get_db),
):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    if data.status not in VALID_TRANSITIONS[ticket.status]:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition from {ticket.status} to {data.status}",
        )

    ticket.status = data.status

    await session.commit()
    await session.refresh(ticket)
    return ticket

