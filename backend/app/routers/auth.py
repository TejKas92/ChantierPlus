from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from .. import models, schemas, database
from ..auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    generate_token,
)
from ..email_service import send_invitation_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])


# Register a new company (creates company + owner user)
@router.post("/register", response_model=schemas.Token)
async def register(
    user_data: schemas.UserRegister, db: AsyncSession = Depends(database.get_db)
):
    """Register a new company with owner account"""
    # Check if email already exists
    result = await db.execute(
        select(models.UserProfile).where(models.UserProfile.email == user_data.email)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if company name already exists
    result = await db.execute(
        select(models.Company).where(models.Company.name == user_data.company_name)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name already exists",
        )

    # Create company
    company = models.Company(name=user_data.company_name)
    db.add(company)
    await db.flush()

    # Create owner user
    user = models.UserProfile(
        company_id=company.id,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role="OWNER",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Create user dict with company name
    user_dict = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "company_id": user.company_id,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "company_name": user_data.company_name,
    }

    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserProfileWithCompany(**user_dict),
    )


# Login
@router.post("/login", response_model=schemas.Token)
async def login(
    credentials: schemas.UserLogin, db: AsyncSession = Depends(database.get_db)
):
    """Authenticate user and return JWT token"""
    result = await db.execute(
        select(models.UserProfile).where(models.UserProfile.email == credentials.email)
    )
    user = result.scalars().first()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is not active",
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Get company info
    result_company = await db.execute(
        select(models.Company).where(models.Company.id == user.company_id)
    )
    company = result_company.scalars().first()

    # Create user dict with company name
    user_dict = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "company_id": user.company_id,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "company_name": company.name if company else "Unknown",
    }

    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserProfileWithCompany(**user_dict),
    )


# Get current user from JWT token
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(database.get_db),
):
    """Get current authenticated user from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    try:
        uuid_obj = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID"
        )

    result = await db.execute(
        select(models.UserProfile).where(models.UserProfile.id == uuid_obj)
    )
    user = result.scalars().first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


# Get current user info
@router.get("/me", response_model=schemas.UserProfile)
async def get_me(current_user: models.UserProfile = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


# Invite employee (OWNER only)
@router.post("/invite-employee")
async def invite_employee(
    invite_data: schemas.InviteEmployee,
    current_user: models.UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    """Invite a new employee to the company (OWNER only)"""
    if current_user.role != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company owners can invite employees",
        )

    # Check if email already exists
    result = await db.execute(
        select(models.UserProfile).where(
            models.UserProfile.email == invite_data.email
        )
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Generate invitation token
    token = generate_token()
    token_expires = datetime.utcnow() + timedelta(days=7)

    # Create invited user (inactive)
    user = models.UserProfile(
        company_id=current_user.company_id,
        email=invite_data.email,
        role="EMPLOYEE",
        is_active=False,
        invitation_token=token,
        token_expires_at=token_expires,
    )
    db.add(user)
    await db.commit()

    # Get company info
    result = await db.execute(
        select(models.Company).where(models.Company.id == current_user.company_id)
    )
    company = result.scalars().first()

    # Send invitation email
    await send_invitation_email(invite_data.email, token, company.name)

    return {"message": "Invitation sent successfully"}


# Activate employee account with invitation token
@router.post("/activate", response_model=schemas.Token)
async def activate_account(
    activation_data: schemas.SetPassword, db: AsyncSession = Depends(database.get_db)
):
    """Activate employee account by setting password with invitation token"""
    result = await db.execute(
        select(models.UserProfile).where(
            models.UserProfile.invitation_token == activation_data.token
        )
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invitation token",
        )

    if user.token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation token has expired",
        )

    # Set password and activate account
    user.password_hash = get_password_hash(activation_data.password)
    user.is_active = True
    user.invitation_token = None
    user.token_expires_at = None

    await db.commit()
    await db.refresh(user)

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Get company info
    result_company = await db.execute(
        select(models.Company).where(models.Company.id == user.company_id)
    )
    company = result_company.scalars().first()

    # Create user dict with company name
    user_dict = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "company_id": user.company_id,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "company_name": company.name if company else "Unknown",
    }

    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserProfileWithCompany(**user_dict),
    )


# Request password reset
@router.post("/request-password-reset")
async def request_password_reset(
    reset_data: schemas.RequestPasswordReset,
    db: AsyncSession = Depends(database.get_db),
):
    """Request a password reset email"""
    result = await db.execute(
        select(models.UserProfile).where(models.UserProfile.email == reset_data.email)
    )
    user = result.scalars().first()

    # Don't reveal if user exists or not
    if not user:
        return {"message": "If the email exists, a reset link has been sent"}

    # Generate reset token
    token = generate_token()
    token_expires = datetime.utcnow() + timedelta(hours=1)

    user.reset_token = token
    user.token_expires_at = token_expires

    await db.commit()

    # Send reset email
    await send_password_reset_email(user.email, token)

    return {"message": "If the email exists, a reset link has been sent"}


# Reset password with token
@router.post("/reset-password", response_model=schemas.Token)
async def reset_password(
    reset_data: schemas.ResetPassword, db: AsyncSession = Depends(database.get_db)
):
    """Reset password using reset token"""
    result = await db.execute(
        select(models.UserProfile).where(
            models.UserProfile.reset_token == reset_data.token
        )
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    if user.token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired",
        )

    # Set new password
    user.password_hash = get_password_hash(reset_data.password)
    user.reset_token = None
    user.token_expires_at = None

    await db.commit()
    await db.refresh(user)

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Get company info
    result_company = await db.execute(
        select(models.Company).where(models.Company.id == user.company_id)
    )
    company = result_company.scalars().first()

    # Create user dict with company name
    user_dict = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "company_id": user.company_id,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "company_name": company.name if company else "Unknown",
    }

    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserProfileWithCompany(**user_dict),
    )
