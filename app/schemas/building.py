from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict


class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float


class BuildingRead(BuildingBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BuildingWithOrganizations(BuildingRead):
    organizations: list["OrganizationRead"] | None = None

    model_config = ConfigDict(from_attributes=True)


if TYPE_CHECKING:  # pragma: no cover - used only for type hints
    from app.schemas.organization import OrganizationRead
