"""
TableWise Seed Script
Realistic fast-food restaurant data for a multi-branch Kenyan chain.

Place this file in your backend/ directory (same level as main.py).
Run: python seed.py
"""

import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

from app.config import settings
from app.models.branch import Branch
from app.models.user import User
from app.models.customer import Customer
from app.models.menu_category import MenuCategory
from app.models.menu_item import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.enums import UserRole, OrderStatus, PaymentStatus, PaymentMethod

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def now():
    return datetime.now(timezone.utc)

def days_ago(n):
    return datetime.now(timezone.utc) - timedelta(days=n)

def hours_ago(n):
    return datetime.now(timezone.utc) - timedelta(hours=n)


# ─────────────────────────────────────────────
# BRANCHES
# ─────────────────────────────────────────────
branch_westlands_id = uuid.uuid4()
branch_cbd_id       = uuid.uuid4()
branch_karen_id     = uuid.uuid4()

BRANCHES = [
    Branch(id=branch_westlands_id, name="TableWise Westlands",
           location="Westlands, Nairobi — Sarit Centre, Ground Floor",
           contact_number="0700123001", is_active=True,
           opening_time="08:00", closing_time="22:00",
           created_at=days_ago(90), updated_at=days_ago(90)),
    Branch(id=branch_cbd_id, name="TableWise CBD",
           location="Nairobi CBD — Kimathi Street, Electricity House",
           contact_number="0700123002", is_active=True,
           opening_time="07:30", closing_time="21:00",
           created_at=days_ago(90), updated_at=days_ago(90)),
    Branch(id=branch_karen_id, name="TableWise Karen",
           location="Karen, Nairobi — Karen Shopping Centre",
           contact_number="0700123003", is_active=True,
           opening_time="09:00", closing_time="22:30",
           created_at=days_ago(90), updated_at=days_ago(90)),
]


# ─────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────
USERS = [
    User(id=uuid.uuid4(), email="brian.kariuki@tablewise.co.ke",
         hashed_password=pwd_context.hash("TableWise@2025"),
         full_name="Brian Kariuki", phone_number="0712000001",
         role=UserRole.OWNER, is_active=True, branch_id=None,
         created_at=days_ago(90), updated_at=days_ago(90)),
    User(id=uuid.uuid4(), email="amina.odhiambo@tablewise.co.ke",
         hashed_password=pwd_context.hash("Manager@2025"),
         full_name="Amina Odhiambo", phone_number="0712000002",
         role=UserRole.BRANCH_MANAGER, is_active=True, branch_id=branch_westlands_id,
         created_at=days_ago(90), updated_at=days_ago(90)),
    User(id=uuid.uuid4(), email="kevin.mutua@tablewise.co.ke",
         hashed_password=pwd_context.hash("Cashier@2025"),
         full_name="Kevin Mutua", phone_number="0712000003",
         role=UserRole.CASHIER, is_active=True, branch_id=branch_cbd_id,
         created_at=days_ago(90), updated_at=days_ago(90)),
]


# ─────────────────────────────────────────────
# CUSTOMERS
# ─────────────────────────────────────────────
customer_grace_id  = uuid.uuid4()
customer_daniel_id = uuid.uuid4()
customer_fatuma_id = uuid.uuid4()
customer_peter_id  = uuid.uuid4()
customer_sylvia_id = uuid.uuid4()
customer_james_id  = uuid.uuid4()
customer_naomi_id  = uuid.uuid4()

CUSTOMERS = [
    Customer(id=customer_grace_id,  phone_number="254712100001", full_name="Grace Wanjiku",
             email="grace.wanjiku@gmail.com",  loyalty_points=1250,
             created_at=days_ago(60), updated_at=days_ago(3)),
    Customer(id=customer_daniel_id, phone_number="254712100002", full_name="Daniel Otieno",
             email="daniel.otieno@gmail.com",  loyalty_points=0,
             created_at=days_ago(1),  updated_at=days_ago(1)),
    Customer(id=customer_fatuma_id, phone_number="254712100003", full_name="Fatuma Hassan",
             email="fatuma.hassan@gmail.com",  loyalty_points=430,
             created_at=days_ago(30), updated_at=days_ago(2)),
    Customer(id=customer_peter_id,  phone_number="254712100004", full_name="Peter Njoroge",
             email="peter.njoroge@corporation.co.ke", loyalty_points=780,
             created_at=days_ago(45), updated_at=days_ago(1)),
    Customer(id=customer_sylvia_id, phone_number="254712100005", full_name="Sylvia Achieng",
             email="sylvia.achieng@gmail.com", loyalty_points=90,
             created_at=days_ago(20), updated_at=days_ago(2)),
    Customer(id=customer_james_id,  phone_number="254712100006", full_name="James Kamau",
             email="james.kamau@gmail.com",    loyalty_points=200,
             created_at=days_ago(15), updated_at=days_ago(5)),
    Customer(id=customer_naomi_id,  phone_number="254712100007", full_name="Naomi Chebet",
             email="naomi.chebet@gmail.com",   loyalty_points=2100,
             created_at=days_ago(90), updated_at=hours_ago(1)),
]


# ─────────────────────────────────────────────
# MENU CATEGORIES
# ─────────────────────────────────────────────
cat_burgers_id = uuid.uuid4()
cat_sides_id   = uuid.uuid4()
cat_drinks_id  = uuid.uuid4()

CATEGORIES = [
    MenuCategory(id=cat_burgers_id, name="Burgers & Wraps",
                 description="Flame-grilled burgers and stuffed wraps",
                 is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuCategory(id=cat_sides_id, name="Sides & Extras",
                 description="Fries, onion rings, and add-ons",
                 is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuCategory(id=cat_drinks_id, name="Drinks",
                 description="Fresh juices, sodas, and shakes",
                 is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
]


# ─────────────────────────────────────────────
# MENU ITEMS
# ─────────────────────────────────────────────
item_classic_id  = uuid.uuid4()
item_spicy_id    = uuid.uuid4()
item_bbq_id      = uuid.uuid4()
item_veggie_id   = uuid.uuid4()
item_fries_id    = uuid.uuid4()
item_rings_id    = uuid.uuid4()
item_coleslaw_id = uuid.uuid4()
item_mango_id    = uuid.uuid4()
item_passion_id  = uuid.uuid4()
item_soda_id     = uuid.uuid4()

MENU_ITEMS = [
    MenuItem(id=item_classic_id,  category_id=cat_burgers_id, name="Nairobi Classic Burger",
             description="Double beef patty, cheddar, caramelised onions, house sauce, brioche bun",
             price=Decimal("650.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_spicy_id,    category_id=cat_burgers_id, name="Spicy Chicken Burger",
             description="Crispy fried chicken, jalapeños, coleslaw, sriracha mayo",
             price=Decimal("580.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_bbq_id,      category_id=cat_burgers_id, name="Smoky BBQ Beef Wrap",
             description="Pulled beef, BBQ sauce, pickled red onions, rocket leaves, flour tortilla",
             price=Decimal("520.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_veggie_id,   category_id=cat_burgers_id, name="Veggie Deluxe Burger",
             description="Black bean patty, avocado, grilled peppers, garlic aioli",
             price=Decimal("490.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_fries_id,    category_id=cat_sides_id,   name="Seasoned Fries",
             description="Crispy fries tossed in our signature TableWise seasoning blend",
             price=Decimal("200.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_rings_id,    category_id=cat_sides_id,   name="Onion Rings",
             description="Beer-battered onion rings with smoky dipping sauce",
             price=Decimal("220.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_coleslaw_id, category_id=cat_sides_id,   name="Coleslaw Cup",
             description="Creamy homemade coleslaw — a Kenyan crowd favourite",
             price=Decimal("120.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_mango_id,    category_id=cat_drinks_id,  name="Fresh Mango Juice",
             description="100% Kenyan mango, blended fresh — no added sugar",
             price=Decimal("180.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_passion_id,  category_id=cat_drinks_id,  name="Passion Fruit Shake",
             description="Creamy passion fruit milkshake — thick and tangy",
             price=Decimal("220.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_soda_id,     category_id=cat_drinks_id,  name="Soft Drink (500ml)",
             description="Coca-Cola, Sprite, Fanta Orange, or Stoney Tangawizi",
             price=Decimal("100.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
]


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def make_order_items(order_id, lines, ts):
    """lines: list of (item_id, price, quantity)"""
    return [
        OrderItem(id=uuid.uuid4(), order_id=order_id, menu_item_id=item_id,
                  quantity=qty, unit_price=price, subtotal=price * qty,
                  special_instructions=None, created_at=ts, updated_at=ts)
        for item_id, price, qty in lines
    ]

def make_payment(order_id, amount, status, checkout_id, receipt, phone, ts):
    return Payment(id=uuid.uuid4(), order_id=order_id, amount=amount,
                   method=PaymentMethod.MPESA, status=status,
                   checkout_request_id=checkout_id,
                   mpesa_receipt_number=receipt,
                   payer_phone_number=phone,
                   created_at=ts, updated_at=ts)

def make_order(order_id, branch_id, customer_id, status, lines,
               is_delivery, address, notes, ts):
    total = sum(p * q for _, p, q in lines)
    return (
        Order(id=order_id, branch_id=branch_id, customer_id=customer_id,
              cashier_id=None, status=status, total_amount=total,
              is_delivery=is_delivery, delivery_address=address,
              notes=notes, created_at=ts, updated_at=ts),
        total
    )


# ─────────────────────────────────────────────
# BUILD ALL ORDERS
# ─────────────────────────────────────────────
def build_orders():
    orders, order_items, payments = [], [], []

    def add(order_id, branch_id, customer_id, status, lines,
            is_delivery, address, notes, ts,
            pay_status=None, checkout_id=None, receipt=None, phone=None):
        order, total = make_order(order_id, branch_id, customer_id,
                                  status, lines, is_delivery, address, notes, ts)
        orders.append(order)
        order_items.extend(make_order_items(order_id, lines, ts))
        if pay_status:
            payments.append(make_payment(order_id, total, pay_status,
                                         checkout_id, receipt, phone, ts))

    # ── GRACE WANJIKU: loyal repeat customer ──────────────────────────────────
    add(uuid.uuid4(), branch_westlands_id, customer_grace_id,
        OrderStatus.DELIVERED,
        [(item_classic_id, Decimal("650.00"), 1),
         (item_fries_id,   Decimal("200.00"), 1),
         (item_mango_id,   Decimal("180.00"), 1)],
        True, "Westlands, Rose Avenue, Apt 4B", None, days_ago(10),
        PaymentStatus.SUCCESS, "ws_CO_GRACE_001", "QKA7X2BN01", "254712100001")

    add(uuid.uuid4(), branch_westlands_id, customer_grace_id,
        OrderStatus.DELIVERED,
        [(item_spicy_id,   Decimal("580.00"), 1),
         (item_rings_id,   Decimal("220.00"), 1),
         (item_passion_id, Decimal("220.00"), 1)],
        False, None, "Extra napkins please", days_ago(3),
        PaymentStatus.SUCCESS, "ws_CO_GRACE_002", "QKA7X2BN02", "254712100001")

    add(uuid.uuid4(), branch_westlands_id, customer_grace_id,
        OrderStatus.PREPARING,
        [(item_classic_id, Decimal("650.00"), 2),
         (item_fries_id,   Decimal("200.00"), 2),
         (item_soda_id,    Decimal("100.00"), 2)],
        True, "Westlands, Rose Avenue, Apt 4B", None, hours_ago(1),
        PaymentStatus.SUCCESS, "ws_CO_GRACE_003", "QKA7X2BN03", "254712100001")

    # ── DANIEL OTIENO: first-time — no orders ────────────────────────────────

    # ── FATUMA HASSAN: delivery-only, currently dispatched ───────────────────
    add(uuid.uuid4(), branch_karen_id, customer_fatuma_id,
        OrderStatus.DISPATCHED,
        [(item_bbq_id,   Decimal("520.00"), 1),
         (item_fries_id, Decimal("200.00"), 1),
         (item_mango_id, Decimal("180.00"), 1)],
        True, "Karen, Langata Road, House 12", "Call when at gate", hours_ago(2),
        PaymentStatus.SUCCESS, "ws_CO_FATUMA_001", "QKA7X2BN04", "254712100003")

    # ── PETER NJOROGE: corporate lunch ───────────────────────────────────────
    add(uuid.uuid4(), branch_cbd_id, customer_peter_id,
        OrderStatus.DELIVERED,
        [(item_classic_id,  Decimal("650.00"), 3),
         (item_spicy_id,    Decimal("580.00"), 2),
         (item_veggie_id,   Decimal("490.00"), 1),
         (item_fries_id,    Decimal("200.00"), 4),
         (item_coleslaw_id, Decimal("120.00"), 3),
         (item_soda_id,     Decimal("100.00"), 5)],
        False, None, "Office lunch — 6 people. Keep orders separate by item.",
        days_ago(1),
        PaymentStatus.SUCCESS, "ws_CO_PETER_001", "QKA7X2BN05", "254712100004")

    add(uuid.uuid4(), branch_cbd_id, customer_peter_id,
        OrderStatus.PENDING_PAYMENT,
        [(item_classic_id, Decimal("650.00"), 4),
         (item_fries_id,   Decimal("200.00"), 4),
         (item_soda_id,    Decimal("100.00"), 4)],
        False, None, "Friday team lunch", hours_ago(1),
        PaymentStatus.PENDING, "ws_CO_PETER_002", None, "254712100004")

    # ── SYLVIA ACHIENG: payment failure ──────────────────────────────────────
    add(uuid.uuid4(), branch_westlands_id, customer_sylvia_id,
        OrderStatus.PAYMENT_FAILED,
        [(item_spicy_id,   Decimal("580.00"), 1),
         (item_fries_id,   Decimal("200.00"), 1),
         (item_passion_id, Decimal("220.00"), 1)],
        True, "Westlands, Parklands Road, Flat 7", None, days_ago(2),
        PaymentStatus.FAILED, "ws_CO_SYLVIA_001", None, "254712100005")

    # ── JAMES KAMAU: cancelled — no payment ──────────────────────────────────
    add(uuid.uuid4(), branch_karen_id, customer_james_id,
        OrderStatus.CANCELLED,
        [(item_veggie_id, Decimal("490.00"), 1),
         (item_rings_id,  Decimal("220.00"), 1),
         (item_mango_id,  Decimal("180.00"), 1)],
        False, None, None, days_ago(5))

    # ── NAOMI CHEBET: high-value customer ────────────────────────────────────
    add(uuid.uuid4(), branch_karen_id, customer_naomi_id,
        OrderStatus.DELIVERED,
        [(item_classic_id, Decimal("650.00"), 2),
         (item_bbq_id,     Decimal("520.00"), 1),
         (item_rings_id,   Decimal("220.00"), 2),
         (item_passion_id, Decimal("220.00"), 2)],
        True, "Karen, Hardy, Mimosa Close, House 3",
        "Please double-wrap — food allergies to raw onion", days_ago(7),
        PaymentStatus.SUCCESS, "ws_CO_NAOMI_001", "QKA7X2BN09", "254712100007")

    add(uuid.uuid4(), branch_karen_id, customer_naomi_id,
        OrderStatus.CONFIRMED,
        [(item_spicy_id,    Decimal("580.00"), 1),
         (item_classic_id,  Decimal("650.00"), 1),
         (item_fries_id,    Decimal("200.00"), 2),
         (item_coleslaw_id, Decimal("120.00"), 1),
         (item_passion_id,  Decimal("220.00"), 2)],
        True, "Karen, Hardy, Mimosa Close, House 3",
        "Ring doorbell twice", hours_ago(1),
        PaymentStatus.SUCCESS, "ws_CO_NAOMI_002", "QKA7X2BN10", "254712100007")

    return orders, order_items, payments


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            print("\n🌱 Seeding TableWise database...\n")

            print("  → Branches...")
            for obj in BRANCHES: session.add(obj)

            print("  → Users...")
            for obj in USERS: session.add(obj)

            print("  → Customers...")
            for obj in CUSTOMERS: session.add(obj)

            print("  → Menu categories...")
            for obj in CATEGORIES: session.add(obj)

            print("  → Menu items...")
            for obj in MENU_ITEMS: session.add(obj)

            print("  → Orders, order items & payments...")
            orders, order_items, payments = build_orders()
            for obj in orders:      session.add(obj)
            for obj in order_items: session.add(obj)
            for obj in payments:    session.add(obj)

    await engine.dispose()

    print("\n Done!\n")
    print("━" * 56)
    print("  BRANCHES")
    print("━" * 56)
    for b in BRANCHES:
        print(f"  • {b.name} — {b.location}")

    print("\n" + "━" * 56)
    print("  LOGIN CREDENTIALS")
    print("━" * 56)
    for name, role, email, pw in [
        ("Brian Kariuki",  "OWNER",          "brian.kariuki@tablewise.co.ke",  "TableWise@2025"),
        ("Amina Odhiambo", "BRANCH MANAGER", "amina.odhiambo@tablewise.co.ke", "Manager@2025"),
        ("Kevin Mutua",    "CASHIER",        "kevin.mutua@tablewise.co.ke",    "Cashier@2025"),
    ]:
        print(f"  • {name} ({role})\n    {email} / {pw}")

    print("\n" + "━" * 56)
    print("  CUSTOMERS")
    print("━" * 56)
    for name, profile in [
        ("Grace Wanjiku",  "Loyal repeat — 3 orders, 1 active, 1250 pts"),
        ("Daniel Otieno",  "First-timer — registered, zero orders"),
        ("Fatuma Hassan",  "Delivery-only — order currently dispatched"),
        ("Peter Njoroge",  "Corporate lunch — 1 pending payment"),
        ("Sylvia Achieng", "Payment failure — M-Pesa declined"),
        ("James Kamau",    "Cancelled order"),
        ("Naomi Chebet",   "High-value — 2100 pts, 1 active confirmed order"),
    ]:
        print(f"  • {name}: {profile}")
    print()


if __name__ == "__main__":
    asyncio.run(seed())
