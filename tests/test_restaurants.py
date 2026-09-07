import pytest
from httpx import AsyncClient

from app.restaurants.models import Restaurant


@pytest.mark.asyncio
async def test_list_restaurants_returns_active(
    client: AsyncClient, restaurant: Restaurant
) -> None:
    # Arrange
    # (Данные уже подготовлены в фикстуре restaurant)

    # Act
    response = await client.get("/restaurants")

    # Assert
    assert response.status_code == 200
    data = response.json()
    ids = [r["id"] for r in data]
    assert str(restaurant.id) in ids


@pytest.mark.asyncio
async def test_list_restaurants_excludes_inactive(
    client: AsyncClient, session, restaurant: Restaurant
) -> None:
    # Arrange
    restaurant.is_active = False
    await session.flush()

    # Act
    response = await client.get("/restaurants")

    # Assert
    assert response.status_code == 200
    ids = [r["id"] for r in response.json()]
    assert str(restaurant.id) not in ids


@pytest.mark.asyncio
async def test_list_restaurants_empty(client: AsyncClient) -> None:
    # Arrange
    # (БД пустая)

    # Act
    response = await client.get("/restaurants")

    # Assert
    assert response.status_code == 200
    assert response.json() == []
