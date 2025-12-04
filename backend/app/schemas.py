from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class CompanyBase(BaseModel):
    name: str

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class UserProfileBase(BaseModel):
    email: EmailStr
    role: str

class UserProfileCreate(UserProfileBase):
    company_id: UUID

class UserProfile(UserProfileBase):
    id: UUID
    company_id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    company_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfileWithCompany(UserProfile):
    company_name: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserProfileWithCompany

class InviteEmployee(BaseModel):
    email: EmailStr

class SetPassword(BaseModel):
    token: str
    password: str

class UpdateCompany(BaseModel):
    name: str

class UpdateEmployeeRole(BaseModel):
    role: str

class EmployeeInfo(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class RequestPasswordReset(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    password: str

class ChantierBase(BaseModel):
    name: str
    address: str
    email: EmailStr

class ChantierCreate(ChantierBase):
    pass

class Chantier(ChantierBase):
    id: UUID
    company_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class AvenantBase(BaseModel):
    description: str
    type: str
    price: Optional[Decimal] = None
    hours: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    photo_url: Optional[str] = None
    signature_url: Optional[str] = None
    signature_data: Optional[str] = None  # For base64 signature upload

class AvenantCreate(AvenantBase):
    chantier_id: UUID

class Avenant(AvenantBase):
    id: UUID
    chantier_id: UUID
    total_ht: Decimal
    signed_at: Optional[datetime]
    status: str
    created_at: datetime
    employee_id: Optional[UUID] = None

    class Config:
        from_attributes = True
