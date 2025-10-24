import sys
import os
# Add VRP module to Python path
vrp_path = os.path.join(os.path.dirname(__file__), '..', 'vrp_mvp')
if vrp_path not in sys.path:
    sys.path.insert(0, vrp_path)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import asyncio
import math
from datetime import datetime

# Import VRP modules at the top level
try:
    from solver import solve_baseline  # type: ignore
    from ga_solver import solve_ga  # type: ignore
    from models import Instance, Depot, Factory, Shift, OwnedVehicleType, RentedVehicleType, Fleet  # type: ignore
    VRP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: VRP modules not available: {e}")
    VRP_AVAILABLE = False

def sanitize_floats(obj):
    """Recursively sanitize float values to be JSON compliant"""
    if isinstance(obj, dict):
        return {k: sanitize_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_floats(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj):
            return 0.0
        elif math.isinf(obj):
            return 999999.0 if obj > 0 else -999999.0
        else:
            return obj
    else:
        return obj

app = FastAPI(title="VRP Optimizer API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Location(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    type: str  # 'depot', 'pickup', 'delivery'
    demand: int = 0

class VehicleType(BaseModel):
    id: str
    name: str
    type: str  # 'owned' or 'rented'
    capacity: int
    costPerKm: float
    maxDistance: float | None = None
    count: int | None = None
    fixedRentalCost: float | None = None

class TimeWindow(BaseModel):
    id: str
    name: str
    start: str
    end: str
    demandMultiplier: float
    durationMin: int | None = None

class OptimizationRequest(BaseModel):
    locations: List[Location]
    vehicleTypes: List[VehicleType]
    timeWindows: List[TimeWindow] | None = None
    algorithmSettings: Dict[str, Any]
    constraints: Dict[str, Any] | None = None

class Route(BaseModel):
    id: str
    vehicleId: str
    vehicleType: str
    stops: List[Dict[str, Any]]
    totalDistance: float
    totalTime: float
    totalCost: float
    capacity: int
    violations: List[str]

class OptimizationResult(BaseModel):
    id: str
    status: str
    progress: int
    currentGeneration: int
    bestFitness: float
    totalCost: float
    totalDistance: float
    routes: List[Route]
    violations: List[Dict[str, Any]]
    logs: List[Dict[str, Any]]

# Store for active optimizations
active_optimizations: Dict[str, OptimizationResult] = {}

@app.get("/")
async def root():
    return {"message": "VRP Optimizer API", "status": "running"}

@app.get("/test-vrp")
async def test_vrp():
    """Test VRP module functionality"""
    try:
        print("🧪 Testing VRP module...", flush=True)
        
        if not VRP_AVAILABLE:
            return {"message": "VRP modules not available", "status": "error"}
        
        print("✅ All VRP imports successful", flush=True)
        return {"message": "VRP module test successful", "status": "ok"}
    except Exception as e:
        print(f"❌ VRP module test failed: {e}", flush=True)
        return {"message": f"VRP module test failed: {str(e)}", "status": "error"}

@app.post("/optimize", response_model=OptimizationResult)
async def start_optimization(request: OptimizationRequest):
    """Start a new optimization process"""
    optimization_id = f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create initial result
    result = OptimizationResult(
        id=optimization_id,
        status="running",
        progress=0,
        currentGeneration=0,
        bestFitness=999999.0,  # Use large number instead of float('inf')
        totalCost=0.0,
        totalDistance=0.0,
        routes=[],
        violations=[],
        logs=[
            {
                "timestamp": datetime.now().isoformat(),
                "level": "info",
                "message": f"Optimization {optimization_id} started with {len(request.locations)} locations and {sum(vt.count for vt in request.vehicleTypes)} vehicles"
            }
        ]
    )
    
    active_optimizations[optimization_id] = result
    
    # Start optimization in background
    print(f"🚀 Starting optimization task: {optimization_id}", flush=True)
    print(f"📊 Request data: {len(request.locations)} locations, {len(request.vehicleTypes)} vehicle types", flush=True)
    asyncio.create_task(run_optimization(optimization_id, request))
    
    return sanitize_floats(result.model_dump())

@app.get("/optimize/{optimization_id}", response_model=OptimizationResult)
async def get_optimization_status(optimization_id: str):
    """Get the current status of an optimization"""
    if optimization_id not in active_optimizations:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    return sanitize_floats(active_optimizations[optimization_id].model_dump())

@app.get("/optimize/{optimization_id}/stop")
async def stop_optimization(optimization_id: str):
    """Stop a running optimization"""
    if optimization_id not in active_optimizations:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    active_optimizations[optimization_id].status = "stopped"
    return {"message": "Optimization stopped"}

async def run_optimization(optimization_id: str, request: OptimizationRequest):
    """Run actual VRP optimization using vrp_mvp solver"""
    print(f"🔄 run_optimization called for {optimization_id}", flush=True)
    result = active_optimizations[optimization_id]
    
    try:
        # Test VRP module import
        print("🔍 Testing VRP module imports...", flush=True)
        if not VRP_AVAILABLE:
            print("❌ VRP modules not available", flush=True)
            raise ImportError("VRP modules not available")
        print("✅ VRP module imports successful", flush=True)
        
        result.logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": "info",
            "message": "Converting frontend data to VRP instance format..."
        })
        
        print("🔍 DEBUG: Received request data:", flush=True)
        print(f"   Locations: {len(request.locations)}", flush=True)
        for loc in request.locations:
            print(f"     - {loc.name}: {loc.demand} passengers, type: {loc.type}", flush=True)
        print(f"   Vehicle Types: {len(request.vehicleTypes)}", flush=True)
        for vt in request.vehicleTypes:
            print(f"     - {vt.name}: {vt.count} vehicles, capacity {vt.capacity}", flush=True)
        
        # Convert frontend data to VRP instance format
        # Find factory from locations (type='factory')
        factory_location = next((loc for loc in request.locations if loc.type == 'factory'), None)
        if not factory_location:
            raise ValueError("No factory location found in request")
        
        factory = Factory(
            id="factory",
            name=factory_location.name,
            lat=factory_location.lat,
            lon=factory_location.lng
        )
        
        # Create depots with demand per shift id
        depots = []
        for loc in request.locations:
            if loc.type == "depot":
                demand_by_shift: Dict[str, int] = {}
                if request.timeWindows and len(request.timeWindows) > 0:
                    # Map demand to each provided shift using multiplier
                    for tw in request.timeWindows:
                        scaled = int(round(loc.demand * float(getattr(tw, "demandMultiplier", 1.0))))
                        demand_by_shift[tw.id] = max(0, scaled)
                else:
                    demand_by_shift["shift1"] = loc.demand

                depot = Depot(
                    id=loc.id,
                    name=loc.name,
                    lat=loc.lat,
                    lon=loc.lng,
                    demand_by_shift=demand_by_shift
                )
                depots.append(depot)
        
        # Create shifts (support multi-shifts with per-shift duration)
        if request.timeWindows and len(request.timeWindows) > 0:
            shifts = []
            for tw in request.timeWindows:
                duration = tw.durationMin if tw.durationMin is not None else 60
                shifts.append(Shift(id=tw.id, start_time=tw.start, max_ride_minutes=duration))
        else:
            shifts = [Shift(id="shift1", start_time="08:00", max_ride_minutes=60)]
        
        # Create vehicle types
        owned_vehicles = []
        rented_vehicles = []
        
        for vt in request.vehicleTypes:
            if vt.type == "owned":
                owned_vehicles.append(OwnedVehicleType(
                    type_id=vt.name,
                    capacity=vt.capacity,
                    cost_per_km=vt.costPerKm,
                    count=vt.count or 1
                ))
            else:  # rented
                fixed_cost = float(vt.fixedRentalCost or 0.0)
                # Support 'count' for rented by treating as multiple available rentals with same spec
                rented_count = vt.count or 1
                for _ in range(rented_count):
                    rented_vehicles.append(RentedVehicleType(
                        type_id=vt.name,
                        capacity=vt.capacity,
                        cost_per_km=vt.costPerKm,
                        fixed_rental_cost=fixed_cost
                    ))
        
        fleet = Fleet(owned=owned_vehicles, rented=rented_vehicles)
        
        # Create instance
        instance = Instance(
            factory=factory,
            depots=depots,
            shifts=shifts,
            vehicles=fleet,
            distances_km={},  # Will be calculated by solver
            times_min={}       # Will be calculated by solver
        )
        
        result.logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": "info",
            "message": f"Running VRP optimization with {len(depots)} depots and {sum(vt.count for vt in request.vehicleTypes)} vehicles..."
        })
        
        # Get algorithm settings from frontend
        pop_size = request.algorithmSettings.get("populationSize", 20)
        generations = request.algorithmSettings.get("generations", 60)
        max_time = request.algorithmSettings.get("maxTime", 300)  # minutes from FE
        # OSRM: default ON with sensible default URL if not provided
        use_osrm = bool(request.algorithmSettings.get("useOSRM", True))
        osrm_url = request.algorithmSettings.get("osrmUrl") or os.environ.get("OSRM_URL") or "http://router.project-osrm.org"
        
        # Clarify GA settings; interpret maxTime from frontend as minutes
        result.logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": "info",
            "message": f"Using GA settings: pop_size={pop_size}, generations={generations}, max_time(min)={max_time}, use_osrm={use_osrm}"
        })
        
        # Run the actual VRP solver with GA parameters
        print("🔍 Testing GA solver import...", flush=True)
        if not VRP_AVAILABLE:
            print("❌ GA solver not available", flush=True)
            raise ImportError("GA solver not available")
        print("✅ GA solver import successful", flush=True)
        
        result.logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": "info",
            "message": "🚀 Starting Genetic Algorithm optimization..."
        })
        
        print("🚀 Starting GA VRP Optimization", flush=True)
        print(f"📊 Population: {pop_size}, Generations: {generations}, Max Time (min): {max_time}", flush=True)
        print(f"🛰️ OSRM: {'ON' if use_osrm else 'OFF'}{f' ({osrm_url})' if use_osrm and osrm_url else ''}", flush=True)
        print(f"🏭 Factory: {factory.name} at ({factory.lat}, {factory.lon})", flush=True)
        print(f"🏢 Depots: {len(depots)}", flush=True)
        for depot in depots:
            print(f"   - {depot.name}: {depot.demand_by_shift.get('shift1', 0)} passengers", flush=True)
        print(f"🚛 Vehicles: {len(owned_vehicles)} owned, {len(rented_vehicles)} rented", flush=True)
        
        try:
            print("🔄 Calling solve_ga...", flush=True)
            print(f"   Instance details: {len(instance.depots)} depots, {len(instance.vehicles.owned)} owned, {len(instance.vehicles.rented)} rented", flush=True)
            print(f"   Factory: {instance.factory.name} at ({instance.factory.lat}, {instance.factory.lon})", flush=True)
            print(f"   Depots: {[d.name for d in instance.depots]}", flush=True)
            print(f"   Owned vehicles: {[v.type_id for v in instance.vehicles.owned]}", flush=True)
            print(f"   Rented vehicles: {[v.type_id for v in instance.vehicles.rented]}", flush=True)
            print("🔄 About to call solve_ga function...", flush=True)
            
            solution = solve_ga(
                instance,
                pop_size=pop_size,
                generations=generations,
                mutation_rate=0.2,
                use_osrm=use_osrm,
                osrm_url=osrm_url
            )
            print("✅ solve_ga returned successfully!", flush=True)
            print(f"✅ GA Optimization Complete!", flush=True)
            print(f"💰 Total Cost: ${solution.total_cost:.2f}", flush=True)
            print(f"🚗 Routes Generated: {len(solution.routes)}", flush=True)
            print(f"📋 Depot Leftovers: {solution.depot_leftovers}", flush=True)

            # Print detailed route information with depot breakdown
            for i, route in enumerate(solution.routes):
                print(f"   Route {i+1}: {route.vehicle_type_id} - {route.passengers}/{route.seats} passengers, cost: ${route.cost:.2f}", flush=True)
                if hasattr(route, 'pickups'):
                    for depot_id, pax in route.pickups:
                        try:
                            d = next(d for d in depots if d.id == depot_id)
                            print(f"      - {d.name}: +{pax}", flush=True)
                        except StopIteration:
                            print(f"      - {depot_id}: +{pax}", flush=True)
                
        except Exception as e:
            print(f"❌ GA Optimization Failed: {str(e)}", flush=True)
            import traceback
            traceback.print_exc()
            raise
        
        result.logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": "info",
            "message": f"VRP optimization completed with {len(solution.routes)} routes"
        })
        
        # Convert VRP solution to frontend format
        routes = []
        for i, route in enumerate(solution.routes):
            # Create stops for the route
            stops = []
            
            # Add depot stops (pickups)
            for depot_id, passengers in route.pickups:
                depot = next(d for d in depots if d.id == depot_id)
                stops.append({
                    "id": depot_id,
                    "name": depot.name,
                    "lat": depot.lat,
                    "lng": depot.lon,
                    "type": "pickup",
                    "demand": passengers,
                    "arrivalTime": route.arrival_time,
                    "serviceTime": 5
                })
            
            # Add factory stop (delivery)
            stops.append({
                "id": "factory",
                "name": factory.name,
                "lat": factory.lat,
                "lng": factory.lon,
                "type": "delivery",
                "demand": -route.passengers,
                "arrivalTime": route.arrival_time,
                "serviceTime": 10
            })
            
            # Calculate total distance and time
            total_distance = sum(leg.distance_km for leg in route.legs)
            total_time = sum(leg.time_min for leg in route.legs)
            
            frontend_route = Route(
                id=f"route-{i}",
                vehicleId=f"vehicle-{i}",
                vehicleType=route.vehicle_type_id,
                stops=stops,
                totalDistance=total_distance,
                totalTime=total_time,
                totalCost=route.cost,
                capacity=route.seats,
                violations=[]  # Will be populated from solution.violations if needed
            )
            routes.append(frontend_route)
        
        # Update result with actual solution
        result.routes = routes
        result.totalCost = solution.total_cost
        result.totalDistance = sum(route.totalDistance for route in routes)
        result.status = "completed"
        result.progress = 100
        result.bestFitness = solution.total_cost
        
        # Add depot leftovers information
        depot_leftovers = []
        for depot_id, remaining in solution.depot_leftovers.items():
            depot_leftovers.append({
                "depotId": depot_id,
                "remainingDemand": remaining,
                "status": "unserved" if remaining > 0 else "fully_served"
            })
        
        result.violations = depot_leftovers
        
        result.logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": "info",
            "message": f"Optimization completed successfully with {len(routes)} routes, total cost: ${solution.total_cost:.2f}"
        })
        
        # Add detailed route information
        for i, route in enumerate(solution.routes):
            result.logs.append({
                "timestamp": datetime.now().isoformat(),
                "level": "info",
                "message": f"Route {i+1}: {route.vehicle_type_id} carrying {route.passengers}/{route.seats} passengers, cost: ${route.cost:.2f}"
            })
        
    except Exception as e:
        result.logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": "error",
            "message": f"VRP optimization failed: {str(e)}"
        })
        result.status = "failed"
        result.progress = 0

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
