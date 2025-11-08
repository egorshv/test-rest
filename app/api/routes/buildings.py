from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db, require_api_key
from app.models import Building, Organization
from app.schemas.building import BuildingRead
from app.schemas.organization import OrganizationRead

router = APIRouter(prefix="/buildings", tags=["buildings"], dependencies=[Depends(require_api_key)])


@router.get("/", response_model=list[BuildingRead])
def list_buildings(db: Session = Depends(get_db)) -> list[Building]:
    stmt = select(Building).order_by(Building.id)
    return list(db.scalars(stmt).all())


@router.get("/{building_id}/organizations", response_model=list[OrganizationRead])
def organizations_in_building(building_id: int, db: Session = Depends(get_db)) -> list[Organization]:
    building = db.get(Building, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    stmt = (
        select(Organization)
        .options(selectinload(Organization.activities), selectinload(Organization.phones), selectinload(Organization.building))
        .where(Organization.building_id == building_id)
        .order_by(Organization.name)
    )
    return list(db.scalars(stmt).all())
