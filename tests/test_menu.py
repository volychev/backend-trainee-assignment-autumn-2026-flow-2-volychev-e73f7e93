import uuid

import pytest
from httpx import AsyncClient

from app.menu_items.models import MenuItem
from app.restaurants.models import Restaurant


@pytest.mark.asyncio
async def test_get_menu_returns_available_items(
    client: AsyncClient, menu_item: MenuItem, restaurant: Restaurant
) -> None:
    # Arrange
    # (Данные уже подготовлены в фикстуре menu_item)

    # Act
    response = await client.get(f"/restaurants/{restaurant.id}/menu")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(menu_item.id)
    assert data[0]["name"] == menu_item.name
    assert float(data[0]["price"]) == float(menu_item.price)


@pytest.mark.asyncio
async def test_get_menu_excludes_unavailable_items(
    client: AsyncClient, session, menu_item: MenuItem, restaurant: Restaurant
) -> None:
    # Arrange
    menu_item.is_available = False
    await session.flush()

    # Act
    response = await client.get(f"/restaurants/{restaurant.id}/menu")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_menu_unknown_restaurant_returns_empty(client: AsyncClient) -> None:
    # Arrange
    # (БД пустая или ресторан с таким ID не существует)

    # Act
    response = await client.get(f"/restaurants/{uuid.uuid4()}/menu")

    # Assert
    assert response.status_code == 200
    assert response.json() == []
