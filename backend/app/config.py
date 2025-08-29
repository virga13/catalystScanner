from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"
    WATCHLIST: str = "AAPL,MSFT,NVDA,TSLA"
    ALPHA_VANTAGE_API_KEY: str | None = None
    FINNHUB_API_KEY: str | None = None
    DEMO_MODE: bool = True

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "catalyst"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    BACKEND_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173"
    SEC_USER_AGENT: str | None = None

    model_config = SettingsConfigDict(env_file="../.env, .env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
