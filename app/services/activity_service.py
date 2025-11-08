from __future__ import annotations

from collections import defaultdict, deque

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Activity
from app.schemas.activity import ActivityRead


def fetch_activity_descendant_ids(db: Session, root_activity_id: int) -> list[int]:
    activities = db.scalars(select(Activity)).all()
    if root_activity_id not in {activity.id for activity in activities}:
        return []

    adjacency: dict[int | None, list[Activity]] = defaultdict(list)
    for activity in activities:
        adjacency[activity.parent_id].append(activity)

    descendants: list[int] = []
    queue: deque[int] = deque([root_activity_id])

    while queue:
        current_id = queue.popleft()
        descendants.append(current_id)
        for child in adjacency[current_id]:
            queue.append(child.id)

    return descendants


def find_activity_by_name(db: Session, name: str) -> Activity | None:
    stmt = select(Activity).where(func.lower(Activity.name) == func.lower(name.strip()))
    return db.scalar(stmt)


def fetch_activity_tree(db: Session) -> list[ActivityRead]:
    activities = db.scalars(select(Activity).order_by(Activity.level, Activity.name)).all()
    adjacency: dict[int | None, list[Activity]] = defaultdict(list)
    for activity in activities:
        adjacency[activity.parent_id].append(activity)

    return [_serialize_activity_tree(node, adjacency) for node in adjacency[None]]


def _serialize_activity_tree(activity: Activity, adjacency: dict[int | None, list[Activity]]) -> ActivityRead:
    children = [_serialize_activity_tree(child, adjacency) for child in adjacency.get(activity.id, [])]
    return ActivityRead.model_validate(
        {
            "id": activity.id,
            "name": activity.name,
            "parent_id": activity.parent_id,
            "level": activity.level,
            "children": children or None,
        }
    )
