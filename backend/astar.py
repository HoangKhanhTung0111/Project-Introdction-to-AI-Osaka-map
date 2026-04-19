"""
astar.py — Thuật toán tìm đường A* trên đồ thị nodes/edges.
"""
import csv
import heapq
import math
import os
from typing import Optional

_EDGES_PATH = os.path.join(os.path.dirname(__file__), "edges.csv")
_NODES_PATH = os.path.join(os.path.dirname(__file__), "nodes.csv")

# ── Load graph ───────────────────────────────────────────────────────────────

_graph: Optional[dict[int, list[tuple[int, float]]]] = None
_node_coords: Optional[dict[int, tuple[float, float]]] = None


def _load_graph():
    global _graph, _node_coords

    _node_coords = {}
    with open(_NODES_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            _node_coords[int(row["node_id"])] = (float(row["lat"]), float(row["lon"]))

    _graph = {nid: [] for nid in _node_coords}
    with open(_EDGES_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            src, dst, dist = int(row["from"]), int(row["to"]), float(row["distance"])
            _graph.setdefault(src, []).append((dst, dist))


def get_graph():
    if _graph is None:
        _load_graph()
    return _graph, _node_coords


# ── Heuristic ────────────────────────────────────────────────────────────────

def _heuristic(nid: int, goal: int, coords: dict) -> float:
    """Khoảng cách Haversine từ node hiện tại → goal làm heuristic."""
    R = 6_371_000
    lat1, lon1 = coords[nid]
    lat2, lon2 = coords[goal]
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


# ── A* ────────────────────────────────────────────────────────────────────────

def astar(start: int, goal: int) -> dict:
    """
    Tìm đường ngắn nhất từ `start` đến `goal` bằng A*.

    Returns
    -------
    {
      "path":      [node_id, ...],   # danh sách node_id theo thứ tự
      "distance":  float,            # tổng khoảng cách (mét)
      "found":     bool
    }
    """
    graph, coords = get_graph()

    if start not in graph or goal not in graph:
        return {"path": [], "distance": 0.0, "found": False}

    # priority queue: (f_score, node_id)
    open_set: list[tuple[float, int]] = []
    heapq.heappush(open_set, (0.0, start))

    came_from: dict[int, int] = {}
    g_score: dict[int, float] = {start: 0.0}
    f_score: dict[int, float] = {start: _heuristic(start, goal, coords)}

    visited: set[int] = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            # Reconstruct path
            path = []
            node = goal
            while node in came_from:
                path.append(node)
                node = came_from[node]
            path.append(start)
            path.reverse()
            return {"path": path, "distance": round(g_score[goal], 2), "found": True}

        if current in visited:
            continue
        visited.add(current)

        for neighbor, weight in graph.get(current, []):
            if neighbor in visited:
                continue
            tentative_g = g_score.get(current, float("inf")) + weight
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + _heuristic(neighbor, goal, coords)
                f_score[neighbor] = f
                heapq.heappush(open_set, (f, neighbor))

    return {"path": [], "distance": 0.0, "found": False}


# ── Dijkstra (bonus algorithm) ───────────────────────────────────────────────

def dijkstra(start: int, goal: int) -> dict:
    """Dijkstra thuần — so sánh với A*."""
    graph, _ = get_graph()

    pq: list[tuple[float, int]] = [(0.0, start)]
    dist: dict[int, float] = {start: 0.0}
    prev: dict[int, int] = {}
    visited: set[int] = set()

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        if u == goal:
            break
        for v, w in graph.get(u, []):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if goal not in dist:
        return {"path": [], "distance": 0.0, "found": False}

    path = []
    node = goal
    while node in prev:
        path.append(node); node = prev[node]
    path.append(start); path.reverse()
    return {"path": path, "distance": round(dist[goal], 2), "found": True}


# ── self-test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    r = astar(0, 99)
    print("A*:", r)
    r2 = dijkstra(0, 99)
    print("Dijkstra:", r2)
