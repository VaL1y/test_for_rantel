from __future__ import annotations

from datetime import datetime
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operator import Operator
from app.models.ticket import Ticket
from app.models.enums import OperatorStatus, TicketStatus

VALID_TRANSITIONS = {
    TicketStatus.new: {TicketStatus.in_progress, TicketStatus.resolved, TicketStatus.closed},
    TicketStatus.in_progress: {TicketStatus.waiting, TicketStatus.resolved, TicketStatus.closed},
    TicketStatus.waiting: {TicketStatus.new, TicketStatus.resolved, TicketStatus.closed},
    TicketStatus.resolved: {TicketStatus.closed},
    TicketStatus.closed: set(),
}


def ensure_transition(old: TicketStatus, new: TicketStatus) -> None:
    if new not in VALID_TRANSITIONS[old]:
        raise ValueError(f"Invalid transition from {old} to {new}")


async def pick_operator_for_new_ticket(session: AsyncSession) -> Operator | None:
    """
    Выбираем свободного (online) оператора
    с минимальной нагрузкой (waiting + new).
    Строка оператора блокируется.
    """

    # Подсчёт нагрузки
    load_subq = (
        select(
            Ticket.operator_id.label("op_id"),
            func.count(Ticket.id).label("load_cnt"),
        )
        .where(
            Ticket.operator_id.is_not(None),
            Ticket.status.in_([TicketStatus.waiting, TicketStatus.new]),
        )
        .group_by(Ticket.operator_id)
        .subquery()
    )

    stmt = (
        select(Operator.id)
        .outerjoin(load_subq, load_subq.c.op_id == Operator.id)
        .where(Operator.status == OperatorStatus.online)
        .order_by(
            func.coalesce(load_subq.c.load_cnt, 0).asc(),
            Operator.id.asc(),
        )
        .limit(1)
    )

    result = await session.execute(stmt)
    operator_id = result.scalar_one_or_none()
    if not operator_id:
        return None
    operator = await session.get(
        Operator,
        operator_id,
        with_for_update=True,
    )

    # Проверка: вдруг его статус изменился
    if operator.status != OperatorStatus.online:
        return None

    return operator


async def pop_best_available_ticket_for_operator(
        session: AsyncSession,
        operator_id: int,
) -> Ticket | None:
    personal_first = case(
        (Ticket.operator_id == operator_id, 0),
        else_=1,
    )

    stmt = (
        select(Ticket)
        .where(
            Ticket.status == TicketStatus.new,
            (
                    (Ticket.operator_id == operator_id) |
                    (Ticket.operator_id.is_(None))
            )
        )
        .order_by(
            Ticket.priority.desc(),
            personal_first.asc(),
            Ticket.created_at.asc(),
            Ticket.id.asc(),
        )
        .limit(1)
        .with_for_update(skip_locked=True)
    )

    res = await session.execute(stmt)
    return res.scalar_one_or_none()


def _assign_ticket(ticket: Ticket, operator: Operator) -> None:
    ticket.operator_id = operator.id
    ticket.status = TicketStatus.in_progress
    operator.status = OperatorStatus.busy


async def create_ticket_with_assignment(
        session: AsyncSession,
        *,
        client_id: int,
        subject: str,
        priority: int,
) -> Ticket:

    ticket = Ticket(
        client_id=client_id,
        subject=subject,
        priority=priority,
        status=TicketStatus.new,
    )
    session.add(ticket)
    await session.flush()

    operator = await pick_operator_for_new_ticket(session)

    if operator:
        _assign_ticket(ticket, operator)


    return ticket


async def assign_next_for_operator(
        session: AsyncSession,
        operator: Operator,
) -> Ticket | None:
    ticket = await pop_best_available_ticket_for_operator(
        session,
        operator.id,
    )

    if not ticket:
        operator.status = OperatorStatus.online
        return None

    _assign_ticket(ticket, operator)
    return ticket


async def _transition_ticket(
    session: AsyncSession,
    ticket: Ticket,
    new_status: TicketStatus,
) -> None:

    old_status = ticket.status
    ensure_transition(old_status, new_status)

    operator = None
    if ticket.operator_id:
        operator = await session.get(
            Operator,
            ticket.operator_id,
            with_for_update=True
        )

    ticket.status = new_status

    if new_status == TicketStatus.waiting:
        ticket.waiting_since = datetime.utcnow()

    # освобождение оператора
    if (
        old_status == TicketStatus.in_progress
        and new_status in {
            TicketStatus.waiting,
            TicketStatus.resolved,
            TicketStatus.closed
        }
        and operator
    ):
        await assign_next_for_operator(session, operator)


async def transition_ticket(
    session: AsyncSession,
    ticket_id: int,
    new_status: TicketStatus,
) -> Ticket:

    ticket = await session.get(
        Ticket,
        ticket_id,
        with_for_update=True
    )

    if not ticket:
        raise ValueError("Ticket not found")

    await _transition_ticket(session, ticket, new_status)

    # await session.refresh(ticket)
    return ticket
