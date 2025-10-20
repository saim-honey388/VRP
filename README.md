VRP — Multi‑Depot Employee Transportation (GA + OSRM + Folium)
===============================================================

A practical Vehicle Routing Problem (VRP) tool for shuttling employees from multiple depots to a factory across shifts, using a heterogeneous fleet (owned + rented). Routes follow real roads via OSRM; solutions are visualized on an interactive Folium map. The solver uses a Genetic Algorithm (GA) with a deterministic, feasible decoder.

Why this exists
---------------
- Plan cost‑efficient transport of employees from many pickup depots to a factory
- Respect seats, vehicle availability, max ride time, and shift arrival
- Use real‑world road distances/times (OSRM), not straight lines
- Visualize routes clearly for review and communication

Key features
------------
- Multi‑depot, multi‑shift, heterogeneous fleet (owned counts, rented types)
- Sequential decoder builds feasible routes from a global remaining demand
  - Greedy nearest‑neighbor multi‑stop pickups per vehicle
  - No duplicate depot in a route; stops immediately at capacity
  - Respects owned vehicle counts; rented optional
- OSRM integration (public or self‑hosted) with caching per segment
- Folium HTML map with per‑route tooltips (pax/empty/time/cost/dist)
- Detailed per‑route reports with per‑depot pickup quantities
- Interactive Leaflet picker to select factory/depots
  - Left‑click preview, right‑click confirm
  - Manual latitude/longitude entry
  - Search by place/region; optional Plus Codes support

Screenshots / Demo
------------------
- Picker: select factory + depots, then download `locations.json`
- Folium map: rendered routes with polylines and rich tooltips

Installation
------------
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Quick start
-----------
1) Pick coordinates (factory + depots)
```bash
python -m vrp_mvp.cli --make-picker locations_picker.html
xdg-open locations_picker.html
```
- Left‑click to preview, right‑click to confirm.
- You can also type lat/lon and click “Place by coords”, then right‑click to confirm.
- Download to `locations.json` when done.

2) Run GA solver
```bash
python -m vrp_mvp.cli \
  --locations "/path/to/locations.json" \
  --use-osrm \
  --map solution_ga_map.html \
  --solver ga --pop-size 6 --generations 2
```
The CLI will prompt for shifts, per‑depot demand, and fleet (e.g., OWN1/OWN2). The solution is printed, saved to JSON, and visualized to HTML.

CLI overview
------------
- `--interactive` interactive prompts for all inputs
- `--locations` load factory/depots JSON from the picker
- `--make-picker` generate the HTML picker
- `--map` write Folium HTML of the solution
- `--use-osrm` enable OSRM road routing (default server is the public demo)
- `--osrm-url` set a custom OSRM server (recommended for reliability)
- `--solver {baseline,ga}` choose solver (GA is the focus)
- GA params: `--pop-size`, `--generations`, `--mutation`

Data model (abridged)
---------------------
- Depots: `id`, `name`, `lat`, `lon`, `demand_by_shift: {shift_id: passengers}`
- Factory: `id`, `name`, `lat`, `lon`
- Shifts: `id`, `start_time (HH:MM)`, `max_ride_minutes`
- Fleet:
  - Owned: `{type_id, capacity, cost_per_km, count}`
  - Rented: `{type_id, capacity, cost_per_km, fixed_rental_cost}`
- Solution routes include `pickups: [(depot_id, passengers)]` and per‑segment `legs`

How the GA works (high level)
-----------------------------
- Population of chromosomes; each evaluated by a deterministic decoder:
  1) Build a concrete vehicle list (respect owned counts; prefer smaller capacity first)
  2) Maintain global `remaining_demand` per depot
  3) For each vehicle: start at depot with largest remaining, then greedily add nearest depots
     until capacity is reached; never revisit a depot
  4) Build per‑segment OSRM legs; compute cost (distance × cost_per_km + fixed rental if any)
- Fitness = total cost (+ penalty per unserved passenger)
- Selection, crossover, mutation produce new populations

Performance tips
----------------
- OSRM calls are the main bottleneck; use `--use-osrm` only when needed
- Prefer a local OSRM instance for speed and reliability; caching is enabled per segment
- For quick iterations set small `--pop-size` and `--generations`

Troubleshooting
---------------
- Panel resizing in picker: use map zoom (mouse wheel over map). Browser zoom scales the entire page
- If the map doesn’t load, hard‑refresh and check the console for CDN errors
- Public OSRM rate limits can slow runs; use `--osrm-url` for a private server

Project layout
--------------
- `vrp_mvp/models.py`  — data models (depots, factory, shifts, fleet, routes, reports)
- `vrp_mvp/ga_solver.py` — GA solver + sequential decoder (multi‑depot, capacity‑aware)
- `vrp_mvp/osrm.py`    — OSRM API wrapper
- `vrp_mvp/visualize.py` — Folium visualization of solutions
- `vrp_mvp/cli.py`     — CLI (picker generation, solver, map export)
- `locations_picker.html` — Leaflet picker to generate `locations.json`
- `examples/`          — example instances (if present)

Roadmap
-------
- Hard max ride‑time enforcement in decoder (currently validated and reported)
- Better GA chromosome representation and operators for faster convergence
- Multi‑shift optimization in a single run
- Rented vehicle budgeting and fixed‑cost trade‑offs

License
-------
MIT


