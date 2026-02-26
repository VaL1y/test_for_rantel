from sqlalchemy import (
    Text,
    ForeignKey,
    Index, CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
    )

    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
    )

    operator_id: Mapped[int | None] = mapped_column(
        ForeignKey("operators.id", ondelete="SET NULL"),
        nullable=True,
    )

    text: Mapped[str] = mapped_column(Text, nullable=False)

    ticket: Mapped["Ticket"] = relationship(back_populates="messages")

    __table_args__ = (
        CheckConstraint(
            "(client_id IS NOT NULL AND operator_id IS NULL) OR "
            "(client_id IS NULL AND operator_id IS NOT NULL)",
            name="ck_message_author_xor"
        ),
        Index("ix_message_ticket_created", "ticket_id", "created_at"),
    )