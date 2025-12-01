from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import models, schemas, database
from uuid import UUID
from datetime import datetime
import shutil
import os

router = APIRouter(
    prefix="/avenants",
    tags=["avenants"]
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

@router.post("/", response_model=schemas.Avenant)
async def create_avenant(
    avenant: schemas.AvenantCreate, 
    db: AsyncSession = Depends(database.get_db),
    current_user: models.UserProfile = Depends(get_current_user_from_header)
):
    # Verify client belongs to user's company
    result = await db.execute(select(models.Client).where(models.Client.id == avenant.client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if client.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this client")

    # Calculate total_ht
    total_ht = 0
    if avenant.type == 'FORFAIT':
        if avenant.price is None:
             raise HTTPException(status_code=400, detail="Price is required for FORFAIT")
        total_ht = avenant.price
    elif avenant.type == 'REGIE':
        if avenant.hours is None or avenant.hourly_rate is None:
             raise HTTPException(status_code=400, detail="Hours and Hourly Rate are required for REGIE")
        total_ht = avenant.hours * avenant.hourly_rate
    
    # Create avenant
    new_avenant = models.Avenant(
        **avenant.model_dump(), 
        total_ht=total_ht,
        status="SIGNED", # As per requirements, it's created as SIGNED
        signed_at=datetime.now()
    )
    
    db.add(new_avenant)
    await db.commit()
    await db.refresh(new_avenant)
    return new_avenant

@router.post("/files")
async def upload_file(file: UploadFile = File(...)):
    # Simulate file storage
    file_location = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    return {"photo_url": file_location}
