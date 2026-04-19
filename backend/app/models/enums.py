import enum

class UserRole(str, enum.Enum):
    OWNER = "owner"
    BRANCH_MANAGER = "branch_manager"
    CASHIER = "cashier"
    CHEF = "chef"
    RIDER = "rider"

class OrderStatus(str, enum.Enum):
    CREATED = "created"
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"
    PAYMENT_FAILED = "payment_failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REVERSED = "reversed"

class PaymentMethod(str, enum.Enum):
    MPESA = "mpesa"
    CARD = "card"
    CASH = "cash"