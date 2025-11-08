from collections.abc import Generator

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import SessionLocal

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_settings_dependency() -> Settings:
    return get_settings()


def require_api_key(
    api_key: str | None = Security(api_key_header), settings: Settings = Depends(get_settings_dependency)
) -> str:
    if api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return api_key
