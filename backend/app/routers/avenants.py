from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import models, schemas, database
from uuid import UUID, uuid4
from datetime import datetime
import shutil
import os
import base64
from pathlib import Path
from .auth import get_current_user
from ..email import send_email
from ..pdf_generator import generate_avenant_pdf

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

    # Handle signature: convert base64 to file if provided
    signature_url = None
    if avenant.signature_data:
        # Extract base64 data from data URL
        if avenant.signature_data.startswith("data:image"):
            signature_base64 = avenant.signature_data.split(",")[1]
        else:
            signature_base64 = avenant.signature_data

        # Decode and save as PNG file
        signature_bytes = base64.b64decode(signature_base64)
        unique_signature_filename = f"{uuid4()}.png"
        signature_path = f"uploads/{unique_signature_filename}"

        os.makedirs("uploads", exist_ok=True)
        with open(signature_path, "wb") as f:
            f.write(signature_bytes)

        signature_url = signature_path

    # Create avenant
    avenant_data = avenant.model_dump(exclude={"signature_data", "signature_url"})
    new_avenant = models.Avenant(
        **avenant_data,
        signature_url=signature_url,
        total_ht=total_ht,
        status="SIGNED",
        signed_at=datetime.now(),
        employee_id=current_user.id
    )

    db.add(new_avenant)
    await db.commit()
    await db.refresh(new_avenant)

    # Generate PDF
    try:
        pdf_path = generate_avenant_pdf(
            avenant_id=str(new_avenant.id),
            chantier_name=chantier.name,
            chantier_address=chantier.address,
            description=new_avenant.description,
            avenant_type=new_avenant.type,
            total_ht=float(new_avenant.total_ht),
            photo_path=new_avenant.photo_url,
            signature_path=signature_url,
            company_name=(await db.execute(select(models.Company).where(models.Company.id == chantier.company_id))).scalars().first().name,
            created_at=new_avenant.created_at.strftime("%d/%m/%Y"),
            price=float(new_avenant.price) if new_avenant.price else None,
            hours=float(new_avenant.hours) if new_avenant.hours else None,
            hourly_rate=float(new_avenant.hourly_rate) if new_avenant.hourly_rate else None
        )

        # Get all emails to send to:
        # 1. Client email (from chantier)
        # 2. Employee email (current user who created the avenant)
        # 3. All company owners emails
        recipients = [chantier.email, current_user.email]

        # Get all owners of the company
        owners_result = await db.execute(
            select(models.UserProfile).where(
                models.UserProfile.company_id == current_user.company_id,
                models.UserProfile.role == "OWNER"
            )
        )
        owners = owners_result.scalars().all()
        for owner in owners:
            if owner.email not in recipients:
                recipients.append(owner.email)

        # Read PDF file
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        # Send email to all recipients
        for recipient_email in recipients:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #f59e0b;
                        color: white;
                        padding: 20px;
                        text-align: center;
                        border-radius: 5px 5px 0 0;
                    }}
                    .content {{
                        background-color: #f9fafb;
                        padding: 30px;
                        border: 1px solid #e5e7eb;
                    }}
                    .detail-row {{
                        margin: 15px 0;
                        padding: 10px;
                        background-color: white;
                        border-radius: 5px;
                    }}
                    .label {{
                        font-weight: bold;
                        color: #6b7280;
                    }}
                    .value {{
                        color: #111827;
                        font-size: 16px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #e5e7eb;
                        color: #6b7280;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Nouvel Avenant</h1>
                </div>

                <div class="content">
                    <p>Bonjour,</p>
                    <p>Un nouvel avenant a été créé et signé pour le chantier <strong>{chantier.name}</strong>.</p>

                    <div class="detail-row">
                        <div class="label">Description :</div>
                        <div class="value">{new_avenant.description}</div>
                    </div>

                    <div class="detail-row">
                        <div class="label">Type :</div>
                        <div class="value">{new_avenant.type}</div>
                    </div>

                    <div class="detail-row">
                        <div class="label">Montant Total HT :</div>
                        <div class="value">{float(new_avenant.total_ht):.2f} €</div>
                    </div>

                    <p><strong>Le PDF de l'avenant est joint à cet email.</strong></p>
                </div>

                <div class="footer">
                    <p>Document généré par ChantierPlus</p>
                    <p>ID Avenant : {str(new_avenant.id)}</p>
                </div>
            </body>
            </html>
            """

            await send_email(
                to_email=recipient_email,
                subject=f"Avenant - {chantier.name}",
                html_content=html_content,
                attachments=[(f"avenant_{str(new_avenant.id)}.pdf", pdf_data, "application/pdf")]
            )

        # Delete temporary files (photo, signature, PDF)
        files_to_delete = []
        if new_avenant.photo_url and os.path.exists(new_avenant.photo_url):
            files_to_delete.append(new_avenant.photo_url)
        if signature_url and os.path.exists(signature_url):
            files_to_delete.append(signature_url)
        if os.path.exists(pdf_path):
            files_to_delete.append(pdf_path)

        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                print(f"[CLEANUP] Deleted temporary file: {file_path}")
            except Exception as e:
                print(f"[WARNING] Could not delete {file_path}: {e}")

    except Exception as e:
        print(f"[ERROR] Error generating/sending PDF: {e}")
        # Don't fail the avenant creation if email sending fails
        import traceback
        traceback.print_exc()

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
