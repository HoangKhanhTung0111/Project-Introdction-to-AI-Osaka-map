"""
Task 3.1 — nearest_point.py
Tìm node_id gần nhất trong nodes.csv so với tọa độ (lat, lon) người dùng click.
"""
import csv
import math
import os
from typing import Optional

_NODES_PATH = os.path.join(os.path.dirname(__file__), "nodes.csv")


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Tính khoảng cách (mét) giữa hai điểm trên Trái Đất theo công thức Haversine."""
    R = 6_371_000  # bán kính Trái Đất (m)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def load_nodes(path: str = _NODES_PATH) -> list[dict]:
    """Đọc nodes.csv và trả về list dict {node_id, lat, lon}."""
    nodes = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            nodes.append({
                "node_id": int(row["node_id"]),
                "lat":     float(row["lat"]),
                "lon":     float(row["lon"]),
            })
    return nodes


# Cache để không đọc lại mỗi lần gọi
_nodes_cache: Optional[list[dict]] = None


def get_nodes() -> list[dict]:
    global _nodes_cache
    if _nodes_cache is None:
        _nodes_cache = load_nodes()
    return _nodes_cache


def nearest_node(lat: float, lon: float) -> dict:
    """
    Trả về dict {node_id, lat, lon, distance_m} của node gần (lat, lon) nhất.

    Parameters
    ----------
    lat : float  — vĩ độ điểm click
    lon : float  — kinh độ điểm click

    Returns
    -------
    dict với các trường node_id, lat, lon, distance_m
    """
    nodes = get_nodes()
    if not nodes:
        raise ValueError("nodes.csv trống hoặc không tồn tại.")

    best_node = None
    best_dist = float("inf")

    for node in nodes:
        d = haversine(lat, lon, node["lat"], node["lon"])
        if d < best_dist:
            best_dist = d
            best_node = node

    return {**best_node, "distance_m": round(best_dist, 2)}


# ── Quick self-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Thử với một điểm gần trung tâm Hà Nội
    result = nearest_node(21.028, 105.852)
    print(f"Nearest node: {result}")
