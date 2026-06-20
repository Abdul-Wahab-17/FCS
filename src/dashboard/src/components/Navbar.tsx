import { AlertTriangle, RefreshCw, Zap } from 'lucide-react';
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
          <h1>Nexus Compliance Core</h1>
        </div>
      </div>

      {/* Actions */}
      <div className="topbar-actions">
        {error && <span className="status-text error" style={{ display: 'flex', alignItems: 'center', gap: 6 }}><AlertTriangle size={16} /> {error}</span>}
        {loading && (
          <span className="status-text" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span className="spinner" /> Loading
          </span>
        )}
      </div>
    </header>
  );
}
