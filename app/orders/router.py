import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user_id, get_db
from app.orders.schemas import OrderCreate, OrderResponse, OrderStatusUpdate
from app.orders.service import (
    create_order,
    get_order,
    send_order_webhook,
    update_order_status,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_new_order(
    payload: OrderCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> OrderResponse:
    order = await create_order(session, user_id, payload)
    response = OrderResponse.model_validate(order)

    background_tasks.add_task(
        send_order_webhook,
        webhook_url=settings.mock_restaurant_webhook_url,
        order_id=order.id,
        restaurant_id=order.restaurant_id,
        user_id=order.user_id,
        delivery_address=order.delivery_address,
        total_price=order.total_price,
        items=[
            {
                "menu_item_id": str(item.menu_item_id),
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
            }
            for item in order.order_items
        ],
    )

    return response


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(
    order_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> OrderResponse:
    order = await get_order(session, order_id)
    return OrderResponse.model_validate(order)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def patch_order_status(
    order_id: uuid.UUID,
    payload: OrderStatusUpdate,
    session: AsyncSession = Depends(get_db),
) -> OrderResponse:
    order = await update_order_status(session, order_id, payload.status)
    return OrderResponse.model_validate(order)
