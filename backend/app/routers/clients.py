from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import models, schemas, database
from uuid import UUID

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)

# Dependency to get current user based on a header (MOCK)
async def get_current_user_from_header(x_user_id: str = Header(...), db: AsyncSession = Depends(database.get_db)):
    try:
        uuid_obj = UUID(x_user_id)
    except ValueError:
         raise HTTPException(status_code=401, detail="Invalid user ID header")
    
    result = await db.execute(select(models.UserProfile).where(models.UserProfile.id == uuid_obj))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/", response_model=schemas.Client)
async def create_client(
    client: schemas.ClientCreate, 
    db: AsyncSession = Depends(database.get_db),
    current_user: models.UserProfile = Depends(get_current_user_from_header)
):
    new_client = models.Client(**client.model_dump(), company_id=current_user.company_id)
    db.add(new_client)
    await db.commit()
    await db.refresh(new_client)
    return new_client

@router.get("/", response_model=List[schemas.Client])
async def read_clients(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(database.get_db),
    current_user: models.UserProfile = Depends(get_current_user_from_header)
):
    result = await db.execute(
        select(models.Client)
        .where(models.Client.company_id == current_user.company_id)
        .offset(skip)
        .limit(limit)
    )
    clients = result.scalars().all()
    return clients
