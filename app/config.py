from functools import lru_cache

from dotenv import find_dotenv
from pydantic import SecretStr, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(usecwd=True),
        env_file_encoding="utf-8",
        extra="ignore",
        # default env_file solution search .env every time BaseSettings is instantiated
        # dotenv search .env when module is imported, without usecwd it starts from the file it was called
    )

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

    # 0. pytest ini_options
    # 1. environment variables
    # 2. .env
    # 3. default values in pydantic settings


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
