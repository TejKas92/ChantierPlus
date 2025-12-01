from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List
from uuid import UUID
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(prefix="/company", tags=["company"])


# Get company info
@router.get("/info", response_model=schemas.Company)
async def get_company_info(
    current_user: models.UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    """Get company information"""
    result = await db.execute(
        select(models.Company).where(models.Company.id == current_user.company_id)
    )
    company = result.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    return company


# Update company name (OWNER only)
@router.put("/update", response_model=schemas.Company)
async def update_company(
    company_data: schemas.UpdateCompany,
    current_user: models.UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    """Update company name (OWNER only)"""
    if current_user.role != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company owners can update company information",
        )

    # Check if new name already exists
    result = await db.execute(
        select(models.Company).where(
            models.Company.name == company_data.name,
            models.Company.id != current_user.company_id
        )
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name already exists",
        )

    # Update company
    result = await db.execute(
        select(models.Company).where(models.Company.id == current_user.company_id)
    )
    company = result.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    company.name = company_data.name
    await db.commit()
    await db.refresh(company)

    return company


# List all employees (OWNER only)
@router.get("/employees", response_model=List[schemas.EmployeeInfo])
async def list_employees(
    current_user: models.UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    """List all company employees (OWNER only)"""
    if current_user.role != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company owners can view employees",
        )

    result = await db.execute(
        select(models.UserProfile)
        .where(models.UserProfile.company_id == current_user.company_id)
        .order_by(models.UserProfile.created_at)
    )
    employees = result.scalars().all()

    return employees


# Update employee role (OWNER only)
@router.put("/employees/{employee_id}/role", response_model=schemas.EmployeeInfo)
async def update_employee_role(
    employee_id: UUID,
    role_data: schemas.UpdateEmployeeRole,
    current_user: models.UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    """Update employee role (OWNER only)"""
    if current_user.role != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company owners can update employee roles",
        )

    # Validate role
    if role_data.role not in ["OWNER", "EMPLOYEE"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be OWNER or EMPLOYEE",
        )

    # Get employee
    result = await db.execute(
        select(models.UserProfile).where(
            models.UserProfile.id == employee_id,
            models.UserProfile.company_id == current_user.company_id
        )
    )
    employee = result.scalars().first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    # Don't allow changing own role
    if employee.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role",
        )

    employee.role = role_data.role
    await db.commit()
    await db.refresh(employee)

    return employee


# Delete employee (OWNER only)
@router.delete("/employees/{employee_id}")
async def delete_employee(
    employee_id: UUID,
    current_user: models.UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    """Delete employee (OWNER only)"""
    if current_user.role != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company owners can delete employees",
        )

    # Get employee
    result = await db.execute(
        select(models.UserProfile).where(
            models.UserProfile.id == employee_id,
            models.UserProfile.company_id == current_user.company_id
        )
    )
    employee = result.scalars().first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    # Don't allow deleting yourself
    if employee.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete yourself",
        )

    await db.delete(employee)
    await db.commit()

    return {"message": "Employee deleted successfully"}
