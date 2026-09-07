import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.orders.enums import OrderStatus


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="UUID из заголовка X-User-ID; внешний FK появится при добавлении сервиса авторизации",
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("restaurants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="orderstatus", create_type=True),
        nullable=False,
        index=True,
        default=OrderStatus.PENDING,
    )
    delivery_address: Mapped[str] = mapped_column(String(500), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    restaurant: Mapped["Restaurant"] = relationship(  # noqa: F821
        "Restaurant",
        back_populates="orders",
        lazy="raise",
    )
    order_items: Mapped[list["OrderItem"]] = relationship(  # noqa: F821
        "OrderItem",
        back_populates="order",
        lazy="raise",
        cascade="all, delete-orphan",
    )
