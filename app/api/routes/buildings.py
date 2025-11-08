from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_building_service, require_api_key
from app.schemas.building import BuildingRead
from app.schemas.organization import OrganizationRead
from app.services.building_service import BuildingService
from app.services.exceptions import NotFoundError

router = APIRouter(prefix="/buildings", tags=["buildings"], dependencies=[Depends(require_api_key)])


@router.get("/", response_model=list[BuildingRead])
def list_buildings(service: BuildingService = Depends(get_building_service)):
    return service.list_buildings()


@router.get("/{building_id}/organizations", response_model=list[OrganizationRead])
def organizations_in_building(
    building_id: int, service: BuildingService = Depends(get_building_service)
):
    try:
        return service.organizations_in_building(building_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
