import enum


class OrderStatus(enum.StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    COOKING = "COOKING"
    READY = "READY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
