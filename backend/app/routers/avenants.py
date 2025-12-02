from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import models, schemas, database
from uuid import UUID, uuid4
from datetime import datetime
import shutil
import os
from pathlib import Path
from .auth import get_current_user
from ..email import send_avenant_email

router = APIRouter(
    prefix="/avenants",
    tags=["avenants"]
)

@router.get("/{avenant_id}", response_model=schemas.Avenant)
async def get_avenant(
    avenant_id: UUID,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.UserProfile = Depends(get_current_user)
):
    # Get avenant
    result = await db.execute(select(models.Avenant).where(models.Avenant.id == avenant_id))
    avenant = result.scalars().first()
    if not avenant:
        raise HTTPException(status_code=404, detail="Avenant not found")

    # Verify avenant belongs to user's company (through chantier)
    result = await db.execute(select(models.Chantier).where(models.Chantier.id == avenant.chantier_id))
    chantier = result.scalars().first()
    if not chantier or chantier.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this avenant")

    return avenant

@router.post("/", response_model=schemas.Avenant)
async def create_avenant(
    avenant: schemas.AvenantCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.UserProfile = Depends(get_current_user)
):
    # Verify chantier belongs to user's company
    result = await db.execute(select(models.Chantier).where(models.Chantier.id == avenant.chantier_id))
    chantier = result.scalars().first()
    if not chantier:
        raise HTTPException(status_code=404, detail="Chantier not found")

    if chantier.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this chantier")

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
    # Validate file type
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Type de fichier non autorisé. Types acceptés: {', '.join(ALLOWED_MIME_TYPES)}"
        )

    # Get file extension
    file_ext = Path(file.filename).suffix.lower() if file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Extension de fichier non autorisée. Extensions acceptées: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file content to check size
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier trop volumineux. Taille maximale: {MAX_FILE_SIZE // (1024*1024)} MB"
        )

    # Generate unique filename with UUID
    unique_filename = f"{uuid4()}{file_ext}"
    file_location = f"uploads/{unique_filename}"

    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    # Save file
    with open(file_location, "wb") as file_object:
        file_object.write(file_content)

    return {"photo_url": file_location}

@router.post("/{avenant_id}/send-email")
async def send_avenant_by_email(
    avenant_id: UUID,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.UserProfile = Depends(get_current_user)
):
    """
    Send an avenant by email to the chantier's contact email
    """
    # Get avenant
    result = await db.execute(select(models.Avenant).where(models.Avenant.id == avenant_id))
    avenant = result.scalars().first()
    if not avenant:
        raise HTTPException(status_code=404, detail="Avenant not found")

    # Get chantier
    result = await db.execute(select(models.Chantier).where(models.Chantier.id == avenant.chantier_id))
    chantier = result.scalars().first()
    if not chantier:
        raise HTTPException(status_code=404, detail="Chantier not found")

    # Verify authorization
    if chantier.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this avenant")

    # Get company
    result = await db.execute(select(models.Company).where(models.Company.id == chantier.company_id))
    company = result.scalars().first()

    # Send email
    try:
        await send_avenant_email(
            to_email=chantier.email,
            chantier_name=chantier.name,
            avenant_description=avenant.description,
            total_ht=float(avenant.total_ht),
            avenant_type=avenant.type,
            avenant_id=str(avenant.id),
            company_name=company.name if company else "ChantierPlus",
            photo_path=avenant.photo_url,
            signature_data=avenant.signature_data
        )
        return {"message": "Email envoyé avec succès", "email": chantier.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi de l'email: {str(e)}")
