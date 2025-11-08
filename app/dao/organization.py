from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Activity, Building, Organization


class OrganizationDAO:
    def __init__(self, db: Session):
        self.db = db

    def _base_stmt(self) -> Select[Organization]:
        return (
            select(Organization)
            .options(
                selectinload(Organization.activities),
                selectinload(Organization.phones),
                selectinload(Organization.building),
            )
            .join(Organization.building)
            .order_by(Organization.name)
        )

    def get(self, organization_id: int) -> Organization | None:
        stmt = self._base_stmt().where(Organization.id == organization_id)
        return self.db.scalar(stmt)

    def search_by_name(self, query: str, limit: int) -> list[Organization]:
        normalized = query.strip()
        stmt = (
            self._base_stmt()
            .where(func.lower(Organization.name).contains(func.lower(normalized)))
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def list_by_building(self, building_id: int) -> list[Organization]:
        stmt = self._base_stmt().where(Organization.building_id == building_id)
        return list(self.db.scalars(stmt).all())

    def list_by_activity_ids(self, activity_ids: list[int]) -> list[Organization]:
        stmt = self._base_stmt().where(Organization.activities.any(Activity.id.in_(activity_ids)))
        return list(self.db.scalars(stmt).all())

    def list_in_rectangle(
        self,
        min_latitude: float,
        max_latitude: float,
        min_longitude: float,
        max_longitude: float,
        limit: int,
    ) -> list[Organization]:
        stmt = (
            self._base_stmt()
            .where(
                Building.latitude >= min_latitude,
                Building.latitude <= max_latitude,
                Building.longitude >= min_longitude,
                Building.longitude <= max_longitude,
            )
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
