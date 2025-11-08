from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def approximate_bounding_box(lat: float, lon: float, radius_km: float) -> tuple[float, float, float, float]:
    lat_delta = (radius_km / EARTH_RADIUS_KM) * 180 / 3.141592653589793
    lon_delta = lat_delta / max(cos(radians(lat)), 0.000001)
    return lat - lat_delta, lat + lat_delta, lon - lon_delta, lon + lon_delta
