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

class RequestPasswordReset(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    password: str

class ClientBase(BaseModel):
    name: str
    address: str
    email: EmailStr

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
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
    signature_data: Optional[str] = None

class AvenantCreate(AvenantBase):
    client_id: UUID

class Avenant(AvenantBase):
    id: UUID
    client_id: UUID
    total_ht: Decimal
    signed_at: Optional[datetime]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
