from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    main_api_url: str = "http://localhost:8000"
    mock_host: str = "0.0.0.0"
    mock_port: int = 8001


settings = Settings()
