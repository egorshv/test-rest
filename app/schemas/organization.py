from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.activity import ActivityRead
from app.schemas.building import BuildingRead


class OrganizationPhoneRead(BaseModel):
    phone_number: str

    model_config = ConfigDict(from_attributes=True)


class OrganizationRead(BaseModel):
    id: int
    name: str
    building: BuildingRead
    activities: list[ActivityRead]
    phones: list[OrganizationPhoneRead]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
