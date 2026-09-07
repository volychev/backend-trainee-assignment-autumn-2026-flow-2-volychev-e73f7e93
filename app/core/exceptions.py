class BaseAppException(Exception):
    """Базовый класс для всех доменных ошибок приложения."""
    detail: str

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)
