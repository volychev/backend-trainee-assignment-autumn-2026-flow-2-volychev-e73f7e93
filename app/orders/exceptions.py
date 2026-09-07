import uuid

from app.core.exceptions import BaseAppException


class OrderNotFoundError(BaseAppException):
    def __init__(self, order_id: uuid.UUID) -> None:
        super().__init__(f"Order {order_id} not found")
