from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_organization_service, require_api_key
from app.schemas.organization import OrganizationRead
from app.services.exceptions import NotFoundError, ValidationError
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"], dependencies=[Depends(require_api_key)])


@router.get("/search", response_model=list[OrganizationRead])
def search_organizations(
    query: str = Query(..., min_length=2, description="Case insensitive substring for organization name"),
    limit: int = Query(50, ge=1, le=200),
    service: OrganizationService = Depends(get_organization_service),
):
    return service.search_organizations(query, limit)


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
    service: OrganizationService = Depends(get_organization_service),
):
    try:
        return service.organizations_nearby(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude,
            limit=limit,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(
    organization_id: int,
    service: OrganizationService = Depends(get_organization_service),
):
    try:
        return service.get_organization(organization_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
