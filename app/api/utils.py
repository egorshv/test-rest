from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from app.models import Organization


def organization_with_relationships_stmt() -> Select[Organization]:
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
