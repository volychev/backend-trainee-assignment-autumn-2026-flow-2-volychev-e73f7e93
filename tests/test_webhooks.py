import uuid

import pytest
from httpx import AsyncClient

from app.orders.enums import OrderStatus
from app.orders.models import Order


@pytest.mark.asyncio
async def test_update_status_to_ready(
    client: AsyncClient, order: Order
) -> None:
    response = await client.patch(
        f"/orders/{order.id}/status",
        json={"status": OrderStatus.READY},
    )

    assert response.status_code == 200
    assert response.json()["status"] == OrderStatus.READY


@pytest.mark.asyncio
async def test_update_status_to_delivered(
    client: AsyncClient, order: Order
) -> None:
    response = await client.patch(
        f"/orders/{order.id}/status",
        json={"status": OrderStatus.DELIVERED},
    )

    assert response.status_code == 200
    assert response.json()["status"] == OrderStatus.DELIVERED


@pytest.mark.asyncio
async def test_update_status_to_cancelled(
    client: AsyncClient, order: Order
) -> None:
    response = await client.patch(
        f"/orders/{order.id}/status",
        json={"status": OrderStatus.CANCELLED},
    )

    assert response.status_code == 200
    assert response.json()["status"] == OrderStatus.CANCELLED


@pytest.mark.asyncio
async def test_update_status_invalid_value_returns_422(
    client: AsyncClient, order: Order
) -> None:
    response = await client.patch(
        f"/orders/{order.id}/status",
        json={"status": "FLYING"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_status_unknown_order_returns_404(client: AsyncClient) -> None:
    response = await client.patch(
        f"/orders/{uuid.uuid4()}/status",
        json={"status": OrderStatus.READY},
    )

    assert response.status_code == 404
