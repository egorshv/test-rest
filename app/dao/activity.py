from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Activity


class ActivityDAO:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Activity]:
        stmt = select(Activity).order_by(Activity.level, Activity.name)
        return list(self.db.scalars(stmt).all())

    def get(self, activity_id: int) -> Activity | None:
        return self.db.get(Activity, activity_id)

    def find_by_name(self, name: str) -> Activity | None:
        stmt = select(Activity).where(func.lower(Activity.name) == func.lower(name.strip()))
        return self.db.scalar(stmt)
