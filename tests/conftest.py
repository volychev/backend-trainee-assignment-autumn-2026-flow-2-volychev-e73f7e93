import uuid
from collections.abc import AsyncGenerator
from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.core.dependencies import get_db
from app.main import app
from app.menu_items.models import MenuItem
from app.orders.enums import OrderStatus
from app.orders.models import Order
from app.order_items.models import OrderItem
from app.restaurants.models import Restaurant

from sqlalchemy.pool import NullPool

TEST_DATABASE_URL = "postgresql+asyncpg://kitchen:kitchen@localhost:5432/kitchen_db"


@pytest_asyncio.fixture
async def engine():
    test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()




@pytest_asyncio.fixture(autouse=True)
async def clean_db(engine):
    async with engine.begin() as conn:
        from sqlalchemy import text
        await conn.execute(text("TRUNCATE TABLE order_items, orders, menu_items, restaurants CASCADE;"))


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as s:
        yield s


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-User-ID": str(uuid.uuid4())},
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# --- Data factories ---

@pytest_asyncio.fixture
async def restaurant(session: AsyncSession) -> Restaurant:
    r = Restaurant(
        name="Test Burger",
        address="ул. Тестовая, 1",
        is_active=True,
    )
    session.add(r)
    await session.flush()
    return r


@pytest_asyncio.fixture
async def menu_item(session: AsyncSession, restaurant: Restaurant) -> MenuItem:
    item = MenuItem(
        restaurant_id=restaurant.id,
        name="Cheeseburger",
        price=Decimal("350.00"),
        is_available=True,
    )
    session.add(item)
    await session.flush()
    return item


@pytest_asyncio.fixture
async def order(session: AsyncSession, restaurant: Restaurant) -> Order:
    o = Order(
        user_id=uuid.uuid4(),
        restaurant_id=restaurant.id,
        status=OrderStatus.PENDING,
        delivery_address="ул. Доставки, 5",
        total_price=Decimal("350.00"),
    )
    session.add(o)
    await session.flush()

    return o
