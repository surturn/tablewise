# Import Base to ensure all models are registered with the SQLAlchemy metadata registry.
# This is required for Alembic auto-generate to work properly.

from app.database import Base
from app.models.enums import UserRole, OrderStatus, PaymentStatus, PaymentMethod
from app.models.branch import Branch
from app.models.user import User
from app.models.customer import Customer
from app.models.menu_category import MenuCategory
from app.models.menu_item import MenuItem
from app.models.inventory_item import InventoryItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.delivery_tracking import DeliveryTracking

# Expose models for easier importing elsewhere
__all__ =[
    "Base",
    "UserRole",
    "OrderStatus",
    "PaymentStatus",
    "PaymentMethod",
    "Branch",
    "User",
    "Customer",
    "MenuCategory",
    "MenuItem",
    "InventoryItem",
    "Order",
    "OrderItem",
    "Payment",
    "DeliveryTracking"
]