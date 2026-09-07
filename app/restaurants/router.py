from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.restaurants.schemas import RestaurantResponse
from app.restaurants.service import get_active_restaurants

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("", response_model=list[RestaurantResponse])
async def list_restaurants(
    session: AsyncSession = Depends(get_db),
) -> list[RestaurantResponse]:
    restaurants = await get_active_restaurants(session)
    return [RestaurantResponse.model_validate(r) for r in restaurants]
