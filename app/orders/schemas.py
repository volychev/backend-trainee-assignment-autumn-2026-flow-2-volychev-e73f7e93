import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.orders.enums import OrderStatus


class OrderItemCreate(BaseModel):
    menu_item_id: uuid.UUID
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    restaurant_id: uuid.UUID
    delivery_address: str = Field(min_length=1)
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    menu_item_id: uuid.UUID
    quantity: int
    unit_price: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    restaurant_id: uuid.UUID
    status: OrderStatus
    delivery_address: str
    total_price: Decimal
    created_at: datetime
    updated_at: datetime | None
    order_items: list[OrderItemResponse]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
