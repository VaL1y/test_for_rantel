from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate, ClientOut

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post("/", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreate,
    session: AsyncSession = Depends(get_db),
):
    client = Client(**data.model_dump())
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client

@router.get("/{client_id}", response_model=ClientOut)
async def get_client(
    client_id: int,
    session: AsyncSession = Depends(get_db),
):
    client = await session.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")
    return client

@router.get("/", response_model=list[ClientOut])
async def list_clients(
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
):
    stmt = select(Client).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.patch("/{client_id}", response_model=ClientOut)
async def update_client(
    client_id: int,
    data: ClientUpdate,
    session: AsyncSession = Depends(get_db),
):
    client = await session.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(client, key, value)

    await session.commit()
    await session.refresh(client)
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    session: AsyncSession = Depends(get_db),
):
    client = await session.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    await session.delete(client)
    await session.commit()