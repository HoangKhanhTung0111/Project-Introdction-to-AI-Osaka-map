# Pathfinder — Tìm đường ngắn nhất (A* / Dijkstra)

Ứng dụng tìm đường trên bản đồ Hà Nội với backend FastAPI + frontend React-Leaflet.

```
pathfinder/
├── backend/
│   ├── nearest_point.py       # Task 3.1 — snap click → node_id gần nhất
│   ├── node_id_to_latlon.py   # Task 3.2 — node_id[] → [[lat,lon],...]
│   ├── astar.py               # Thuật toán A* & Dijkstra
│   ├── server.py              # Task 3.3 — FastAPI /api/find_path
│   ├── nodes.csv              # Dữ liệu nodes (node_id, lat, lon)
│   ├── edges.csv              # Dữ liệu cạnh (from, to, distance)
│   └── roads.geojson          # GeoJSON lớp đường cho bản đồ
└── frontend/
    ├── public/index.html
    └── src/
        ├── App.js                         # Task 4.1 — root component
        ├── styles.css
        ├── store/usePathStore.js          # Task 4.3 — Context + Reducer
        └── components/
            ├── MapView.jsx                # Task 4.2 + 4.4 — Leaflet map
            └── ControlPanel.jsx          # Task 4.3 — UI sidebar
```

---

## Cài đặt & chạy

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python server.py
# → http://localhost:8000
```

**API docs tự động:** http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm start
# → http://localhost:3000
```

Proxy đã được cấu hình sẵn trong `package.json` → mọi request `/api/*` tự forward tới `localhost:8000`.

---

## API Reference

### `POST /api/find_path`

**Request:**
```json
{
  "point_a":   { "lat": 21.028, "lon": 105.834 },
  "point_b":   { "lat": 21.045, "lon": 105.862 },
  "algorithm": "astar"
}
```

**Response:**
```json
{
  "found": true,
  "node_a": { "node_id": 46, "lat": 21.027, "lon": 105.835, "distance_m": 142.5 },
  "node_b": { "node_id": 87, "lat": 21.044, "lon": 105.861, "distance_m": 98.3 },
  "path_nodes":  [46, 47, 57, 67, 77, 87],
  "path_coords": [[21.027, 105.835], [21.027, 105.844], ...],
  "total_distance_m": 4823.6,
  "algorithm_used": "astar"
}
```

### `GET /api/roads`
Trả về GeoJSON đường đi để vẽ lớp nền bản đồ.

### `GET /api/nodes`
Trả về toàn bộ danh sách nodes.

---

## Dùng dữ liệu thực (OpenStreetMap)

Để thay mock data bằng dữ liệu thực của Hà Nội:

```bash
pip install osmnx
python3 - <<'EOF'
import osmnx as ox, csv, json

G = ox.graph_from_place("Hanoi, Vietnam", network_type="drive")
nodes, edges = ox.graph_to_gdfs(G)

# nodes.csv
with open("nodes.csv","w",newline="") as f:
    w = csv.writer(f); w.writerow(["node_id","lat","lon"])
    for nid, row in nodes.iterrows():
        w.writerow([nid, row.y, row.x])

# edges.csv
with open("edges.csv","w",newline="") as f:
    w = csv.writer(f); w.writerow(["from","to","distance"])
    for (u,v,_), row in edges.iterrows():
        w.writerow([u, v, row.get("length", 0)])

print("Done!")
EOF
```
