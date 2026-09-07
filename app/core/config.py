from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://kitchen:kitchen@localhost:5432/kitchen_db",
        description="Async PostgreSQL connection URL (asyncpg driver)",
    )

    # Application
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)

    # Webhook
    mock_restaurant_webhook_url: str = Field(
        default="http://localhost:8001/webhook/order",
        description="URL Mock Restaurant API для отправки вебхуков",
    )


settings = Settings()
