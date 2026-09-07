from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.restaurants.models import Restaurant


async def get_active_restaurants(session: AsyncSession) -> list[Restaurant]:
    result = await session.execute(
        select(Restaurant)
        .where(Restaurant.is_active.is_(True))
        .order_by(Restaurant.name)
    )
    return list(result.scalars().all())
