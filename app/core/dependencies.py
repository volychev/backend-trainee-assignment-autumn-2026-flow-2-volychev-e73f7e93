import uuid
from collections.abc import AsyncGenerator

from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionFactory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user_id(x_user_id: uuid.UUID = Header(...)) -> uuid.UUID:
    return x_user_id
