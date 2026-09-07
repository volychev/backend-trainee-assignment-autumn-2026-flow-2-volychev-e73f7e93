import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MenuItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    description: str | None
    price: Decimal
    is_available: bool
    created_at: datetime
    updated_at: datetime | None
