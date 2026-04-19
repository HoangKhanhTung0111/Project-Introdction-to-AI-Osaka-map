"""
Task 3.3 — server.py
FastAPI backend: endpoint /api/find_path nhận tọa độ A, B → trả đường đi + khoảng cách.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from nearest_point import nearest_node
from node_id_to_latlon import node_ids_to_latlon
from astar import astar, dijkstra

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Pathfinder API",
    description="Tìm đường ngắn nhất trên bản đồ Hà Nội (A* / Dijkstra)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev: cho phép mọi origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schema ────────────────────────────────────────────────────────────────────

class LatLon(BaseModel):
    lat: float = Field(..., description="Vĩ độ (latitude)", example=21.028)
    lon: float = Field(..., description="Kinh độ (longitude)", example=105.852)


class FindPathRequest(BaseModel):
    point_a: LatLon = Field(..., description="Điểm xuất phát")
    point_b: LatLon = Field(..., description="Điểm đích")
    algorithm: str  = Field(default="astar", description="'astar' hoặc 'dijkstra'")


class NodeSnap(BaseModel):
    node_id:    int
    lat:        float
    lon:        float
    distance_m: float   # khoảng cách từ click đến node snap (mét)


class FindPathResponse(BaseModel):
    found:        bool
    node_a:       NodeSnap
    node_b:       NodeSnap
    path_nodes:   list[int]                  # mảng node_id
    path_coords:  list[list[float]]          # [[lat,lon], ...] cho Leaflet
    total_distance_m: float
    algorithm_used:   str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/find_path", response_model=FindPathResponse)
def find_path(req: FindPathRequest):
    """
    Nhận tọa độ A, B → snap sang node gần nhất → chạy A* / Dijkstra
    → trả mảng tọa độ đường đi.
    """
    # 1. Snap tọa độ click → node_id gần nhất
    snap_a = nearest_node(req.point_a.lat, req.point_a.lon)
    snap_b = nearest_node(req.point_b.lat, req.point_b.lon)

    if snap_a["node_id"] == snap_b["node_id"]:
        raise HTTPException(
            status_code=400,
            detail="Điểm A và B snap về cùng một node. Hãy chọn hai điểm cách xa hơn."
        )

    # 2. Chạy thuật toán tìm đường
    algo = req.algorithm.lower()
    if algo == "dijkstra":
        result = dijkstra(snap_a["node_id"], snap_b["node_id"])
    else:
        result = astar(snap_a["node_id"], snap_b["node_id"])

    if not result["found"]:
        raise HTTPException(
            status_code=404,
            detail="Không tìm được đường đi giữa hai điểm đã chọn."
        )

    # 3. Chuyển node_id → tọa độ
    coords = node_ids_to_latlon(result["path"])

    return FindPathResponse(
        found=True,
        node_a=NodeSnap(**snap_a),
        node_b=NodeSnap(**snap_b),
        path_nodes=result["path"],
        path_coords=coords,
        total_distance_m=result["distance"],
        algorithm_used=algo,
    )


@app.get("/api/nodes")
def get_nodes_endpoint():
    """Trả toàn bộ nodes để Frontend hiển thị."""
    from nearest_point import get_nodes
    return {"nodes": get_nodes()}


# ── Serve GeoJSON tĩnh ────────────────────────────────────────────────────────
_geojson_path = os.path.join(os.path.dirname(__file__), "roads.geojson")

@app.get("/api/roads")
def get_roads():
    import json
    with open(_geojson_path, encoding="utf-8") as f:
        return json.load(f)


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
