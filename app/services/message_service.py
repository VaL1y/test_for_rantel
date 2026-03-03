from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket
from app.models.message import Message
from app.models.enums import TicketStatus
from app.services.assignment import transition_ticket, _transition_ticket


async def create_message_and_handle_ticket(
    session: AsyncSession,
    *,
    ticket_id: int,
    client_id: int | None,
    operator_id: int | None,
    text: str,
) -> Message:

    ticket = await session.get(
        Ticket,
        ticket_id,
        with_for_update=True,
    )

    if not ticket:
        raise ValueError("Ticket not found")

    message = Message(
        ticket_id=ticket_id,
        client_id=client_id,
        operator_id=operator_id,
        text=text,
    )
    session.add(message)

    # если клиент ответил — корректный переход через state machine
    if client_id and ticket.status == TicketStatus.waiting:
        await _transition_ticket(
            session,
            ticket,
            TicketStatus.new
        )

    # await session.refresh(message)
    return message