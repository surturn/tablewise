import asyncio
import httpx
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.enums import UserRole
from sqlalchemy import select
from app.utils.jwt import create_access_token

async def main():
    # 1. Fetch an existing owner from the DB
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.role == UserRole.owner))
        user = result.scalars().first()
        
        if not user:
            # Create a mock user in the DB for testing
            user = User(email="testadmin@example.com", is_active=True, role=UserRole.owner, full_name="Admin", hashed_password="hash", phone_number="1234567890")
            db.add(user)
            await db.commit()
            await db.refresh(user)

    print(f"Using User ID: {user.id}")

    # 2. Generate an admin token for our request
    token = create_access_token(subject=user.id, role=UserRole.owner)
    
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "http://localhost:8000/api/v1"

    async with httpx.AsyncClient() as client:
        print("--- Testing Inventory Endpoint ---")
        response1 = await client.get(f"{base_url}/inventory/?limit=1000", headers=headers)
        print(f"Status Code: {response1.status_code}")
        payload1 = response1.json()
        print("Payload keys:", payload1.keys())

        if "items" not in payload1 or "total" not in payload1:
            print(f"FAILED: Missing 'items' or 'total' in Inventory payload: {payload1}")
            sys.exit(1)

        print("\n--- Testing Customers Endpoint ---")
        response2 = await client.get(f"{base_url}/customers/?limit=1000", headers=headers)
        print(f"Status Code: {response2.status_code}")
        payload2 = response2.json()
        print("Payload keys:", payload2.keys())

        if "items" not in payload2 or "total" not in payload2:
            print(f"FAILED: Missing 'items' or 'total' in Customers payload: {payload2}")
            sys.exit(1)

    print("\nSUCCESS: All payload structures verified and properly paginated!")

if __name__ == "__main__":
    asyncio.run(main())
