from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Tuple, Dict
from datetime import datetime

from models import Instance, Solution, Route, RouteLeg, RouteReport
from geo import haversine_km, travel_time_min
from osrm import osrm_route

# Global OSRM cache to avoid repeated API calls
_osrm_cache: Dict[tuple, Tuple[float, float, List]] = {}

def clear_osrm_cache():
    """Clear the OSRM cache - useful for testing or memory management"""
    global _osrm_cache
    _osrm_cache.clear()


@dataclass
class Chromosome:
    # For MVP, each gene is an assignment of (depot_id -> list of vehicle usages with type + passengers)
    # We encode simply as list of (depot_index, passengers_per_vehicle) where capacity is inferred by type choice.
    assignments: List[Tuple[int, int]]  # (depot_index, passengers)


def _evaluate_chromosome(ch: Chromosome, instance: Instance, use_osrm: bool = False, osrm_url: str | None = None) -> Tuple[Solution, float]:
    """Evaluate chromosome by constructing routes sequentially from global remaining demand.
    The chromosome is currently not used for ordering (MVP) to ensure correctness first.
    """
    routes: List[Route] = []
    total_cost = 0.0
    factory = instance.factory
    shift = instance.shifts[0]

    # Global remaining demand per depot index
    remaining: Dict[int, int] = {}
    for i, d in enumerate(instance.depots):
        remaining[i] = d.demand_by_shift.get(shift.id, 0)

    # Build concrete vehicle instances list honoring owned counts; prefer smaller capacity first
    vehicles: List[Tuple[str, int, float, bool]] = []  # (type_id, capacity, cost_per_km, owned)
    for o in sorted(instance.vehicles.owned, key=lambda x: x.capacity):
        for _ in range(o.count):
            vehicles.append((o.type_id, o.capacity, o.cost_per_km, True))
    for r in sorted(instance.vehicles.rented, key=lambda x: x.capacity):
        # Treat rented as one each for now unless counts provided elsewhere
        vehicles.append((r.type_id, r.capacity, r.cost_per_km, False))

    # Helper to compute OSRM segment
    def osrm_segment(a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float, List[Tuple[float, float]]]:
        seg_key = (round(a[0], 6), round(a[1], 6), round(b[0], 6), round(b[1], 6))
        if seg_key in _osrm_cache:
            dist, t, path = _osrm_cache[seg_key]
            print(f"      💾 OSRM cache hit for segment: {dist:.2f}km, {t:.2f}min")
            return dist, t, path
        try:
            print("      🌐 Calling OSRM for segment 2 coords...")
            dist, t, path = osrm_route([a, b], base_url=osrm_url or "http://router.project-osrm.org")
            print(f"      ✅ OSRM returned segment: {dist:.2f}km, {t:.2f}min")
        except Exception as e:
            print(f"      ❌ OSRM failed segment: {e}, falling back")
            dist = haversine_km(a[0], a[1], b[0], b[1])
            t = travel_time_min(dist)
            path = [a, b]
        _osrm_cache[seg_key] = (dist, t, path)
        return dist, t, path

    def any_demand_left() -> bool:
        return any(v > 0 for v in remaining.values())

    # Greedy build routes vehicle by vehicle
    for vtype, capacity, cost_per_km, is_owned in vehicles:
        if not any_demand_left():
            break

        capacity_left = capacity
        used_depots: set[int] = set()
        pickups: List[Tuple[str, int]] = []
        ordered_depot_indices: List[int] = []

        # Choose starting depot: the one with the largest remaining demand
        start_idx = max((i for i in remaining.keys() if remaining[i] > 0), key=lambda i: remaining[i], default=None)
        if start_idx is None:
            break

        current_idx = start_idx
        while capacity_left > 0 and current_idx is not None:
            if remaining[current_idx] <= 0 or current_idx in used_depots:
                break
            take = min(remaining[current_idx], capacity_left)
            if take <= 0:
                break
            pickups.append((instance.depots[current_idx].id, take))
            ordered_depot_indices.append(current_idx)
            used_depots.add(current_idx)
            remaining[current_idx] -= take
            capacity_left -= take
            if capacity_left <= 0:
                break
            # pick next depot: nearest to current_idx among depots with remaining>0 and not visited
            cur = instance.depots[current_idx]
            candidates = [j for j in remaining.keys() if remaining[j] > 0 and j not in used_depots]
            if not candidates:
                current_idx = None
                break
            current_idx = min(candidates, key=lambda j: haversine_km(cur.lat, cur.lon, instance.depots[j].lat, instance.depots[j].lon))

        if not pickups:
            continue

        # Build legs in the depot order to the factory
        waypoints: List[Tuple[float, float]] = [(instance.depots[i].lat, instance.depots[i].lon) for i in ordered_depot_indices]
        node_seq: List[str] = [instance.depots[i].id for i in ordered_depot_indices]
        waypoints.append((factory.lat, factory.lon))
        node_seq.append(factory.id)

        legs: List[RouteLeg] = []
        total_dist = 0.0
        total_time = 0.0
        for (a, b, from_id, to_id) in zip(waypoints[:-1], waypoints[1:], node_seq[:-1], node_seq[1:]):
            if use_osrm:
                seg_dist, seg_time, seg_path = osrm_segment(a, b)
            else:
                seg_dist = haversine_km(a[0], a[1], b[0], b[1])
                seg_time = travel_time_min(seg_dist)
                seg_path = [a, b]
            total_dist += seg_dist
            total_time += seg_time
            legs.append(RouteLeg(from_node=from_id, to_node=to_id, distance_km=seg_dist, time_min=seg_time, path_coords=seg_path))

        # Compute cost (no fixed cost for owned)
        route_cost = total_dist * cost_per_km

        route = Route(
            shift_id=shift.id,
            vehicle_type_id=vtype,
            owned=is_owned,
            seats=capacity,
            passengers=sum(p for _, p in pickups),
            depot_ids=[instance.depots[i].id for i in ordered_depot_indices],
            pickups=pickups,
            legs=legs,
            arrival_time=shift.start_time,
            cost=route_cost,
        )
        routes.append(route)
        total_cost += route_cost

    # Penalize unserved passengers to avoid zero-route solutions being preferred
    total_demand = sum(d.demand_by_shift.get(shift.id, 0) for d in instance.depots)
    served_total = sum(r.passengers for r in routes)
    if served_total < total_demand:
        unserved = total_demand - served_total
        UNASSIGNED_PAX_PENALTY = 1000  # Strong penalty but not astronomically large
        penalty_cost = unserved * UNASSIGNED_PAX_PENALTY
        print(f"      🚨 Penalizing unserved passengers: {unserved} -> +{penalty_cost:.2f}")
        total_cost += penalty_cost

    return Solution(routes=routes, total_cost=total_cost), total_cost


def _generate_reports(solution: Solution, instance: Instance) -> Solution:
    """Generate detailed reports for each route and validate constraints."""
    reports = []
    violations = []
    depot_leftovers = {}
    
    # Initialize depot leftovers
    for depot in instance.depots:
        depot_leftovers[depot.id] = depot.demand_by_shift.get(instance.shifts[0].id, 0)
    
    # Track depot visits per vehicle
    depot_visits = {}  # {vehicle_id: set of depot_ids}
    
    for idx, route in enumerate(solution.routes):
        vehicle_id = f"V{idx+1}"
        depot_visits[vehicle_id] = set()
        
        # Check for duplicate depot visits
        if len(route.depot_ids) != len(set(route.depot_ids)):
            violations.append(f"Vehicle {vehicle_id} visits same depot multiple times: {route.depot_ids}")
        
        # Calculate route metrics
        total_time = sum(leg.time_min for leg in route.legs)
        total_cost = route.cost
        passengers = route.passengers
        empty_seats = route.seats - passengers
        
        # Update depot leftovers using per-depot pickups
        for depot_id, taken in route.pickups:
            before = depot_leftovers.get(depot_id, 0)
            depot_leftovers[depot_id] = max(0, before - taken)
            depot_visits[vehicle_id].add(depot_id)
        
        # Create depot visit details
        depot_visits_detail = []
        for i, (depot_id, taken) in enumerate(route.pickups):
            leg = route.legs[min(i, len(route.legs) - 1)]
            depot_visits_detail.append({
                "depot_id": depot_id,
                "passengers": taken,
                "time_min": leg.time_min,
                "cost": leg.distance_km * (50 if route.owned else 50)  # Simplified cost calculation
            })
        
        # Check for violations
        route_violations = []
        if empty_seats < 0:
            route_violations.append("over_capacity")
        if total_time > instance.shifts[0].max_ride_minutes:
            route_violations.append("exceeds_ride_time")
        
        report = RouteReport(
            vehicle_id=vehicle_id,
            vehicle_type=route.vehicle_type_id,
            shift_id=route.shift_id,
            passengers_carried=passengers,
            empty_seats=empty_seats,
            total_trip_time_min=total_time,
            total_trip_cost=total_cost,
            depot_visits=depot_visits_detail,
            violations=route_violations
        )
        reports.append(report)
    
    # Check for duplicate depot visits across vehicles
    for depot_id, remaining in depot_leftovers.items():
        if remaining > 0:
            violations.append(f"Depot {depot_id} has {remaining} unserved passengers")
    
    solution.reports = reports
    solution.depot_leftovers = depot_leftovers
    solution.violations = violations
    
    return solution


def _seed_population(instance: Instance, pop_size: int) -> List[Chromosome]:
    chromos: List[Chromosome] = []
    shift = instance.shifts[0]
    
    print(f"   Seeding {pop_size} chromosomes...", flush=True)
    
    for chromo_idx in range(pop_size):
        print(f"   Creating chromosome {chromo_idx + 1}/{pop_size}...", flush=True)
        assignments: List[Tuple[int, int]] = []
        
        # Get all depots with demand
        depots_with_demand = []
        for i, d in enumerate(instance.depots):
            demand = d.demand_by_shift.get(shift.id, 0)
            if demand > 0:
                depots_with_demand.append((i, demand))
        
        print(f"     Found {len(depots_with_demand)} depots with demand", flush=True)
        
        # Create assignments that encourage multi-depot routing
        remaining_demand = {i: demand for i, demand in depots_with_demand}
        
        # Try to create efficient multi-depot assignments
        iteration = 0
        max_iterations = 100  # Safety check to prevent infinite loops
        while any(remaining_demand.values()) and iteration < max_iterations:
            iteration += 1
            print(f"     Iteration {iteration}: remaining demand = {remaining_demand}", flush=True)
            
            # Find the smallest remaining demand
            min_demand = min(remaining_demand.values())
            print(f"     Min demand: {min_demand}", flush=True)
            
            # Find best vehicle type for this demand
            best_vehicle = None
            for o in sorted(instance.vehicles.owned, key=lambda x: x.capacity):
                if o.capacity >= min_demand:
                    best_vehicle = o
                    break
            if best_vehicle is None and instance.vehicles.rented:
                for r in sorted(instance.vehicles.rented, key=lambda x: x.capacity):
                    if r.capacity >= min_demand:
                        best_vehicle = r
                        break
            
            if best_vehicle:
                # Try to fill this vehicle with multiple depots
                current_passengers = 0
                assigned_depots = []
                
                # Sort depots by distance from factory for efficient routing
                factory_coords = (instance.factory.lat, instance.factory.lon)
                depot_distances = []
                for i, demand in remaining_demand.items():
                    if demand > 0:
                        depot = instance.depots[i]
                        dist = haversine_km(depot.lat, depot.lon, factory_coords[0], factory_coords[1])
                        depot_distances.append((i, demand, dist))
                
                depot_distances.sort(key=lambda x: x[2])  # Sort by distance
                
                # Fill vehicle with nearby depots
                for i, demand, dist in depot_distances:
                    if current_passengers + demand <= best_vehicle.capacity:
                        assigned_depots.append((i, demand))
                        current_passengers += demand
                        remaining_demand[i] = 0
                    else:
                        # Take what fits
                        can_take = best_vehicle.capacity - current_passengers
                        if can_take > 0:
                            assigned_depots.append((i, can_take))
                            current_passengers += can_take
                            remaining_demand[i] -= can_take
                        break
                
                # Create assignments for this vehicle
                for depot_idx, pax in assigned_depots:
                    assignments.append((depot_idx, pax))
            else:
                # No suitable vehicle, use largest available
                if instance.vehicles.owned:
                    largest = max(instance.vehicles.owned, key=lambda x: x.capacity)
                    for i, demand in remaining_demand.items():
                        if demand > 0:
                            passengers_to_take = min(demand, largest.capacity)
                            assignments.append((i, passengers_to_take))
                            remaining_demand[i] -= passengers_to_take
                            break
                elif instance.vehicles.rented:
                    largest = max(instance.vehicles.rented, key=lambda x: x.capacity)
                    for i, demand in remaining_demand.items():
                        if demand > 0:
                            passengers_to_take = min(demand, largest.capacity)
                            assignments.append((i, passengers_to_take))
                            remaining_demand[i] -= passengers_to_take
                            break
                else:
                    break  # No vehicles available
        
        random.shuffle(assignments)
        chromos.append(Chromosome(assignments))
    
    return chromos


def _crossover(a: Chromosome, b: Chromosome) -> Chromosome:
    cut = random.randint(0, len(a.assignments))
    child_assign = a.assignments[:cut] + [g for g in b.assignments if g not in a.assignments[:cut]]
    return Chromosome(child_assign)


def _mutate(ch: Chromosome, instance: Instance, rate: float = 0.2) -> None:
    shift = instance.shifts[0]
    for idx in range(len(ch.assignments)):
        if random.random() < rate:
            depot_idx, pax = ch.assignments[idx]
            # tweak passengers by ±10% bounded [1, demand]
            demand = instance.depots[depot_idx].demand_by_shift.get(shift.id, pax)
            delta = max(1, int(0.1 * pax))
            new_pax = max(1, min(demand, pax + random.choice([-delta, delta])))
            ch.assignments[idx] = (depot_idx, new_pax)


def solve_ga(instance: Instance, pop_size: int = 20, generations: int = 60, mutation_rate: float = 0.2, use_osrm: bool = False, osrm_url: str | None = None) -> Solution:
    print(f"🚀 Starting GA: pop_size={pop_size}, generations={generations}, use_osrm={use_osrm}", flush=True)
    
    # Clear OSRM cache at start of each run
    if use_osrm:
        clear_osrm_cache()
        print("🧹 Cleared OSRM cache", flush=True)
    
    print("📊 Seeding population...", flush=True)
    print(f"   Instance has {len(instance.depots)} depots", flush=True)
    print(f"   Instance has {len(instance.vehicles.owned)} owned vehicle types", flush=True)
    print(f"   Instance has {len(instance.vehicles.rented)} rented vehicle types", flush=True)
    
    population = _seed_population(instance, pop_size)
    print(f"✅ Created {len(population)} chromosomes", flush=True)
    
    best_sol: Solution | None = None
    best_cost = float("inf")

    for gen in range(generations):
        print(f"\n🔄 Generation {gen + 1}/{generations}")
        
        # Evaluate
        print("🔍 Evaluating population...")
        scored = []
        for i, ch in enumerate(population):
            print(f"  📝 Evaluating chromosome {i+1}/{len(population)} (assignments: {len(ch.assignments)})")
            sol, cost = _evaluate_chromosome(ch, instance, use_osrm=use_osrm, osrm_url=osrm_url)
            scored.append((ch, sol, cost))
            print(f"    💰 Cost: {cost:.2f}, Routes: {len(sol.routes)}")
            if cost < best_cost:
                best_cost, best_sol = cost, sol
                print(f"    🏆 New best cost: {best_cost:.2f}")

        print(f"📈 Best cost so far: {best_cost:.2f}")

        # Selection (tournament of size 3)
        print("🎯 Selection and reproduction...")
        def tournament() -> Chromosome:
            cand = random.sample(scored, k=min(3, len(scored)))
            cand.sort(key=lambda x: x[2])
            return cand[0][0]

        new_pop: List[Chromosome] = []
        while len(new_pop) < pop_size:
            p1, p2 = tournament(), tournament()
            child = _crossover(p1, p2)
            _mutate(child, instance, mutation_rate)
            new_pop.append(child)
        population = new_pop
        print(f"✅ Created new population of {len(population)} chromosomes")

    print(f"\n🏁 GA completed! Final best cost: {best_cost:.2f}")
    assert best_sol is not None
    
    # Show cache statistics
    if use_osrm:
        print(f"📊 OSRM cache: {len(_osrm_cache)} unique routes cached")
    
    print("📋 Generating reports...")
    # Generate detailed reports
    best_sol = _generate_reports(best_sol, instance)
    print("✅ Reports generated")
    
    return best_sol


