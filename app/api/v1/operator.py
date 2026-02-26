from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.operator import Operator
from app.schemas.operator import OperatorCreate, OperatorUpdate, OperatorOut

router = APIRouter(prefix="/operators", tags=["Operators"])

@router.post("/", response_model=OperatorOut, status_code=status.HTTP_201_CREATED)
async def create_operator(
    data: OperatorCreate,
    session: AsyncSession = Depends(get_db),
):
    operator = Operator(**data.model_dump())
    session.add(operator)
    await session.commit()
    await session.refresh(operator)
    return operator

@router.get("/{operator_id}", response_model=OperatorOut)
async def get_operator(
    operator_id: int,
    session: AsyncSession = Depends(get_db),
):
    operator = await session.get(Operator, operator_id)
    if not operator:
        raise HTTPException(404, "Operator not found")
    return operator

@router.get("/", response_model=list[OperatorOut])
async def list_operators(
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
):
    stmt = select(Operator).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.patch("/{operator_id}", response_model=OperatorOut)
async def update_operator(
    operator_id: int,
    data: OperatorUpdate,
    session: AsyncSession = Depends(get_db),
):
    operator = await session.get(Operator, operator_id)
    if not operator:
        raise HTTPException(404, "Operator not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(operator, key, value)

    await session.commit()
    await session.refresh(operator)
    return operator

@router.delete("/{operator_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_operator(
    operator_id: int,
    session: AsyncSession = Depends(get_db),
):
    operator = await session.get(Operator, operator_id)
    if not operator:
        raise HTTPException(404, "Operator not found")

    await session.delete(operator)
    await session.commit()

