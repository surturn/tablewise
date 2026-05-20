import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))
import asyncio
from app.database import AsyncSessionLocal
from app.models.property import Property
from app.models.branch import Outlet
from app.models.customer import Guest
from app.models.enums import OutletType, RoomStatus, UserRole
from app.models.rooms import Room, RoomType
from app.models.user import User
from app.utils.security import get_password_hash


async def main() -> None:
    async with AsyncSessionLocal() as db:
        property_ = Property(name="Grand Hotel Juba", address="Juba, South Sudan", timezone="Africa/Juba", currency="USD", settings={"country_code": "+211"})
        db.add(property_)
        await db.flush()

        restaurant = Outlet(property_id=property_.id, type=OutletType.restaurant, name="Grand Restaurant", location="Ground Floor", contact_number="+211900000001")
        bar = Outlet(property_id=property_.id, type=OutletType.bar, name="Nile Bar", location="Lobby", contact_number="+211900000002")
        db.add_all([restaurant, bar])

        room_types = [
            RoomType(property_id=property_.id, name="Standard", description="Comfortable room with Wi-Fi and AC", capacity=2, base_price_usd_cents=8500, amenities=["wifi", "ac"], photos=[]),
            RoomType(property_id=property_.id, name="Deluxe", description="Larger room with minibar", capacity=2, base_price_usd_cents=12500, amenities=["wifi", "ac", "minibar"], photos=[]),
            RoomType(property_id=property_.id, name="Suite", description="Premium suite for extended stays", capacity=4, base_price_usd_cents=22000, amenities=["wifi", "ac", "minibar", "lounge"], photos=[]),
        ]
        db.add_all(room_types)
        await db.flush()

        rooms = []
        for index in range(1, 11):
            room_type = room_types[0] if index <= 5 else room_types[1] if index <= 8 else room_types[2]
            rooms.append(Room(room_type_id=room_type.id, room_number=f"{100 + index}", floor=1 if index <= 5 else 2, status=RoomStatus.available))
        db.add_all(rooms)

        owner = User(email="owner@grandplatform.local", hashed_password=get_password_hash("GrandPlatform@2026"), full_name="Grand Platform Owner", phone_number="+211900000000", role=UserRole.owner, is_active=True, outlet_id=None)
        db.add(owner)
        await db.commit()
        print("Seeded GrandPlatform property, outlets, rooms, and owner account.")


if __name__ == "__main__":
    asyncio.run(main())
