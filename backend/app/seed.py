"""
TableWise Seed Script
Realistic fast-food restaurant data for a multi-branch Kenyan chain.
"""

import os
import sys
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# ENVIRONMENT VARIABLES & PATH FIX
# ─────────────────────────────────────────────
# 1. Dynamically find the backend directory (parent of the 'app' folder)
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ENV_PATH = os.path.join(BACKEND_DIR, '.env')

# 2. Load the environment variables explicitly BEFORE importing app modules
load_dotenv(ENV_PATH)

# 3. Ensure Python can resolve the 'app' module imports
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# ─────────────────────────────────────────────
# NOW SAFE TO IMPORT APP MODULES
# ─────────────────────────────────────────────
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
from app.models.inventory_item import InventoryItem
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
# DETERMINISTIC ID GENERATOR (PREVENTS DUPLICATES)
# ─────────────────────────────────────────────
NAMESPACE_TABLEWISE = uuid.UUID('00000000-0000-0000-0000-000000000000')

def gen_id(unique_string: str) -> uuid.UUID:
    """Generates the same UUID every time for a given string."""
    return uuid.uuid5(NAMESPACE_TABLEWISE, unique_string)


# ─────────────────────────────────────────────
# BRANCHES
# ─────────────────────────────────────────────
branch_westlands_id = gen_id("branch_westlands")
branch_cbd_id       = gen_id("branch_cbd")
branch_karen_id     = gen_id("branch_karen")

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
    User(id=gen_id("user_brian"), email="brian.kariuki@tablewise.co.ke",
         hashed_password=pwd_context.hash("TableWise@2025"),
         full_name="Brian Kariuki", phone_number="0712000001",
         role=UserRole.OWNER, is_active=True, branch_id=None,
         created_at=days_ago(90), updated_at=days_ago(90)),
    User(id=gen_id("user_amina"), email="amina.odhiambo@tablewise.co.ke",
         hashed_password=pwd_context.hash("Manager@2025"),
         full_name="Amina Odhiambo", phone_number="0712000002",
         role=UserRole.BRANCH_MANAGER, is_active=True, branch_id=branch_westlands_id,
         created_at=days_ago(90), updated_at=days_ago(90)),
    User(id=gen_id("user_kevin"), email="kevin.mutua@tablewise.co.ke",
         hashed_password=pwd_context.hash("Cashier@2025"),
         full_name="Kevin Mutua", phone_number="0712000003",
         role=UserRole.CASHIER, is_active=True, branch_id=branch_cbd_id,
         created_at=days_ago(90), updated_at=days_ago(90)),
]


# ─────────────────────────────────────────────
# CUSTOMERS
# ─────────────────────────────────────────────
customer_grace_id  = gen_id("cust_254712100001")
customer_daniel_id = gen_id("cust_254712100002")
customer_fatuma_id = gen_id("cust_254712100003")
customer_peter_id  = gen_id("cust_254712100004")
customer_sylvia_id = gen_id("cust_254712100005")
customer_james_id  = gen_id("cust_254712100006")
customer_naomi_id  = gen_id("cust_254712100007")

CUSTOMERS = [
    Customer(id=customer_grace_id,  phone_number="254712100001", full_name="Grace Wanjiku", email="grace.wanjiku@gmail.com",  loyalty_points=1250, created_at=days_ago(60), updated_at=days_ago(3)),
    Customer(id=customer_daniel_id, phone_number="254712100002", full_name="Daniel Otieno", email="daniel.otieno@gmail.com",  loyalty_points=0, created_at=days_ago(1),  updated_at=days_ago(1)),
    Customer(id=customer_fatuma_id, phone_number="254712100003", full_name="Fatuma Hassan", email="fatuma.hassan@gmail.com",  loyalty_points=430, created_at=days_ago(30), updated_at=days_ago(2)),
    Customer(id=customer_peter_id,  phone_number="254712100004", full_name="Peter Njoroge", email="peter.njoroge@corporation.co.ke", loyalty_points=780, created_at=days_ago(45), updated_at=days_ago(1)),
    Customer(id=customer_sylvia_id, phone_number="254712100005", full_name="Sylvia Achieng", email="sylvia.achieng@gmail.com", loyalty_points=90, created_at=days_ago(20), updated_at=days_ago(2)),
    Customer(id=customer_james_id,  phone_number="254712100006", full_name="James Kamau", email="james.kamau@gmail.com",    loyalty_points=200, created_at=days_ago(15), updated_at=days_ago(5)),
    Customer(id=customer_naomi_id,  phone_number="254712100007", full_name="Naomi Chebet", email="naomi.chebet@gmail.com",   loyalty_points=2100, created_at=days_ago(90), updated_at=hours_ago(1)),
]


# ─────────────────────────────────────────────
# MENU CATEGORIES & ITEMS
# ─────────────────────────────────────────────
cat_burgers_id = gen_id("cat_burgers")
cat_sides_id   = gen_id("cat_sides")
cat_drinks_id  = gen_id("cat_drinks")

CATEGORIES = [
    MenuCategory(id=cat_burgers_id, name="Burgers & Wraps", description="Flame-grilled burgers and stuffed wraps", is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuCategory(id=cat_sides_id, name="Sides & Extras", description="Fries, onion rings, and add-ons", is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuCategory(id=cat_drinks_id, name="Drinks", description="Fresh juices, sodas, and shakes", is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
]

item_classic_id  = gen_id("item_classic")
item_spicy_id    = gen_id("item_spicy")
item_bbq_id      = gen_id("item_bbq")
item_veggie_id   = gen_id("item_veggie")
item_fries_id    = gen_id("item_fries")
item_rings_id    = gen_id("item_rings")
item_coleslaw_id = gen_id("item_coleslaw")
item_mango_id    = gen_id("item_mango")
item_passion_id  = gen_id("item_passion")
item_soda_id     = gen_id("item_soda")

MENU_ITEMS = [
    MenuItem(id=item_classic_id,  category_id=cat_burgers_id, name="Nairobi Classic Burger", price=Decimal("650.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_spicy_id,    category_id=cat_burgers_id, name="Spicy Chicken Burger", price=Decimal("580.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_bbq_id,      category_id=cat_burgers_id, name="Smoky BBQ Beef Wrap", price=Decimal("520.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_veggie_id,   category_id=cat_burgers_id, name="Veggie Deluxe Burger", price=Decimal("490.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_fries_id,    category_id=cat_sides_id,   name="Seasoned Fries", price=Decimal("200.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_rings_id,    category_id=cat_sides_id,   name="Onion Rings", price=Decimal("220.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_coleslaw_id, category_id=cat_sides_id,   name="Coleslaw Cup", price=Decimal("120.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_mango_id,    category_id=cat_drinks_id,  name="Fresh Mango Juice", price=Decimal("180.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_passion_id,  category_id=cat_drinks_id,  name="Passion Fruit Shake", price=Decimal("220.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
    MenuItem(id=item_soda_id,     category_id=cat_drinks_id,  name="Soft Drink (500ml)", price=Decimal("100.00"), is_active=True, created_at=days_ago(90), updated_at=days_ago(90)),
]


# ─────────────────────────────────────────────
# INVENTORY ITEMS
# ─────────────────────────────────────────────
INVENTORY_ITEMS = [
    InventoryItem(id=gen_id("inv_west_beef"), branch_id=branch_westlands_id, name="Beef Patties (150g)", sku="BEEF-150-W", quantity=Decimal("250.0"), unit="pcs", low_stock_threshold=Decimal("50.0"), created_at=days_ago(30), updated_at=now()),
    InventoryItem(id=gen_id("inv_west_chicken"), branch_id=branch_westlands_id, name="Chicken Breast", sku="CHCK-BRST-W", quantity=Decimal("120.0"), unit="pcs", low_stock_threshold=Decimal("40.0"), created_at=days_ago(30), updated_at=now()),
    InventoryItem(id=gen_id("inv_west_buns"), branch_id=branch_westlands_id, name="Brioche Buns", sku="BUN-BRI-W", quantity=Decimal("300.0"), unit="pcs", low_stock_threshold=Decimal("100.0"), created_at=days_ago(30), updated_at=now()),
    InventoryItem(id=gen_id("inv_west_potatoes"), branch_id=branch_westlands_id, name="Potatoes", sku="POT-RAW-W", quantity=Decimal("150.0"), unit="kg", low_stock_threshold=Decimal("30.0"), created_at=days_ago(30), updated_at=now()),
    InventoryItem(id=gen_id("inv_west_oil"), branch_id=branch_westlands_id, name="Cooking Oil", sku="OIL-COOK-W", quantity=Decimal("40.0"), unit="L", low_stock_threshold=Decimal("15.0"), created_at=days_ago(30), updated_at=now()),
    InventoryItem(id=gen_id("inv_west_boxes"), branch_id=branch_westlands_id, name="Takeaway Boxes", sku="BOX-TAKE-W", quantity=Decimal("800.0"), unit="pcs", low_stock_threshold=Decimal("200.0"), created_at=days_ago(30), updated_at=now()),
    InventoryItem(id=gen_id("inv_cbd_beef"), branch_id=branch_cbd_id, name="Beef Patties (150g)", sku="BEEF-150-C", quantity=Decimal("180.0"), unit="pcs", low_stock_threshold=Decimal("50.0"), created_at=days_ago(30), updated_at=now()),
    InventoryItem(id=gen_id("inv_cbd_buns"), branch_id=branch_cbd_id, name="Brioche Buns", sku="BUN-BRI-C", quantity=Decimal("25.0"), unit="pcs", low_stock_threshold=Decimal("100.0"), created_at=days_ago(30), updated_at=now()),
    InventoryItem(id=gen_id("inv_cbd_potatoes"), branch_id=branch_cbd_id, name="Potatoes", sku="POT-RAW-C", quantity=Decimal("80.0"), unit="kg", low_stock_threshold=Decimal("30.0"), created_at=days_ago(30), updated_at=now()),
]


# ─────────────────────────────────────────────
# HELPERS & ORDERS
# ─────────────────────────────────────────────
def make_order_items(order_id, lines, ts):
    return [
        OrderItem(id=gen_id(f"oi_{order_id}_{item_id}"), order_id=order_id, menu_item_id=item_id,
                  quantity=qty, unit_price=price, subtotal=price * qty,
                  special_instructions=None, created_at=ts, updated_at=ts)
        for item_id, price, qty in lines
    ]

def make_payment(order_id, amount, status, checkout_id, receipt, phone, ts):
    return Payment(id=gen_id(f"pay_{order_id}"), order_id=order_id, amount=amount,
                   method=PaymentMethod.MPESA, status=status,
                   checkout_request_id=checkout_id, mpesa_receipt_number=receipt,
                   payer_phone_number=phone, created_at=ts, updated_at=ts)

def make_order(order_id, branch_id, customer_id, status, lines, is_delivery, address, notes, ts):
    total = sum(p * q for _, p, q in lines)
    return Order(id=order_id, branch_id=branch_id, customer_id=customer_id,
                 cashier_id=None, status=status, total_amount=total,
                 is_delivery=is_delivery, delivery_address=address,
                 notes=notes, created_at=ts, updated_at=ts), total

def build_orders():
    orders, order_items, payments = [], [], []

    def add(order_id, branch_id, customer_id, status, lines, is_delivery, address, notes, ts, pay_status=None, checkout_id=None, receipt=None, phone=None):
        order, total = make_order(order_id, branch_id, customer_id, status, lines, is_delivery, address, notes, ts)
        orders.append(order)
        order_items.extend(make_order_items(order_id, lines, ts))
        if pay_status:
            payments.append(make_payment(order_id, total, pay_status, checkout_id, receipt, phone, ts))

    add(gen_id("order_grace_1"), branch_westlands_id, customer_grace_id, OrderStatus.DELIVERED, [(item_classic_id, Decimal("650.00"), 1), (item_fries_id, Decimal("200.00"), 1), (item_mango_id, Decimal("180.00"), 1)], True, "Westlands, Rose Avenue, Apt 4B", None, days_ago(10), PaymentStatus.SUCCESS, "ws_CO_GRACE_001", "QKA7X2BN01", "254712100001")
    add(gen_id("order_grace_2"), branch_westlands_id, customer_grace_id, OrderStatus.DELIVERED, [(item_spicy_id, Decimal("580.00"), 1), (item_rings_id, Decimal("220.00"), 1), (item_passion_id, Decimal("220.00"), 1)], False, None, "Extra napkins please", days_ago(3), PaymentStatus.SUCCESS, "ws_CO_GRACE_002", "QKA7X2BN02", "254712100001")
    add(gen_id("order_grace_3"), branch_westlands_id, customer_grace_id, OrderStatus.PREPARING, [(item_classic_id, Decimal("650.00"), 2), (item_fries_id, Decimal("200.00"), 2), (item_soda_id, Decimal("100.00"), 2)], True, "Westlands, Rose Avenue, Apt 4B", None, hours_ago(1), PaymentStatus.SUCCESS, "ws_CO_GRACE_003", "QKA7X2BN03", "254712100001")
    add(gen_id("order_fatuma_1"), branch_karen_id, customer_fatuma_id, OrderStatus.DISPATCHED, [(item_bbq_id, Decimal("520.00"), 1), (item_fries_id, Decimal("200.00"), 1), (item_mango_id, Decimal("180.00"), 1)], True, "Karen, Langata Road, House 12", "Call when at gate", hours_ago(2), PaymentStatus.SUCCESS, "ws_CO_FATUMA_001", "QKA7X2BN04", "254712100003")
    add(gen_id("order_peter_1"), branch_cbd_id, customer_peter_id, OrderStatus.DELIVERED, [(item_classic_id, Decimal("650.00"), 3), (item_spicy_id, Decimal("580.00"), 2), (item_veggie_id, Decimal("490.00"), 1), (item_fries_id, Decimal("200.00"), 4), (item_coleslaw_id, Decimal("120.00"), 3), (item_soda_id, Decimal("100.00"), 5)], False, None, "Office lunch", days_ago(1), PaymentStatus.SUCCESS, "ws_CO_PETER_001", "QKA7X2BN05", "254712100004")

    return orders, order_items, payments


# ─────────────────────────────────────────────
# MAIN EXECUTOR
# ─────────────────────────────────────────────
async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            print("\n🌱 Seeding TableWise database (Idempotent Mode)...\n")

            print("  → Branches...")
            for obj in BRANCHES: await session.merge(obj)

            print("  → Users...")
            for obj in USERS: await session.merge(obj)

            print("  → Customers...")
            for obj in CUSTOMERS: await session.merge(obj)

            print("  → Menu categories...")
            for obj in CATEGORIES: await session.merge(obj)

            print("  → Menu items...")
            for obj in MENU_ITEMS: await session.merge(obj)

            print("  → Inventory items...")
            for obj in INVENTORY_ITEMS: await session.merge(obj)

            print("  → Orders, order items & payments...")
            orders, order_items, payments = build_orders()
            for obj in orders:      await session.merge(obj)
            for obj in order_items: await session.merge(obj)
            for obj in payments:    await session.merge(obj)

    await engine.dispose()
    print("\n✅ Seeding Complete!\n")

if __name__ == "__main__":
    asyncio.run(seed())