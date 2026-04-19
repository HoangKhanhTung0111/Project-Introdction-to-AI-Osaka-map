/**
 * Task 4.3 — store/usePathStore.js
 * Global state quản lý: markers, đường đi, thuật toán, loading, error
 */
import { createContext, useContext, useReducer, useCallback } from "react";

// ── State shape ───────────────────────────────────────────────────────────────
const initialState = {
  pointA: null,          // { lat, lon, address? }
  pointB: null,
  algorithm: "astar",    // "astar" | "dijkstra"
  result: null,          // FindPathResponse từ backend
  loading: false,
  error: null,
  activeMarker: "A",     // "A" | "B" — click tiếp theo đặt marker nào
};

// ── Reducer ───────────────────────────────────────────────────────────────────
function reducer(state, action) {
  switch (action.type) {
    case "SET_POINT_A":
      return { ...state, pointA: action.payload, result: null, error: null };
    case "SET_POINT_B":
      return { ...state, pointB: action.payload, result: null, error: null };
    case "SET_ALGORITHM":
      return { ...state, algorithm: action.payload, result: null };
    case "SET_ACTIVE_MARKER":
      return { ...state, activeMarker: action.payload };
    case "FIND_PATH_START":
      return { ...state, loading: true, error: null, result: null };
    case "FIND_PATH_SUCCESS":
      return { ...state, loading: false, result: action.payload };
    case "FIND_PATH_ERROR":
      return { ...state, loading: false, error: action.payload };
    case "CLEAR":
      return { ...initialState };
    case "SWAP_POINTS":
      return { ...state, pointA: state.pointB, pointB: state.pointA, result: null };
    default:
      return state;
  }
}

// ── Context ───────────────────────────────────────────────────────────────────
const PathContext = createContext(null);

export function PathProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const setPointA = useCallback((latlon) =>
    dispatch({ type: "SET_POINT_A", payload: latlon }), []);

  const setPointB = useCallback((latlon) =>
    dispatch({ type: "SET_POINT_B", payload: latlon }), []);

  const setAlgorithm = useCallback((algo) =>
    dispatch({ type: "SET_ALGORITHM", payload: algo }), []);

  const setActiveMarker = useCallback((marker) =>
    dispatch({ type: "SET_ACTIVE_MARKER", payload: marker }), []);

  const swapPoints = useCallback(() =>
    dispatch({ type: "SWAP_POINTS" }), []);

  const clear = useCallback(() =>
    dispatch({ type: "CLEAR" }), []);

  // ── Task 4.4: Call API ──────────────────────────────────────────────────────
  const findPath = useCallback(async () => {
    if (!state.pointA || !state.pointB) return;

    dispatch({ type: "FIND_PATH_START" });
    try {
      const res = await fetch("/api/find_path", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          point_a:   { lat: state.pointA.lat, lon: state.pointA.lon },
          point_b:   { lat: state.pointB.lat, lon: state.pointB.lon },
          algorithm: state.algorithm,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Lỗi không xác định" }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      dispatch({ type: "FIND_PATH_SUCCESS", payload: data });
    } catch (err) {
      dispatch({ type: "FIND_PATH_ERROR", payload: err.message });
    }
  }, [state.pointA, state.pointB, state.algorithm]);

  const value = {
    ...state,
    setPointA, setPointB, setAlgorithm,
    setActiveMarker, swapPoints, clear, findPath,
  };

  return <PathContext.Provider value={value}>{children}</PathContext.Provider>;
}

export function usePathStore() {
  const ctx = useContext(PathContext);
  if (!ctx) throw new Error("usePathStore must be used inside PathProvider");
  return ctx;
}
