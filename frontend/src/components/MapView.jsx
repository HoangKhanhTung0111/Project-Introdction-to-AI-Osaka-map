/**
 * Task 4.2 + 4.4 — components/MapView.jsx
 * Leaflet map: lớp nền OSM, roads GeoJSON, markers A/B, Polyline kết quả A*.
 */
import { useEffect, useRef, useCallback } from "react";
import {
  MapContainer, TileLayer, GeoJSON,
  Marker, Polyline, useMapEvents, Tooltip,
} from "react-leaflet";
import L from "leaflet";
import { usePathStore } from "../store/usePathStore";

// Fix Leaflet default icon (CRA issue)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl:       "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl:     "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

// Custom marker icons
function makeIcon(color, label) {
  return L.divIcon({
    className: "",
    html: `
      <div style="
        width:36px;height:36px;border-radius:50% 50% 50% 0;
        background:${color};transform:rotate(-45deg);
        border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.4);
        display:flex;align-items:center;justify-content:center;
      ">
        <span style="transform:rotate(45deg);color:white;font-weight:800;font-size:13px;font-family:sans-serif;">
          ${label}
        </span>
      </div>`,
    iconSize:   [36, 36],
    iconAnchor: [18, 36],
    popupAnchor:[0, -36],
  });
}
const iconA = makeIcon("#6366f1", "A");
const iconB = makeIcon("#f59e0b", "B");

// ── Snap-click handler ────────────────────────────────────────────────────────
function ClickHandler() {
  const { activeMarker, setPointA, setPointB, setActiveMarker } = usePathStore();

  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      if (activeMarker === "A") {
        setPointA({ lat, lon: lng });
        setActiveMarker("B");
      } else {
        setPointB({ lat, lon: lng });
        setActiveMarker("A");
      }
    },
  });
  return null;
}

// ── GeoJSON road style ────────────────────────────────────────────────────────
const roadStyle = {
  color: "#334155",
  weight: 1.5,
  opacity: 0.55,
};

// ── Main Component ─────────────────────────────────────────────────────────────
export default function MapView({ roadsGeoJson }) {
  const { pointA, pointB, result, activeMarker } = usePathStore();

  const center = [21.028, 105.834];   // Trung tâm Hà Nội

  // Path polyline coordinates (Leaflet expects [[lat,lon]])
  const pathCoords = result?.path_coords ?? [];

  // Snap markers from result
  const snapA = result?.node_a;
  const snapB = result?.node_b;

  return (
    <MapContainer
      center={center}
      zoom={13}
      style={{ height: "100%", width: "100%" }}
      zoomControl={false}
    >
      {/* Tile layer */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Task 4.2: Roads GeoJSON layer */}
      {roadsGeoJson && (
        <GeoJSON
          key="roads"
          data={roadsGeoJson}
          style={roadStyle}
        />
      )}

      {/* Click handler */}
      <ClickHandler />

      {/* Marker A — điểm click (trước snap) */}
      {pointA && !result && (
        <Marker position={[pointA.lat, pointA.lon]} icon={iconA}>
          <Tooltip permanent direction="top" offset={[0, -36]}>
            A ({pointA.lat.toFixed(4)}, {pointA.lon.toFixed(4)})
          </Tooltip>
        </Marker>
      )}

      {/* Marker B — điểm click (trước snap) */}
      {pointB && !result && (
        <Marker position={[pointB.lat, pointB.lon]} icon={iconB}>
          <Tooltip permanent direction="top" offset={[0, -36]}>
            B ({pointB.lat.toFixed(4)}, {pointB.lon.toFixed(4)})
          </Tooltip>
        </Marker>
      )}

      {/* Task 4.4: Polyline kết quả */}
      {pathCoords.length > 0 && (
        <Polyline
          positions={pathCoords}
          pathOptions={{
            color: "#6366f1",
            weight: 5,
            opacity: 0.9,
            lineCap: "round",
            lineJoin: "round",
          }}
        />
      )}

      {/* Snap markers (sau khi có kết quả) */}
      {snapA && (
        <Marker position={[snapA.lat, snapA.lon]} icon={iconA}>
          <Tooltip permanent direction="top" offset={[0, -36]}>
            Điểm A (node #{snapA.node_id})
          </Tooltip>
        </Marker>
      )}
      {snapB && (
        <Marker position={[snapB.lat, snapB.lon]} icon={iconB}>
          <Tooltip permanent direction="top" offset={[0, -36]}>
            Điểm B (node #{snapB.node_id})
          </Tooltip>
        </Marker>
      )}

      {/* Cursor hint */}
      <div className={`map-cursor-hint ${activeMarker === "A" ? "hint-a" : "hint-b"}`}>
        Click để đặt điểm <strong>{activeMarker}</strong>
      </div>
    </MapContainer>
  );
}
