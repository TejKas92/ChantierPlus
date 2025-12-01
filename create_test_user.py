"""
Script to create a test user for ChantierPlus
Run this after starting the backend to create a test owner account
"""
import asyncio
import sys
from backend.app.database import AsyncSessionLocal
from backend.app.models import Company, UserProfile
from backend.app.auth_utils import get_password_hash


async def create_test_user():
    async with AsyncSessionLocal() as db:
        # Create test company
        company = Company(name="Test Company")
        db.add(company)
        await db.flush()

        # Create test owner
        owner = UserProfile(
            company_id=company.id,
            email="owner@test.com",
            password_hash=get_password_hash("password123"),
            role="OWNER",
            is_active=True,
        )
        db.add(owner)

        # Create test employee
        employee = UserProfile(
            company_id=company.id,
            email="employee@test.com",
            password_hash=get_password_hash("password123"),
            role="EMPLOYEE",
            is_active=True,
        )
        db.add(employee)

        await db.commit()

        print("✅ Test users created successfully!")
        print("\nOwner account:")
        print("  Email: owner@test.com")
        print("  Password: password123")
        print("\nEmployee account:")
        print("  Email: employee@test.com")
        print("  Password: password123")


if __name__ == "__main__":
    print("Creating test users...")
    asyncio.run(create_test_user())
