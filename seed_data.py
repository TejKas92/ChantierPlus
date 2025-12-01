import asyncio
from backend.app.database import AsyncSessionLocal, engine, Base
from backend.app.models import Company, UserProfile, Client
import uuid

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Create Company
        company_id = uuid.uuid4()
        company = Company(id=company_id, name="BTP Express")
        session.add(company)
        
        # Create User
        user_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        user = UserProfile(id=user_id, company_id=company_id, email="tej@btp-express.com", role="OWNER")
        session.add(user)
        
        # Create Client
        client = Client(
            id=uuid.uuid4(), 
            company_id=company_id, 
            name="M. Dupont", 
            address="12 Rue de la Paix, Paris", 
            email="dupont@email.com"
        )
        session.add(client)
        
        await session.commit()
        print("Data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
