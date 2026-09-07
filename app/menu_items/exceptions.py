import uuid

from app.core.exceptions import BaseAppException


class MenuItemNotFoundError(BaseAppException):
    def __init__(self, menu_item_id: uuid.UUID) -> None:
        self.menu_item_id = menu_item_id
        super().__init__(f"Menu item {menu_item_id} not found")


class MenuItemUnavailableError(BaseAppException):
    def __init__(self, menu_item_id: uuid.UUID) -> None:
        self.menu_item_id = menu_item_id
        super().__init__(f"Menu item {menu_item_id} is not available")
