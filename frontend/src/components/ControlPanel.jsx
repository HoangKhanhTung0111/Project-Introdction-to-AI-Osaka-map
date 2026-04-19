/**
 * Task 4.3 — components/ControlPanel.jsx
 * Sidebar: input A/B, chọn thuật toán, nút Tìm đường, hiển thị kết quả.
 */
import { usePathStore } from "../store/usePathStore";

function CoordBadge({ point, label, color, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`coord-badge ${active ? "coord-badge--active" : ""}`}
      style={{ "--badge-color": color }}
    >
      <span className="coord-badge__label" style={{ background: color }}>
        {label}
      </span>
      <span className="coord-badge__value">
        {point
          ? `${point.lat.toFixed(5)}, ${point.lon.toFixed(5)}`
          : <em>Click trên bản đồ…</em>}
      </span>
      {point && <span className="coord-badge__clear" title="Xóa">✕</span>}
    </button>
  );
}

function StatItem({ icon, label, value, unit, highlight }) {
  return (
    <div className={`stat-item ${highlight ? "stat-item--highlight" : ""}`}>
      <span className="stat-item__icon">{icon}</span>
      <div>
        <div className="stat-item__label">{label}</div>
        <div className="stat-item__value">
          {value} <span className="stat-item__unit">{unit}</span>
        </div>
      </div>
    </div>
  );
}

export default function ControlPanel() {
  const {
    pointA, pointB, algorithm, result,
    loading, error, activeMarker,
    setPointA, setPointB, setAlgorithm,
    setActiveMarker, swapPoints, clear, findPath,
  } = usePathStore();

  const canFind = pointA && pointB && !loading;
  const distKm  = result ? (result.total_distance_m / 1000).toFixed(2) : null;
  const distM   = result ? Math.round(result.total_distance_m) : null;

  return (
    <aside className="panel">
      {/* Header */}
      <div className="panel__header">
        <div className="panel__logo">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.93 4.93l2.12 2.12M16.95 16.95l2.12 2.12M4.93 19.07l2.12-2.12M16.95 7.05l2.12-2.12"/>
          </svg>
          Pathfinder
        </div>
        <span className="panel__subtitle">Tìm đường ngắn nhất</span>
      </div>

      {/* Algorithm selector */}
      <div className="section">
        <label className="section__label">Thuật toán</label>
        <div className="algo-pills">
          {["astar", "dijkstra"].map((algo) => (
            <button
              key={algo}
              onClick={() => setAlgorithm(algo)}
              className={`algo-pill ${algorithm === algo ? "algo-pill--active" : ""}`}
            >
              {algo === "astar" ? "A* (nhanh hơn)" : "Dijkstra"}
            </button>
          ))}
        </div>
      </div>

      {/* Points A / B */}
      <div className="section">
        <label className="section__label">Chọn điểm trên bản đồ</label>

        <CoordBadge
          label="A"
          color="#6366f1"
          point={pointA}
          active={activeMarker === "A"}
          onClick={() => {
            if (pointA) setPointA(null);
            setActiveMarker("A");
          }}
        />

        {/* Swap button */}
        <button
          className="swap-btn"
          onClick={swapPoints}
          title="Đổi A ↔ B"
          disabled={!pointA || !pointB}
        >
          ⇅
        </button>

        <CoordBadge
          label="B"
          color="#f59e0b"
          point={pointB}
          active={activeMarker === "B"}
          onClick={() => {
            if (pointB) setPointB(null);
            setActiveMarker("B");
          }}
        />
      </div>

      {/* Actions */}
      <div className="section section--actions">
        <button
          className="btn btn--primary"
          onClick={findPath}
          disabled={!canFind}
        >
          {loading ? (
            <><span className="spinner" /> Đang tính…</>
          ) : (
            <><span>🔍</span> Tìm đường</>
          )}
        </button>
        <button className="btn btn--ghost" onClick={clear}>
          Xóa tất cả
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="alert alert--error">
          <span>⚠</span> {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="result-box">
          <div className="result-box__title">
            <span className="result-box__check">✓</span>
            Tìm thấy đường đi
          </div>

          <div className="stats-grid">
            <StatItem
              icon="📏"
              label="Tổng quãng đường"
              value={distKm}
              unit="km"
              highlight
            />
            <StatItem
              icon="🔢"
              label="Số điểm nút"
              value={result.path_nodes.length}
              unit="nodes"
            />
            <StatItem
              icon="⚡"
              label="Thuật toán"
              value={result.algorithm_used.toUpperCase()}
              unit=""
            />
            <StatItem
              icon="📍"
              label="Snap A → node"
              value={`#${result.node_a.node_id}`}
              unit={`(${result.node_a.distance_m}m)`}
            />
            <StatItem
              icon="📍"
              label="Snap B → node"
              value={`#${result.node_b.node_id}`}
              unit={`(${result.node_b.distance_m}m)`}
            />
          </div>

          {/* Node path preview */}
          <div className="path-preview">
            <div className="path-preview__label">Chuỗi nodes:</div>
            <div className="path-preview__nodes">
              {result.path_nodes.slice(0, 8).map((n, i) => (
                <span key={i} className="node-chip">{n}</span>
              ))}
              {result.path_nodes.length > 8 && (
                <span className="node-chip node-chip--more">
                  +{result.path_nodes.length - 8}
                </span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Help */}
      {!pointA && !pointB && (
        <div className="help-box">
          <p>👆 Click bản đồ để đặt điểm <strong>A</strong>, rồi click tiếp để đặt điểm <strong>B</strong>.</p>
          <p>Backend sẽ tự động snap sang node đường gần nhất.</p>
        </div>
      )}
    </aside>
  );
}
