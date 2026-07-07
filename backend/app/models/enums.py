import enum


class UserRole(str, enum.Enum):
    owner = "owner"
    hotel_manager = "hotel_manager"
    restaurant_manager = "restaurant_manager"
    receptionist = "receptionist"
    chef = "chef"
    bartender = "bartender"
    waiter = "waiter"
    rider = "rider"
    customer = "customer"

    # Backward-compatible aliases used by older code paths/tests.
    OWNER = "owner"
    BRANCH_MANAGER = "restaurant_manager"
    CASHIER = "receptionist"
    CHEF = "chef"
    RIDER = "rider"


class OutletType(str, enum.Enum):
    restaurant = "restaurant"
    bar = "bar"


class RoomStatus(str, enum.Enum):
    available = "available"
    occupied = "occupied"
    cleaning = "cleaning"
    maintenance = "maintenance"


class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    checked_in = "checked_in"
    checked_out = "checked_out"
    cancelled = "cancelled"


class BookingPaymentStatus(str, enum.Enum):
    unpaid = "unpaid"
    partial = "partial"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class OrderType(str, enum.Enum):
    dine_in = "dine_in"
    delivery = "delivery"
    takeaway = "takeaway"
    room_service = "room_service"


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
    pending = "pending"
    success = "success"
    failed = "failed"
    reversed = "reversed"


class PaymentMethod(str, enum.Enum):
    mpesa = "mpesa"
    cash = "cash"


class PaymentEntityType(str, enum.Enum):
    booking = "booking"
    order = "order"
