from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())

    users = relationship("UserProfile", back_populates="company")
    clients = relationship("Client", back_populates="company")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=True)  # Null for invited users who haven't set password yet
    role = Column(String, default="EMPLOYEE") # OWNER, EMPLOYEE
    is_active = Column(Boolean, default=False)  # True once password is set
    invitation_token = Column(Text, nullable=True, unique=True)  # For employee invitations
    reset_token = Column(Text, nullable=True, unique=True)  # For password reset
    token_expires_at = Column(DateTime, nullable=True)  # Expiration for tokens
    created_at = Column(DateTime, default=func.now())

    company = relationship("Company", back_populates="users")

class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(Text, nullable=False)
    address = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    company = relationship("Company", back_populates="clients")
    avenants = relationship("Avenant", back_populates="client")

class Avenant(Base):
    __tablename__ = "avenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String, nullable=False) # FORFAIT, REGIE
    price = Column(Numeric, nullable=True)
    hours = Column(Numeric, nullable=True)
    hourly_rate = Column(Numeric, nullable=True)
    total_ht = Column(Numeric, nullable=False)
    photo_url = Column(Text, nullable=True)
    signature_data = Column(Text, nullable=True)
    signed_at = Column(DateTime, nullable=True)
    status = Column(String, default="DRAFT") # DRAFT, SIGNED, SENT
    created_at = Column(DateTime, default=func.now())

    client = relationship("Client", back_populates="avenants")
