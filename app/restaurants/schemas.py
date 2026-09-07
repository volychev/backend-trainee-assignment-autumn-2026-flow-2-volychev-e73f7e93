import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RestaurantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    address: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
