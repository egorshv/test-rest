from collections.abc import Generator

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.dao import ActivityDAO, BuildingDAO, OrganizationDAO
from app.core.config import Settings, get_settings
from app.db.session import SessionLocal
from app.services.activity_service import ActivityService
from app.services.building_service import BuildingService
from app.services.organization_service import OrganizationService

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


def get_activity_service(db: Session = Depends(get_db)) -> ActivityService:
    return ActivityService(ActivityDAO(db), OrganizationDAO(db))


def get_building_service(db: Session = Depends(get_db)) -> BuildingService:
    organization_dao = OrganizationDAO(db)
    return BuildingService(BuildingDAO(db), organization_dao)


def get_organization_service(db: Session = Depends(get_db)) -> OrganizationService:
    return OrganizationService(OrganizationDAO(db))
