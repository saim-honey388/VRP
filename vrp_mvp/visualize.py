from __future__ import annotations

import folium
from typing import Tuple

from .models import Instance, Solution


def render_map(solution: Solution, instance: Instance, out_html: str) -> None:
    # center on factory (we'll fit to bounds later)
    m = folium.Map(location=[instance.factory.lat, instance.factory.lon], zoom_start=11)

    # markers
    folium.Marker(
        [instance.factory.lat, instance.factory.lon],
        popup=f"Factory {instance.factory.name}",
        icon=folium.Icon(color="red", icon="industry", prefix="fa"),
    ).add_to(m)

    depot_lookup = {d.id: d for d in instance.depots}

    colors = [
        "blue", "green", "purple", "orange", "darkred", "lightred", "beige",
        "darkblue", "darkgreen", "cadetblue", "darkpurple", "white", "pink",
        "lightblue", "lightgreen", "gray", "black", "lightgray",
    ]

    all_coords: list[tuple[float, float]] = []
    for idx, route in enumerate(solution.routes):
        color = colors[idx % len(colors)]
        dep_id = route.depot_ids[0]
        d = depot_lookup[dep_id]
        folium.Marker([d.lat, d.lon], popup=f"Depot {d.name}\nPax {route.passengers}").add_to(m)
        path = None
        if route.legs and route.legs[0].path_coords:
            path = route.legs[0].path_coords
        else:
            path = [(d.lat, d.lon), (instance.factory.lat, instance.factory.lon)]
        all_coords.extend(path)
        # Enhanced tooltip with detailed info
        empty_seats = route.seats - route.passengers
        total_time = sum(leg.time_min for leg in route.legs)
        tooltip_text = f"""
        <b>Vehicle {route.vehicle_type_id}</b><br>
        Route: {dep_id} → {instance.factory.id}<br>
        Passengers: {route.passengers}/{route.seats} (Empty: {empty_seats})<br>
        Time: {total_time:.1f} min<br>
        Cost: ${route.cost:.2f}<br>
        Distance: {route.legs[0].distance_km:.1f} km
        """
        folium.PolyLine(locations=path, color=color, weight=4, opacity=0.7,
                        tooltip=tooltip_text).add_to(m)

    # Fit map to all route coordinates if available
    if all_coords:
        lats = [lat for lat, _ in all_coords]
        lons = [lon for _, lon in all_coords]
        south, north = min(lats), max(lats)
        west, east = min(lons), max(lons)
        # add small padding if degenerate
        if south == north:
            south -= 0.005; north += 0.005
        if west == east:
            west -= 0.005; east += 0.005
        folium.FitBounds([[south, west], [north, east]]).add_to(m)

    m.save(out_html)


