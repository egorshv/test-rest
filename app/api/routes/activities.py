from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.api.utils import organization_with_relationships_stmt
from app.models import Activity, Organization
from app.schemas.activity import ActivityRead
from app.schemas.organization import OrganizationRead
from app.services.activity_service import (
    fetch_activity_descendant_ids,
    fetch_activity_tree,
    find_activity_by_name,
)

router = APIRouter(prefix="/activities", tags=["activities"], dependencies=[Depends(require_api_key)])


@router.get("/", response_model=list[ActivityRead])
def list_activities(db: Session = Depends(get_db)) -> list[ActivityRead]:
    return fetch_activity_tree(db)


def _organizations_by_activity_stmt(activity_ids: list[int]) -> Select[Organization]:
    stmt = organization_with_relationships_stmt().where(
        Organization.activities.any(Activity.id.in_(activity_ids))
    )
    return stmt


@router.get("/search/organizations", response_model=list[OrganizationRead])
def organizations_for_activity_name(
    name: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
) -> list[Organization]:
    activity = find_activity_by_name(db, name)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    descendant_ids = fetch_activity_descendant_ids(db, activity.id)
    stmt = _organizations_by_activity_stmt(descendant_ids)
    return list(db.scalars(stmt).all())


@router.get("/{activity_id}/organizations", response_model=list[OrganizationRead])
def organizations_for_activity(activity_id: int, db: Session = Depends(get_db)) -> list[Organization]:
    descendant_ids = fetch_activity_descendant_ids(db, activity_id)
    if not descendant_ids:
        raise HTTPException(status_code=404, detail="Activity not found")
    stmt = _organizations_by_activity_stmt(descendant_ids)
    return list(db.scalars(stmt).all())
