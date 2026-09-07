import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import TIMESTAMP, Boolean, CheckConstraint, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"
    __table_args__ = (
        CheckConstraint("price > 0", name="ck_menu_items_price_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("restaurants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_available: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    restaurant: Mapped["Restaurant"] = relationship(  # noqa: F821
        "Restaurant",
        back_populates="menu_items",
        lazy="raise",
    )
    order_items: Mapped[list["OrderItem"]] = relationship(  # noqa: F821
        "OrderItem",
        back_populates="menu_item",
        lazy="raise",
    )
