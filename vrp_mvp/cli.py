from __future__ import annotations

import json
from pathlib import Path
import click

from .io import load_instance, save_solution
from .solver import solve_baseline
from .ga_solver import solve_ga
from .models import (
    Instance,
    Depot,
    Factory,
    Shift,
    Fleet,
    OwnedVehicleType,
    RentedVehicleType,
)
from .visualize import render_map
from .picker import write_picker_html


def _prompt_instance() -> Instance:
    click.echo("Enter factory (central depot) details:")
    f_id = click.prompt("Factory ID", default="F")
    f_name = click.prompt("Factory name", default="Factory")
    f_lat = click.prompt("Factory latitude", type=float)
    f_lon = click.prompt("Factory longitude", type=float)
    factory = Factory(id=f_id, name=f_name, lat=f_lat, lon=f_lon)

    # Shifts
    n_shifts = click.prompt("Number of shifts", type=int, default=1)
    shifts: list[Shift] = []
    for i in range(n_shifts):
        sid = click.prompt(f"Shift {i+1} ID", default=f"S{i+1}")
        sstart = click.prompt(f"Shift {sid} start time (HH:MM)", default="08:00")
        sride = click.prompt(f"Shift {sid} max ride minutes", type=int, default=90)
        shifts.append(Shift(id=sid, start_time=sstart, max_ride_minutes=sride))

    # Depots
    n_depots = click.prompt("Number of depots (pickup points)", type=int)
    depots: list[Depot] = []
    for i in range(n_depots):
        did = click.prompt(f"Depot {i+1} ID", default=f"D{i+1}")
        dname = click.prompt(f"Depot {did} name", default=f"Depot {i+1}")
        dlat = click.prompt(f"Depot {did} latitude", type=float)
        dlon = click.prompt(f"Depot {did} longitude", type=float)
        demand_by_shift: dict[str, int] = {}
        for sh in shifts:
            dem = click.prompt(f"Demand at {did} for shift {sh.id}", type=int, default=0)
            demand_by_shift[sh.id] = dem
        depots.append(Depot(id=did, name=dname, lat=dlat, lon=dlon, demand_by_shift=demand_by_shift))

    # Vehicles
    click.echo("Enter OWNED vehicle types:")
    n_owned = click.prompt("Count of owned types", type=int, default=1)
    owned: list[OwnedVehicleType] = []
    for i in range(n_owned):
        tid = click.prompt(f"Owned type {i+1} ID", default=f"OWN{i+1}")
        cap = click.prompt(f"{tid} capacity (seats)", type=int)
        cpk = click.prompt(f"{tid} cost per km", type=float)
        cnt = click.prompt(f"{tid} available count", type=int, default=1)
        owned.append(OwnedVehicleType(type_id=tid, capacity=cap, cost_per_km=cpk, count=cnt))

    click.echo("Enter RENTED vehicle types:")
    n_rent = click.prompt("Count of rented types", type=int, default=1)
    rented: list[RentedVehicleType] = []
    for i in range(n_rent):
        tid = click.prompt(f"Rented type {i+1} ID", default=f"RENT{i+1}")
        cap = click.prompt(f"{tid} capacity (seats)", type=int)
        cpk = click.prompt(f"{tid} cost per km", type=float)
        fix = click.prompt(f"{tid} fixed rental cost", type=float)
        rented.append(RentedVehicleType(type_id=tid, capacity=cap, cost_per_km=cpk, fixed_rental_cost=fix))

    fleet = Fleet(owned=owned, rented=rented)
    inst = Instance(depots=depots, factory=factory, shifts=shifts, vehicles=fleet)
    return inst

def _prompt_instance_partial(locations: dict) -> Instance:
    # locations: { factory: {lat, lon}, depots: [{id?, name?, lat, lon}, ...] }
    if not locations.get("factory"):
        raise click.UsageError("locations.json is missing 'factory'")
    f_lat = float(locations["factory"]["lat"])
    f_lon = float(locations["factory"]["lon"])
    f_id = click.prompt("Factory ID", default="F")
    f_name = click.prompt("Factory name", default="Factory")
    factory = Factory(id=f_id, name=f_name, lat=f_lat, lon=f_lon)

    # Shifts
    n_shifts = click.prompt("Number of shifts", type=int, default=1)
    shifts: list[Shift] = []
    for i in range(n_shifts):
        sid = click.prompt(f"Shift {i+1} ID", default=f"S{i+1}")
        sstart = click.prompt(f"Shift {sid} start time (HH:MM)", default="08:00")
        sride = click.prompt(f"Shift {sid} max ride minutes", type=int, default=90)
        shifts.append(Shift(id=sid, start_time=sstart, max_ride_minutes=sride))

    depots: list[Depot] = []
    for i, d in enumerate(locations.get("depots", [])):
        did = d.get("id") or f"D{i+1}"
        dname = d.get("name") or f"Depot {i+1}"
        dlat = float(d["lat"]) ; dlon = float(d["lon"]) 
        demand_by_shift: dict[str, int] = {}
        for sh in shifts:
            dem = click.prompt(f"Demand at {did} for shift {sh.id}", type=int, default=0)
            demand_by_shift[sh.id] = dem
        depots.append(Depot(id=did, name=dname, lat=dlat, lon=dlon, demand_by_shift=demand_by_shift))

    # Vehicles
    click.echo("Enter OWNED vehicle types:")
    n_owned = click.prompt("Count of owned types", type=int, default=1)
    owned: list[OwnedVehicleType] = []
    for i in range(n_owned):
        tid = click.prompt(f"Owned type {i+1} ID", default=f"OWN{i+1}")
        cap = click.prompt(f"{tid} capacity (seats)", type=int)
        cpk = click.prompt(f"{tid} cost per km", type=float)
        cnt = click.prompt(f"{tid} available count", type=int, default=1)
        owned.append(OwnedVehicleType(type_id=tid, capacity=cap, cost_per_km=cpk, count=cnt))

    click.echo("Enter RENTED vehicle types:")
    n_rent = click.prompt("Count of rented types", type=int, default=1)
    rented: list[RentedVehicleType] = []
    for i in range(n_rent):
        tid = click.prompt(f"Rented type {i+1} ID", default=f"RENT{i+1}")
        cap = click.prompt(f"{tid} capacity (seats)", type=int)
        cpk = click.prompt(f"{tid} cost per km", type=float)
        fix = click.prompt(f"{tid} fixed rental cost", type=float)
        rented.append(RentedVehicleType(type_id=tid, capacity=cap, cost_per_km=cpk, fixed_rental_cost=fix))

    fleet = Fleet(owned=owned, rented=rented)
    inst = Instance(depots=depots, factory=factory, shifts=shifts, vehicles=fleet)
    return inst

@click.command()
@click.option("--instance", "instance_path", type=click.Path(exists=True, dir_okay=False), required=False)
@click.option("--out", "out_path", type=click.Path(dir_okay=False), default="solution.json")
@click.option("--solver", type=click.Choice(["baseline", "ga"], case_sensitive=False), default="baseline")
@click.option("--pop-size", type=int, default=20)
@click.option("--generations", type=int, default=60)
@click.option("--mutation", type=float, default=0.2)
@click.option("--interactive", is_flag=True, default=False, help="Prompt for inputs instead of loading JSON")
@click.option("--map", "map_path", type=click.Path(dir_okay=False), default=None, help="Output HTML map file")
@click.option("--use-osrm", is_flag=True, default=False, help="Use OSRM road routing")
@click.option("--osrm-url", type=str, default="http://router.project-osrm.org", help="OSRM base URL")
@click.option("--make-picker", type=click.Path(dir_okay=False), default=None, help="Write a map picker HTML here and exit")
@click.option("--locations", type=click.Path(exists=True, dir_okay=False), default=None, help="JSON from picker with factory and depots")
def main(instance_path: str | None, out_path: str, solver: str, pop_size: int, generations: int, mutation: float, interactive: bool, map_path: str | None, use_osrm: bool, osrm_url: str, make_picker: str | None, locations: str | None) -> None:
    if make_picker:
        write_picker_html(make_picker)
        click.echo(json.dumps({"picker": make_picker}))
        return

    if interactive:
        inst = _prompt_instance()
        # Default to GA in interactive mode
        solver = "ga"
    else:
        if locations:
            # Load locations and then prompt for remaining fields
            import json as _json
            from pathlib import Path as _Path
            loc = _json.loads(_Path(locations).read_text())
            inst = _prompt_instance_partial(loc)
            solver = "ga"
        else:
            if not instance_path:
                raise click.UsageError("--instance is required unless --interactive or --locations is used")
            inst = load_instance(instance_path)
    if solver == "ga":
        sol = solve_ga(inst, pop_size=pop_size, generations=generations, mutation_rate=mutation, use_osrm=use_osrm, osrm_url=osrm_url)
    else:
        sol = solve_baseline(inst)
    save_solution(sol, out_path)
    
    # Print detailed summary
    click.echo(json.dumps({
        "total_cost": sol.total_cost, 
        "routes": len(sol.routes),
        "violations": sol.violations,
        "depot_leftovers": sol.depot_leftovers
    }, indent=2))
    
    # Print per-route details
    if sol.reports:
        click.echo("\n=== ROUTE REPORTS ===")
        for report in sol.reports:
            click.echo(f"\nVehicle {report.vehicle_id} ({report.vehicle_type}):")
            click.echo(f"  Passengers: {report.passengers_carried}/{report.passengers_carried + report.empty_seats} (Empty: {report.empty_seats})")
            click.echo(f"  Trip Time: {report.total_trip_time_min:.1f} min")
            click.echo(f"  Trip Cost: ${report.total_trip_cost:.2f}")
            if report.violations:
                click.echo(f"  Violations: {', '.join(report.violations)}")
            for visit in report.depot_visits:
                click.echo(f"    {visit['depot_id']}: {visit['passengers']} pax, {visit['time_min']:.1f} min, ${visit['cost']:.2f}")
    if map_path:
        render_map(sol, inst, map_path)
        click.echo(json.dumps({"map": map_path}))


if __name__ == "__main__":
    main()


