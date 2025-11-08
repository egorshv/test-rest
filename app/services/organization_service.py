from app.dao import OrganizationDAO
from app.services.exceptions import NotFoundError, ValidationError
from app.services.geo import approximate_bounding_box, haversine_km


class OrganizationService:
    def __init__(self, organization_dao: OrganizationDAO):
        self.organization_dao = organization_dao

    def get_organization(self, organization_id: int):
        organization = self.organization_dao.get(organization_id)
        if not organization:
            raise NotFoundError("Organization not found")
        return organization

    def search_organizations(self, query: str, limit: int):
        return self.organization_dao.search_by_name(query, limit)

    def organizations_nearby(
        self,
        latitude: float,
        longitude: float,
        *,
        radius_km: float | None,
        min_latitude: float | None,
        max_latitude: float | None,
        min_longitude: float | None,
        max_longitude: float | None,
        limit: int,
    ):
        if radius_km is None:
            if None in {min_latitude, max_latitude, min_longitude, max_longitude}:
                raise ValidationError("Provide either radius_km or full rectangular bounds.")
        else:
            min_latitude, max_latitude, min_longitude, max_longitude = approximate_bounding_box(
                latitude, longitude, radius_km
            )

        limit_multiplier = 5 if radius_km is not None else 1
        candidates = self.organization_dao.list_in_rectangle(
            min_latitude,
            max_latitude,
            min_longitude,
            max_longitude,
            limit * limit_multiplier,
        )

        if radius_km is None:
            return candidates[:limit]

        filtered = []
        for organization in candidates:
            distance = haversine_km(
                latitude,
                longitude,
                organization.building.latitude,
                organization.building.longitude,
            )
            if distance <= radius_km:
                filtered.append(organization)
            if len(filtered) >= limit:
                break
        return filtered
