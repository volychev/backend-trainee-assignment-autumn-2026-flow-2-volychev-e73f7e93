import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.menu_items.schemas import MenuItemResponse
from app.menu_items.service import get_available_menu_items

router = APIRouter(prefix="/restaurants", tags=["Menu"])


@router.get("/{restaurant_id}/menu", response_model=list[MenuItemResponse])
async def get_restaurant_menu(
    restaurant_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> list[MenuItemResponse]:
    items = await get_available_menu_items(session, restaurant_id)
    return [MenuItemResponse.model_validate(item) for item in items]
