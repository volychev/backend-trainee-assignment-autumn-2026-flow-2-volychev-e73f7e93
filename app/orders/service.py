import logging
import uuid
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.menu_items.exceptions import MenuItemNotFoundError, MenuItemUnavailableError
from app.menu_items.models import MenuItem
from app.order_items.models import OrderItem
from app.orders.enums import OrderStatus
from app.orders.exceptions import OrderNotFoundError
from app.orders.models import Order
from app.orders.schemas import OrderCreate

logger = logging.getLogger(__name__)



async def create_order(
    session: AsyncSession,
    user_id: uuid.UUID,
    payload: OrderCreate,
) -> Order:
    menu_item_ids = [item.menu_item_id for item in payload.items]
    result = await session.execute(
        select(MenuItem).where(MenuItem.id.in_(menu_item_ids))
    )
    menu_items_map: dict[uuid.UUID, MenuItem] = {
        mi.id: mi for mi in result.scalars().all()
    }

    for item in payload.items:
        if item.menu_item_id not in menu_items_map:
            raise MenuItemNotFoundError(item.menu_item_id)
        if not menu_items_map[item.menu_item_id].is_available:
            raise MenuItemUnavailableError(item.menu_item_id)

    total_price: Decimal = sum(
        (menu_items_map[item.menu_item_id].price * item.quantity for item in payload.items),
        Decimal(0),
    )

    order = Order(
        user_id=user_id,
        restaurant_id=payload.restaurant_id,
        status=OrderStatus.PENDING,
        delivery_address=payload.delivery_address,
        total_price=total_price,
    )
    session.add(order)
    await session.flush()

    for item in payload.items:
        session.add(
            OrderItem(
                order_id=order.id,
                menu_item_id=item.menu_item_id,
                quantity=item.quantity,
                unit_price=menu_items_map[item.menu_item_id].price,
            )
        )
    await session.flush()

    refreshed = await session.execute(
        select(Order)
        .options(selectinload(Order.order_items))
        .where(Order.id == order.id)
    )
    return refreshed.scalar_one()


async def get_order(session: AsyncSession, order_id: uuid.UUID) -> Order:
    result = await session.execute(
        select(Order)
        .options(selectinload(Order.order_items))
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if order is None:
        raise OrderNotFoundError(order_id)
    return order


async def update_order_status(
    session: AsyncSession,
    order_id: uuid.UUID,
    new_status: OrderStatus,
) -> Order:
    result = await session.execute(
        select(Order)
        .options(selectinload(Order.order_items))
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if order is None:
        raise OrderNotFoundError(order_id)
    order.status = new_status
    return order


async def send_order_webhook(
    webhook_url: str,
    order_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    user_id: uuid.UUID,
    delivery_address: str,
    total_price: Decimal,
    items: list[dict[str, object]],
) -> None:
    payload = {
        "order_id": str(order_id),
        "restaurant_id": str(restaurant_id),
        "user_id": str(user_id),
        "delivery_address": delivery_address,
        "total_price": str(total_price),
        "items": items,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(webhook_url, json=payload)
        except httpx.RequestError as exc:
            logger.warning("Webhook delivery failed for order %s: %s", order_id, exc)
