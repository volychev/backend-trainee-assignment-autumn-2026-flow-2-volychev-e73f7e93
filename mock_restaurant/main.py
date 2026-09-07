import asyncio
import logging
import random

import httpx
from fastapi import BackgroundTasks, FastAPI, Request, status
from fastapi.responses import JSONResponse

from mock_restaurant.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mock Restaurant API",
    description="Эмулятор ресторана-партнёра. Принимает вебхуки о заказах и возвращает статус в Main API.",
    version="0.1.0",
)


async def process_order(order_id: str) -> None:
    """Эмулирует процесс приготовления заказа и отправляет статус READY в Main API."""
    cook_time = random.uniform(5, 10)
    await asyncio.sleep(cook_time)

    url = f"{settings.main_api_url}/orders/{order_id}/status"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.patch(url, json={"status": "READY"})
            response.raise_for_status()
            logger.info("Order %s marked as READY", order_id)
        except httpx.HTTPError as exc:
            logger.warning("Failed to update status for order %s: %s", order_id, exc)


@app.post("/webhook/order", status_code=status.HTTP_200_OK)
async def receive_order_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> JSONResponse:
    payload = await request.json()
    order_id: str = payload.get("order_id", "")

    if not order_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "order_id is required"},
        )

    logger.info("Received webhook for order %s", order_id)
    background_tasks.add_task(process_order, order_id)

    return JSONResponse(content={"received": True, "order_id": order_id})
