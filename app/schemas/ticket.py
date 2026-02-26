from pydantic import BaseModel
from typing import Optional
from app.models.enums import TicketStatus


class TicketCreate(BaseModel):
    client_id: int
    subject: str
    priority: int = 2


class TicketUpdate(BaseModel):
    subject: Optional[str] = None
    priority: Optional[int] = None


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketOut(BaseModel):
    id: int
    client_id: int
    operator_id: Optional[int]
    status: TicketStatus
    subject: str
    priority: int

    class Config:
        from_attributes = True