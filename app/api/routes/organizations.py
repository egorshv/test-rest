from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Select, func
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.api.utils import organization_with_relationships_stmt
from app.models import Building, Organization
from app.schemas.organization import OrganizationRead
from app.services.geo import approximate_bounding_box, haversine_km

router = APIRouter(prefix="/organizations", tags=["organizations"], dependencies=[Depends(require_api_key)])


def _base_organization_stmt() -> Select[Organization]:
    return organization_with_relationships_stmt()


@router.get("/search", response_model=list[OrganizationRead])
def search_organizations(
    query: str = Query(..., min_length=2, description="Case insensitive substring for organization name"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[Organization]:
    stmt = (
        _base_organization_stmt()
        .where(func.lower(Organization.name).contains(func.lower(query.strip())))
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


@router.get("/nearby", response_model=list[OrganizationRead])
def organizations_nearby(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float | None = Query(None, gt=0, description="Search radius in kilometers"),
    min_latitude: float | None = Query(None, ge=-90, le=90),
    max_latitude: float | None = Query(None, ge=-90, le=90),
    min_longitude: float | None = Query(None, ge=-180, le=180),
    max_longitude: float | None = Query(None, ge=-180, le=180),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Organization]:
    if radius_km is None and None in {min_latitude, max_latitude, min_longitude, max_longitude}:
        raise HTTPException(
            status_code=400,
            detail="Provide either radius_km or the full rectangular bounds (min/max lat & lon).",
        )

    if radius_km is not None:
        min_latitude, max_latitude, min_longitude, max_longitude = approximate_bounding_box(
            latitude, longitude, radius_km
        )

    limit_multiplier = 5 if radius_km is not None else 1

    stmt = (
        _base_organization_stmt()
        .where(
            Building.latitude >= min_latitude,
            Building.latitude <= max_latitude,
            Building.longitude >= min_longitude,
            Building.longitude <= max_longitude,
        )
        .limit(limit * limit_multiplier)
    )
    candidates = list(db.scalars(stmt).all())

    if radius_km is None:
        return candidates[:limit]

    filtered: list[Organization] = []
    for organization in candidates:
        distance = haversine_km(
            latitude,
            longitude,
            organization.building.latitude,
            organization.building.longitude,
        )
        if distance <= radius_km:
            filtered.append(organization)
        if len(filtered) >= limit:
            break
    return filtered


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(organization_id: int, db: Session = Depends(get_db)) -> Organization:
    stmt = _base_organization_stmt().where(Organization.id == organization_id)
    organization = db.scalar(stmt)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization
