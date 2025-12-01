from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import models, schemas, database
from uuid import UUID

router = APIRouter(
    prefix="/chantiers",
    tags=["chantiers"]
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

@router.post("/", response_model=schemas.Chantier)
async def create_chantier(
    chantier: schemas.ChantierCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.UserProfile = Depends(get_current_user_from_header)
):
    new_chantier = models.Chantier(**chantier.model_dump(), company_id=current_user.company_id)
    db.add(new_chantier)
    await db.commit()
    await db.refresh(new_chantier)
    return new_chantier

@router.get("/", response_model=List[schemas.Chantier])
async def read_chantiers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.UserProfile = Depends(get_current_user_from_header)
):
    result = await db.execute(
        select(models.Chantier)
        .where(models.Chantier.company_id == current_user.company_id)
        .offset(skip)
        .limit(limit)
    )
    chantiers = result.scalars().all()
    return chantiers
