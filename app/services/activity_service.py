from __future__ import annotations

from collections import defaultdict, deque

from app.dao import ActivityDAO, OrganizationDAO
from app.models import Activity
from app.schemas.activity import ActivityRead
from app.services.exceptions import NotFoundError


class ActivityService:
    def __init__(self, activity_dao: ActivityDAO, organization_dao: OrganizationDAO):
        self.activity_dao = activity_dao
        self.organization_dao = organization_dao

    def get_activity_tree(self) -> list[ActivityRead]:
        activities = self.activity_dao.list_all()
        adjacency = self._build_adjacency(activities)
        return [self._serialize_activity_tree(node, adjacency) for node in adjacency[None]]

    def organizations_for_activity(self, activity_id: int):
        activities = self.activity_dao.list_all()
        descendant_ids = self._descendant_ids(activities, activity_id)
        if not descendant_ids:
            raise NotFoundError("Activity not found")
        return self.organization_dao.list_by_activity_ids(descendant_ids)

    def organizations_for_activity_name(self, name: str):
        activity = self.activity_dao.find_by_name(name)
        if not activity:
            raise NotFoundError("Activity not found")
        return self.organizations_for_activity(activity.id)

    @staticmethod
    def _build_adjacency(activities: list[Activity]) -> dict[int | None, list[Activity]]:
        adjacency: dict[int | None, list[Activity]] = defaultdict(list)
        for activity in activities:
            adjacency[activity.parent_id].append(activity)
        return adjacency

    def _descendant_ids(self, activities: list[Activity], root_activity_id: int) -> list[int]:
        if root_activity_id not in {activity.id for activity in activities}:
            return []

        adjacency = self._build_adjacency(activities)
        descendants: list[int] = []
        queue: deque[int] = deque([root_activity_id])

        while queue:
            current_id = queue.popleft()
            descendants.append(current_id)
            for child in adjacency[current_id]:
                queue.append(child.id)

        return descendants

    def _serialize_activity_tree(self, activity: Activity, adjacency: dict[int | None, list[Activity]]) -> ActivityRead:
        children = [self._serialize_activity_tree(child, adjacency) for child in adjacency.get(activity.id, [])]
        return ActivityRead.model_validate(
            {
                "id": activity.id,
                "name": activity.name,
                "parent_id": activity.parent_id,
                "level": activity.level,
                "children": children or None,
            }
        )
