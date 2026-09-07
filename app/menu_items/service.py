import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.menu_items.models import MenuItem


async def get_available_menu_items(
    session: AsyncSession, restaurant_id: uuid.UUID
) -> list[MenuItem]:
    result = await session.execute(
        select(MenuItem)
        .where(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.is_available.is_(True),
        )
        .order_by(MenuItem.name)
    )
    return list(result.scalars().all())
