from __future__ import annotations

import math


EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def travel_time_min(distance_km: float, avg_speed_kmh: float = 30.0) -> float:
    if avg_speed_kmh <= 0:
        raise ValueError("avg_speed_kmh must be positive")
    return (distance_km / avg_speed_kmh) * 60.0


