from app.dao import BuildingDAO, OrganizationDAO
from app.services.exceptions import NotFoundError


class BuildingService:
    def __init__(self, building_dao: BuildingDAO, organization_dao: OrganizationDAO):
        self.building_dao = building_dao
        self.organization_dao = organization_dao

    def list_buildings(self):
        return self.building_dao.list_all()

    def organizations_in_building(self, building_id: int):
        building = self.building_dao.get(building_id)
        if not building:
            raise NotFoundError("Building not found")
        return self.organization_dao.list_by_building(building_id)
