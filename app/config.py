from functools import lru_cache

from pydantic import SecretStr, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding="utf-8", extra="ignore")

    # API SETTINGS
    api_v1: str = "/api/v1"
    api_latest: str = api_v1
    paging_limit: int = 1000

    # DATABASE SETTINGS
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "library"
    db_user: str = "user"
    db_password: SecretStr = SecretStr("password")

    @property
    def db_uri(self) -> PostgresDsn:
        return (
            f"postgresql+psycopg://"
            f"{self.db_user}:{self.db_password.get_secret_value()}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
