from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/chantiers",
    tags=["chantiers"]
)

@router.post("/", response_model=schemas.Chantier)
async def create_chantier(
    chantier: schemas.ChantierCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.UserProfile = Depends(get_current_user)
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
    current_user: models.UserProfile = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Chantier)
        .where(models.Chantier.company_id == current_user.company_id)
        .offset(skip)
        .limit(limit)
    )
    chantiers = result.scalars().all()
    return chantiers

@router.get("/{chantier_id}/avenants", response_model=List[schemas.Avenant])
async def get_chantier_avenants(
    chantier_id: UUID,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.UserProfile = Depends(get_current_user)
):
    """Get all avenants for a specific chantier"""
    # Verify chantier exists and belongs to user's company
    result = await db.execute(
        select(models.Chantier).where(models.Chantier.id == chantier_id)
    )
    chantier = result.scalars().first()

    if not chantier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chantier not found"
        )

    if chantier.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this chantier"
        )

    # Get all avenants for this chantier
    result = await db.execute(
        select(models.Avenant)
        .where(models.Avenant.chantier_id == chantier_id)
        .order_by(models.Avenant.created_at.desc())
    )
    avenants = result.scalars().all()

    return avenants

@router.get("/{chantier_id}", response_model=schemas.Chantier)
async def get_chantier(
    chantier_id: UUID,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.UserProfile = Depends(get_current_user)
):
    """Get a specific chantier by ID"""
    result = await db.execute(
        select(models.Chantier).where(models.Chantier.id == chantier_id)
    )
    chantier = result.scalars().first()

    if not chantier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chantier not found"
        )

    # Verify chantier belongs to user's company
    if chantier.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this chantier"
        )

    return chantier
