from app.core.exceptions import BaseAppException


class RestaurantNotFoundError(BaseAppException):
    def __init__(self, restaurant_id: object) -> None:
        super().__init__(f"Restaurant {restaurant_id} not found")
