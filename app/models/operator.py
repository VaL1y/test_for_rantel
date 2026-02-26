from typing import List
from sqlalchemy import String, Enum as SAEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin
from app.models.enums import OperatorStatus


class Operator(Base, TimestampMixin):
    __tablename__ = "operators"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    status: Mapped[OperatorStatus] = mapped_column(
        SAEnum(OperatorStatus, name="operator_status"),
        nullable=False,
        server_default=OperatorStatus.offline.value,
    )

    tickets: Mapped[List["Ticket"]] = relationship(
        back_populates="operator"
    )

    __table_args__ = (
        Index("ix_operator_status", "status"),
    )