from __future__ import annotations

from typing import List, Tuple
from datetime import datetime, timedelta

from models import Instance, Solution, Route, RouteLeg, VehicleTypeId


def _parse_time(hhmm: str) -> datetime:
    return datetime.strptime(hhmm, "%H:%M")


def _format_time(t: datetime) -> str:
    return t.strftime("%H:%M")


def _find_best_vehicle_for_load(instance: Instance, load: int) -> Tuple[VehicleTypeId, bool, int, float]:
    """Return (vehicle_type_id, owned, capacity, fixed_cost).

    Preference: use owned if capacity >= load and available; otherwise rented minimal capacity >= load.
    For MVP, we ignore owned availability per shift and just prefer owned types first by capacity fit.
    """
    # Try owned types sorted by capacity ascending
    owned_sorted = sorted(instance.vehicles.owned, key=lambda o: o.capacity)
    for o in owned_sorted:
        if o.capacity >= load:
            return o.type_id, True, o.capacity, 0.0
    # Fallback to rented
    rented_sorted = sorted(instance.vehicles.rented, key=lambda r: r.capacity)
    for r in rented_sorted:
        if r.capacity >= load:
            return r.type_id, False, r.capacity, r.fixed_rental_cost
    # If none large enough, pick the largest rented and let caller split externally
    if rented_sorted:
        r = rented_sorted[-1]
        return r.type_id, False, r.capacity, r.fixed_rental_cost
    # Or largest owned as last resort
    if owned_sorted:
        o = owned_sorted[-1]
        return o.type_id, True, o.capacity, 0.0
    raise ValueError("No vehicles defined")


def solve_baseline(instance: Instance) -> Solution:
    routes: List[Route] = []
    total_cost = 0.0
    factory_id = instance.factory.id
    shifts_by_id = {s.id: s for s in instance.shifts}

    for shift in instance.shifts:
        shift_start = _parse_time(shift.start_time)
        for depot in instance.depots:
            demand = depot.demand_by_shift.get(shift.id, 0)
            if demand <= 0:
                continue
            remaining = demand
            while remaining > 0:
                vtype, owned, capacity, fixed = _find_best_vehicle_for_load(instance, remaining)
                passengers = min(capacity, remaining)

                dist = float(instance.distances_km[depot.id][factory_id])
                time_min = float(instance.times_min[depot.id][factory_id])

                # Compute departure to arrive just at shift start
                arrival_time = shift_start
                ride_time_td = timedelta(minutes=time_min)
                # For direct trip, earliest passenger ride time equals time_min
                if time_min > shift.max_ride_minutes:
                    # Mark infeasible by skipping; in real system we'd split differently or flag
                    # Here we still create the route but it's up to downstream to adjust
                    pass

                # Cost per km lookup
                per_km = None
                if owned:
                    per_km = next(o.cost_per_km for o in instance.vehicles.owned if o.type_id == vtype)
                else:
                    per_km = next(r.cost_per_km for r in instance.vehicles.rented if r.type_id == vtype)
                variable_cost = dist * per_km
                route_cost = fixed + variable_cost

                leg = RouteLeg(from_node=depot.id, to_node=factory_id, distance_km=dist, time_min=time_min)
                route = Route(
                    shift_id=shift.id,
                    vehicle_type_id=vtype,
                    owned=owned,
                    seats=capacity,
                    passengers=passengers,
                    depot_ids=[depot.id],
                    legs=[leg],
                    arrival_time=_format_time(arrival_time),
                    cost=route_cost,
                )
                routes.append(route)
                total_cost += route_cost
                remaining -= passengers

    return Solution(routes=routes, total_cost=total_cost)


