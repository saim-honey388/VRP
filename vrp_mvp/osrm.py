from __future__ import annotations

from typing import List, Tuple
import requests
import polyline


def osrm_route(coords: List[Tuple[float, float]], base_url: str = "http://router.project-osrm.org") -> tuple[float, float, list[tuple[float, float]]]:
    """Query OSRM for a route through given coords [(lat, lon), ...]. Returns (distance_km, time_min, path_coords).
    Uses the public demo server by default; for production, run your own OSRM.
    """
    if len(coords) < 2:
        return 0.0, 0.0, coords
    # OSRM expects lon,lat; profile driving
    loc = ";".join(f"{lon},{lat}" for lat, lon in coords)
    url = f"{base_url}/route/v1/driving/{loc}?overview=full&geometries=polyline6"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    if not data.get("routes"):
        raise RuntimeError(f"OSRM returned no routes: {data}")
    route = data["routes"][0]
    dist_km = route["distance"] / 1000.0
    time_min = route["duration"] / 60.0
    coords_path = polyline.decode(route["geometry"], precision=6)
    # decoded: list of (lat, lon)
    return dist_km, time_min, [(lat, lon) for lat, lon in coords_path]


