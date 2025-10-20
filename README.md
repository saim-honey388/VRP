VRP MVP
=======

Minimal scaffold for the factory employee transportation problem (multi-depot, multi-shift, heterogeneous fleet).

What this MVP includes
----------------------
- Core data models: depots, vehicles, shifts, distance/time matrices
- Baseline direct solver: depot -> factory routes with capacity-based splitting
- Feasibility checks: capacity, shift arrival, max ride time (for direct trips)
- Cost model: distance * cost_per_km + fixed rental cost (for rented vehicles)
- CLI: load instance JSON and run baseline solver
- Example instance JSON under `examples/`

Quick start
----------
1) Create a virtual environment and install dependencies (none strictly required for MVP):
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) Run the CLI on the example instance:
```bash
python -m vrp_mvp.cli --instance examples/example_instance.json
```

Input schema (JSON)
-------------------
See `examples/example_instance.json` for a complete example. Top-level keys:
- depots: [{id, name, demand_by_shift:{"S1": int, ...}}]
- factory: {id, name}
- shifts: [{id, start_time: "HH:MM", max_ride_minutes: int}]
- vehicles: {
    owned: [{type_id, capacity, cost_per_km, count}],
    rented: [{type_id, capacity, cost_per_km, fixed_rental_cost}]
  }
- distances_km: matrix keyed by node ids (square, symmetric okay)
- times_min: matrix keyed by node ids (square, possibly asymmetric)

Notes
-----
- The MVP assumes vehicles start at the first depot they serve and end at the factory.
- Arrival must be before shift start. For direct trips, ride time equals travel time depot->factory.
- Owned fleet availability is enforced by counts per type per shift in this MVP.


