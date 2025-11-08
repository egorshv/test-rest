from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Building, Organization


class BuildingDAO:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Building]:
        stmt = select(Building).order_by(Building.id)
        return list(self.db.scalars(stmt).all())

    def get(self, building_id: int) -> Building | None:
        return self.db.get(Building, building_id)

    def organizations_in_building(self, building_id: int) -> list[Organization]:
        stmt = (
            select(Organization)
            .options(
                selectinload(Organization.activities),
                selectinload(Organization.phones),
                selectinload(Organization.building),
            )
            .where(Organization.building_id == building_id)
            .order_by(Organization.name)
        )
        return list(self.db.scalars(stmt).all())
