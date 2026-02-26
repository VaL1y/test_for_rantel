from pydantic import BaseModel, EmailStr
from typing import Optional


class ClientCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class ClientOut(BaseModel):
    id: int
    name: str
    email: Optional[str]

    class Config:
        from_attributes = True