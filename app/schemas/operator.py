from pydantic import BaseModel
from typing import Optional
from app.models.enums import OperatorStatus


class OperatorCreate(BaseModel):
    name: str
    status: OperatorStatus = OperatorStatus.offline


class OperatorUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[OperatorStatus] = None


class OperatorOut(BaseModel):
    id: int
    name: str
    status: OperatorStatus

    class Config:
        from_attributes = True