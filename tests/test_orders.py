import uuid

import pytest
from httpx import AsyncClient

from app.menu_items.models import MenuItem
from app.orders.enums import OrderStatus
from app.restaurants.models import Restaurant


@pytest.mark.asyncio
async def test_create_order_returns_201(
    client: AsyncClient, restaurant: Restaurant, menu_item: MenuItem
) -> None:
    payload = {
        "restaurant_id": str(restaurant.id),
        "delivery_address": "ул. Пушкина, 10",
        "items": [{"menu_item_id": str(menu_item.id), "quantity": 2}],
    }

    response = await client.post("/orders", json=payload)

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_order_status_is_pending(
    client: AsyncClient, restaurant: Restaurant, menu_item: MenuItem
) -> None:
    payload = {
        "restaurant_id": str(restaurant.id),
        "delivery_address": "ул. Пушкина, 10",
        "items": [{"menu_item_id": str(menu_item.id), "quantity": 1}],
    }

    response = await client.post("/orders", json=payload)

    assert response.json()["status"] == OrderStatus.PENDING


@pytest.mark.asyncio
async def test_create_order_calculates_total_price(
    client: AsyncClient, restaurant: Restaurant, menu_item: MenuItem
) -> None:
    quantity = 3
    payload = {
        "restaurant_id": str(restaurant.id),
        "delivery_address": "ул. Пушкина, 10",
        "items": [{"menu_item_id": str(menu_item.id), "quantity": quantity}],
    }

    response = await client.post("/orders", json=payload)

    expected_total = float(menu_item.price) * quantity
    assert float(response.json()["total_price"]) == pytest.approx(expected_total)


@pytest.mark.asyncio
async def test_create_order_returns_order_id(
    client: AsyncClient, restaurant: Restaurant, menu_item: MenuItem
) -> None:
    payload = {
        "restaurant_id": str(restaurant.id),
        "delivery_address": "ул. Пушкина, 10",
        "items": [{"menu_item_id": str(menu_item.id), "quantity": 1}],
    }

    response = await client.post("/orders", json=payload)

    order_id = response.json().get("id")
    assert order_id is not None
    assert uuid.UUID(order_id)


@pytest.mark.asyncio
async def test_create_order_unavailable_item_returns_400(
    client: AsyncClient, session, restaurant: Restaurant, menu_item: MenuItem
) -> None:
    menu_item.is_available = False
    await session.flush()

    payload = {
        "restaurant_id": str(restaurant.id),
        "delivery_address": "ул. Пушкина, 10",
        "items": [{"menu_item_id": str(menu_item.id), "quantity": 1}],
    }

    response = await client.post("/orders", json=payload)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_order_unknown_item_returns_404(
    client: AsyncClient, restaurant: Restaurant
) -> None:
    payload = {
        "restaurant_id": str(restaurant.id),
        "delivery_address": "ул. Пушкина, 10",
        "items": [{"menu_item_id": str(uuid.uuid4()), "quantity": 1}],
    }

    response = await client.post("/orders", json=payload)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_order_returns_correct_data(
    client: AsyncClient, restaurant: Restaurant, menu_item: MenuItem
) -> None:
    payload = {
        "restaurant_id": str(restaurant.id),
        "delivery_address": "ул. Ленина, 5",
        "items": [{"menu_item_id": str(menu_item.id), "quantity": 2}],
    }
    created = (await client.post("/orders", json=payload)).json()

    response = await client.get(f"/orders/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["delivery_address"] == "ул. Ленина, 5"


@pytest.mark.asyncio
async def test_get_order_not_found(client: AsyncClient) -> None:
    response = await client.get(f"/orders/{uuid.uuid4()}")

    assert response.status_code == 404
