import type { DashboardStats } from '../types';

interface NavbarProps {
  stats: DashboardStats;
  loading: boolean;
  error: string | null;
  onSeedDemo: () => void;
  onRefresh: () => void;
}

export default function Navbar({
  stats,
  loading,
  error,
  onSeedDemo,
  onRefresh,
}: NavbarProps) {
  const bySev = stats.by_severity ?? {};

  return (
    <header className="topbar">
      {/* Brand */}
      <div className="topbar-brand">
        <div className="brand-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 1L3 5v6c0 5.25 3.75 10.15 9 11.25C17.25 21.15 21 16.25 21 11V5L12 1zm0 2.18l7 3.12V11c0 4.33-2.92 8.4-7 9.63-4.08-1.23-7-5.3-7-9.63V6.3l7-3.12zM11 7v6h2V7h-2zm0 8v2h2v-2h-2z"/>
          </svg>
        </div>
        <div>
          <h1>FactoryGuard</h1>
          <div className="live-indicator">
            <span className="live-dot" />
            Live Monitoring
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="topbar-metrics" aria-live="polite">
        <div className="metric-pill total">
          <strong>{stats.total ?? 0}</strong>
          <small>Total</small>
        </div>
        <div className="metric-pill low-m">
          <strong>{bySev.LOW ?? 0}</strong>
          <small>Low</small>
        </div>
        <div className="metric-pill med-m">
          <strong>{bySev.MEDIUM ?? 0}</strong>
          <small>Medium</small>
        </div>
        <div className="metric-pill high-m">
          <strong>{bySev.HIGH ?? 0}</strong>
          <small>High</small>
        </div>
        <div className="metric-pill crit-m">
          <strong>{bySev.CRITICAL ?? 0}</strong>
          <small>Critical</small>
        </div>
      </div>

      {/* Actions */}
      <div className="topbar-actions">
        {error && <span className="status-text error">⚠ {error}</span>}
        {loading && (
          <span className="status-text" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span className="spinner" /> Loading
          </span>
        )}
        <button className="button secondary" onClick={onRefresh} type="button">
          ↻ Refresh
        </button>
        <button className="button primary" onClick={onSeedDemo} type="button">
          ⚡ Seed Demo
        </button>
      </div>
    </header>
  );
}
