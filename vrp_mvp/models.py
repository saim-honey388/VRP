from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, validator


NodeId = str
ShiftId = str
VehicleTypeId = str


class Depot(BaseModel):
    id: NodeId
    name: str
    lat: float
    lon: float
    demand_by_shift: Dict[ShiftId, int] = Field(default_factory=dict)


class Factory(BaseModel):
    id: NodeId
    name: str
    lat: float
    lon: float


class Shift(BaseModel):
    id: ShiftId
    start_time: str  # HH:MM
    max_ride_minutes: int


class OwnedVehicleType(BaseModel):
    type_id: VehicleTypeId
    capacity: int
    cost_per_km: float
    count: int


class RentedVehicleType(BaseModel):
    type_id: VehicleTypeId
    capacity: int
    cost_per_km: float
    fixed_rental_cost: float


class Fleet(BaseModel):
    owned: List[OwnedVehicleType] = Field(default_factory=list)
    rented: List[RentedVehicleType] = Field(default_factory=list)

    def max_capacity(self) -> int:
        total = 0
        for o in self.owned:
            total += o.capacity * o.count
        # Assume arbitrary number of rentals available in MVP; capacity here is unbounded by rentals
        return total


class Instance(BaseModel):
    depots: List[Depot]
    factory: Factory
    shifts: List[Shift]
    vehicles: Fleet
    distances_km: Optional[Dict[NodeId, Dict[NodeId, float]]] = None
    times_min: Optional[Dict[NodeId, Dict[NodeId, float]]] = None

    @validator("times_min")
    def ensure_nodes_present(cls, v, values):  # type: ignore[override]
        if v is None:
            return v
        node_ids = {d.id for d in values.get("depots", [])}
        factory: Optional[Factory] = values.get("factory")
        if factory:
            node_ids.add(factory.id)
        for a, m in v.items():
            if a not in node_ids:
                raise ValueError(f"Unknown node in times_min: {a}")
            for b in m.keys():
                if b not in node_ids:
                    raise ValueError(f"Unknown node in times_min row {a}: {b}")
        return v


class RouteLeg(BaseModel):
    from_node: NodeId
    to_node: NodeId
    distance_km: float
    time_min: float
    path_coords: Optional[List[Tuple[float, float]]] = None  # [(lat, lon), ...]


class Route(BaseModel):
    shift_id: ShiftId
    vehicle_type_id: VehicleTypeId
    owned: bool
    seats: int
    passengers: int
    depot_ids: List[NodeId]
    # Ordered pickups with per-depot passenger counts for accurate accounting
    pickups: List[Tuple[NodeId, int]] = Field(default_factory=list)
    legs: List[RouteLeg]
    arrival_time: str  # HH:MM at factory
    cost: float


class RouteReport(BaseModel):
    vehicle_id: str
    vehicle_type: str
    shift_id: str
    passengers_carried: int
    empty_seats: int
    total_trip_time_min: float
    total_trip_cost: float
    depot_visits: List[dict] = Field(default_factory=list)  # [{"depot_id": str, "passengers": int, "time_min": float, "cost": float}]
    violations: List[str] = Field(default_factory=list)  # ["duplicate_depot", "over_capacity", etc.]


class Solution(BaseModel):
    routes: List[Route] = Field(default_factory=list)
    total_cost: float = 0.0
    reports: List[RouteReport] = Field(default_factory=list)
    depot_leftovers: dict = Field(default_factory=dict)  # {depot_id: remaining_demand}
    violations: List[str] = Field(default_factory=list)


