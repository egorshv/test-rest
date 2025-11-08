from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_activity_service, require_api_key
from app.schemas.activity import ActivityRead
from app.schemas.organization import OrganizationRead
from app.services.activity_service import ActivityService
from app.services.exceptions import NotFoundError

router = APIRouter(prefix="/activities", tags=["activities"], dependencies=[Depends(require_api_key)])


@router.get("/", response_model=list[ActivityRead])
def list_activities(service: ActivityService = Depends(get_activity_service)) -> list[ActivityRead]:
    return service.get_activity_tree()


@router.get("/search/organizations", response_model=list[OrganizationRead])
def organizations_for_activity_name(
    name: str = Query(..., min_length=2),
    service: ActivityService = Depends(get_activity_service),
):
    try:
        return service.organizations_for_activity_name(name)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{activity_id}/organizations", response_model=list[OrganizationRead])
def organizations_for_activity(
    activity_id: int,
    service: ActivityService = Depends(get_activity_service),
):
    try:
        return service.organizations_for_activity(activity_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
