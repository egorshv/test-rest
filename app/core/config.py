from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./app.db", alias="DATABASE_URL")
    api_key: str = Field(default="secret-api-key", alias="API_KEY")
    api_prefix: str = "/api"
    project_name: str = "Organization Directory"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
