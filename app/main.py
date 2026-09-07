import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import BaseAppException
from app.menu_items.exceptions import MenuItemNotFoundError, MenuItemUnavailableError
from app.menu_items.router import router as menu_router
from app.orders.exceptions import OrderNotFoundError
from app.orders.router import router as orders_router
from app.restaurants.exceptions import RestaurantNotFoundError
from app.restaurants.router import router as restaurants_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Авито.Кухня",
    description="MVP платформа доставки еды — REST API для управления ресторанами, меню и заказами.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(restaurants_router)
app.include_router(menu_router)
app.include_router(orders_router)


# --- Domain exception handlers ---

@app.exception_handler(OrderNotFoundError)
@app.exception_handler(RestaurantNotFoundError)
async def not_found_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail},
    )


@app.exception_handler(MenuItemNotFoundError)
async def menu_item_not_found_handler(
    request: Request, exc: MenuItemNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail},
    )


@app.exception_handler(MenuItemUnavailableError)
async def menu_item_unavailable_handler(
    request: Request, exc: MenuItemUnavailableError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.detail},
    )


# --- Framework exception handlers ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
