/**
 * Task 4.1 — App.js
 * Root component: tích hợp PathProvider, load roads GeoJSON, chia layout.
 */
import { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";
import "./styles.css";

import { PathProvider } from "./store/usePathStore";
import MapView       from "./components/MapView";
import ControlPanel  from "./components/ControlPanel";

export default function App() {
  const [roadsGeoJson, setRoadsGeoJson] = useState(null);
  const [geoError, setGeoError]         = useState(null);

  // Task 4.2: Đọc GeoJSON từ backend (hoặc /public nếu deploy tĩnh)
  useEffect(() => {
    fetch("/api/roads")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setRoadsGeoJson)
      .catch((err) => {
        console.warn("Không load được roads GeoJSON:", err.message);
        setGeoError(err.message);
        // Thử fallback: load từ /public
        fetch("/roads.geojson")
          .then((r) => r.ok ? r.json() : null)
          .then((data) => data && setRoadsGeoJson(data))
          .catch(() => {});
      });
  }, []);

  return (
    <PathProvider>
      <div className="app-layout">
        {/* Sidebar */}
        <ControlPanel />

        {/* Map area */}
        <div className="map-area">
          <MapView roadsGeoJson={roadsGeoJson} />

          {/* Backend status badge */}
          {geoError && (
            <div className="map-notice">
              ⚠ Backend offline — roads layer không khả dụng
            </div>
          )}
        </div>
      </div>
    </PathProvider>
  );
}
