"""
Task 3.2 — node_id_to_latlon.py
Chuyển đổi mảng node_id kết quả A* thành mảng tọa độ [lat, lon]
để Frontend dùng vẽ Polyline trên bản đồ.
"""
import os
from typing import Optional
from nearest_point import get_nodes   # tái dụng cache đã có

_NODES_PATH = os.path.join(os.path.dirname(__file__), "nodes.csv")


def build_node_index() -> dict[int, dict]:
    """Tạo dict {node_id -> {lat, lon}} để tra cứu O(1)."""
    return {n["node_id"]: n for n in get_nodes()}


# Cache index
_index: Optional[dict[int, dict]] = None


def get_index() -> dict[int, dict]:
    global _index
    if _index is None:
        _index = build_node_index()
    return _index


def node_ids_to_latlon(node_ids: list[int]) -> list[list[float]]:
    """
    Chuyển mảng node_id → mảng [[lat, lon], ...].

    Parameters
    ----------
    node_ids : list[int]  — thứ tự các node trên đường đi (output của A*)

    Returns
    -------
    list of [lat, lon] — dùng trực tiếp cho Leaflet Polyline / GeoJSON
    """
    index = get_index()
    result = []
    for nid in node_ids:
        if nid not in index:
            raise KeyError(f"node_id={nid} không tồn tại trong nodes.csv")
        n = index[nid]
        result.append([n["lat"], n["lon"]])
    return result


def node_ids_to_geojson_coords(node_ids: list[int]) -> list[list[float]]:
    """
    Giống node_ids_to_latlon nhưng trả về [[lon, lat], ...] theo chuẩn GeoJSON
    (GeoJSON dùng [longitude, latitude]).
    """
    index = get_index()
    return [[index[nid]["lon"], index[nid]["lat"]] for nid in node_ids]


# ── Quick self-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample_path = [0, 1, 2, 11, 21, 31]
    coords = node_ids_to_latlon(sample_path)
    print("Leaflet coords (lat, lon):")
    for c in coords:
        print(f"  {c}")

    geo = node_ids_to_geojson_coords(sample_path)
    print("\nGeoJSON coords (lon, lat):")
    for c in geo:
        print(f"  {c}")
