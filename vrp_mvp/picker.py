from __future__ import annotations

from pathlib import Path


PICKER_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>VRP Location Picker</title>
  <link rel=\"stylesheet\" href=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.css\" />
  <style>
    html, body, #map { height: 100%; margin: 0; }
    .panel { position: absolute; top: 10px; left: 10px; background: white; padding: 8px; z-index: 1000; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.2); }
    .panel button { margin-right: 6px; }
    pre { max-height: 200px; overflow: auto; background: #f5f5f5; padding: 6px; }
  </style>
</head>
<body>
  <div id=\"map\"></div>
  <div class=\"panel\">
    <div>
      <button id=\"mode-factory\">Set Factory</button>
      <button id=\"mode-depot\">Add Depot</button>
      <button id=\"clear\">Clear</button>
      <button id=\"download\">Download JSON</button>
    </div>
    <div>
      <input id=\"region\" placeholder=\"Type city/country (e.g., Lahore)\" />
      <button id=\"go\">Go</button>
    </div>
    <div><small>Click map: first set factory, then add depots.</small></div>
    <pre id=\"out\"></pre>
  </div>

  <script src=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.js\"></script>
  <script>
    const map = L.map('map', { scrollWheelZoom: true }).setView([25.1, 55.17], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 20 }).addTo(map);

    let mode = 'factory';
    let factory = null;
    let depots = [];
    let markers = [];

    function refreshOutput() {
      const obj = { factory, depots };
      document.getElementById('out').textContent = JSON.stringify(obj, null, 2);
    }

    function clearAll() {
      factory = null; depots = [];
      markers.forEach(m => map.removeLayer(m));
      markers = [];
      refreshOutput();
    }

    document.getElementById('mode-factory').onclick = () => { mode = 'factory'; };
    document.getElementById('mode-depot').onclick = () => { mode = 'depot'; };
    document.getElementById('clear').onclick = clearAll;
    document.getElementById('download').onclick = () => {
      const data = JSON.stringify({ factory, depots }, null, 2);
      const blob = new Blob([data], {type: 'application/json'});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'locations.json'; a.click();
      URL.revokeObjectURL(url);
    };

    document.getElementById('go').onclick = async () => {
      const q = document.getElementById('region').value;
      if (!q) return;
      const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&limit=1`);
      const data = await res.json();
      if (data && data.length > 0) {
        const item = data[0];
        const bbox = item.boundingbox.map(parseFloat); // [south, north, west, east]
        const south = bbox[0], north = bbox[1], west = bbox[2], east = bbox[3];
        const bounds = L.latLngBounds([south, west], [north, east]);
        map.fitBounds(bounds);
        // Choose a sensible zoom depending on region size
        const width = Math.abs(east - west);
        const height = Math.abs(north - south);
        let zoom = 11;
        const maxSpan = Math.max(width, height);
        if (maxSpan > 10) zoom = 6; // country-scale
        else if (maxSpan > 5) zoom = 7;
        else if (maxSpan > 2) zoom = 9;
        else if (maxSpan > 1) zoom = 11;
        else if (maxSpan > 0.5) zoom = 12;
        else zoom = 13; // city/neighborhoood
        const centerLat = parseFloat(item.lat), centerLon = parseFloat(item.lon);
        map.setView([centerLat, centerLon], zoom);
        map.setMaxBounds(bounds.pad(0.1));
        map.invalidateSize();
        // Optional: visually show bbox
        if (window._bbox) { map.removeLayer(window._bbox); }
        window._bbox = L.rectangle(bounds, {color: '#ff7800', weight: 1, fillOpacity: 0.03}).addTo(map);
      }
    };

    map.on('click', function(e) {
      const lat = e.latlng.lat; const lon = e.latlng.lng;
      if (mode === 'factory') {
        factory = { lat, lon };
        // remove previous factory marker
        markers.forEach(m => { if (m.options && m.options.title === 'factory') map.removeLayer(m); });
        const m = L.marker([lat, lon], {title: 'factory'}).addTo(map).bindPopup('Factory');
        markers.push(m);
      } else {
        const id = 'D' + (depots.length + 1);
        depots.push({ id, name: 'Depot ' + (depots.length + 1), lat, lon });
        const m = L.marker([lat, lon], {title: id}).addTo(map).bindPopup(id);
        markers.push(m);
      }
      refreshOutput();
    });

    refreshOutput();
  </script>
</body>
</html>
"""


def write_picker_html(path: str) -> None:
    Path(path).write_text(PICKER_HTML)


