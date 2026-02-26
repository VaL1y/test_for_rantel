from pydantic import BaseModel


class MessageCreate(BaseModel):
    ticket_id: int
    text: str
    client_id: int | None = None
    operator_id: int | None = None


class MessageOut(BaseModel):
    id: int
    ticket_id: int
    text: str
    client_id: int | None
    operator_id: int | None

    class Config:
        from_attributes = True