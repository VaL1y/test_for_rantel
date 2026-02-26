from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin
from app.models.enums import TicketStatus


class Ticket(Base, TimestampMixin):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )

    operator_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("operators.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[TicketStatus] = mapped_column(
        SAEnum(TicketStatus, name="ticket_status"),
        nullable=False,
        server_default=TicketStatus.new.value,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="2",
    )

    subject: Mapped[str] = mapped_column(String(300), nullable=False)

    waiting_since: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    client: Mapped["Client"] = relationship(back_populates="tickets")
    operator: Mapped[Optional["Operator"]] = relationship(back_populates="tickets")

    messages: Mapped[List["Message"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    __table_args__ = (
        CheckConstraint("priority BETWEEN 1 AND 4", name="ck_ticket_priority_range"),
        Index("ix_ticket_status", "status"),
        Index("ix_ticket_operator_status", "operator_id", "status"),
        Index("ix_ticket_waiting_since", "waiting_since"),
    )