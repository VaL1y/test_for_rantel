from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.message import Message
from app.models.ticket import Ticket
from app.schemas.message import MessageCreate, MessageOut

router = APIRouter(prefix="/messages", tags=["Messages"])

@router.post("/", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def create_message(
    data: MessageCreate,
    session: AsyncSession = Depends(get_db),
):
    ticket = await session.get(Ticket, data.ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    if bool(data.client_id) == bool(data.operator_id):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Message must have either client_id or operator_id (but not both)",
        )

    message = Message(**data.model_dump())

    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message

@router.get("/{message_id}", response_model=MessageOut)
async def get_message(
    message_id: int,
    session: AsyncSession = Depends(get_db),
):
    message = await session.get(Message, message_id)
    if not message:
        raise HTTPException(404, "Message not found")
    return message

@router.get("/", response_model=list[MessageOut])
async def list_messages(
    ticket_id: int | None = None,
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
):
    stmt = select(Message)

    if ticket_id:
        stmt = stmt.where(Message.ticket_id == ticket_id)

    stmt = stmt.limit(limit).offset(offset)

    result = await session.execute(stmt)
    return result.scalars().all()

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    session: AsyncSession = Depends(get_db),
):
    message = await session.get(Message, message_id)
    if not message:
        raise HTTPException(404, "Message not found")

    await session.delete(message)
    await session.commit()

