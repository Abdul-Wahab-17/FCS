import { useCallback, useState } from 'react';
import { History, Activity } from 'lucide-react';
import AlertNotification from './components/AlertNotification';
import AlertTimeline from './components/AlertTimeline';
import HistoricalLog from './components/HistoricalLog';
import LiveFeedMonitor from './components/LiveFeedMonitor';
import Navbar from './components/Navbar';
import { useFetchData } from './hooks/useFetchData';
import { useWebSocket } from './hooks/useWebSocket';
import type { Violation, ViolationFilters } from './types';
import { seedDemo } from './utils/api';

export default function App() {
  const { violations, setViolations, stats, rules, loading, error, refresh } = useFetchData();
  const [activeTab, setActiveTab] = useState<'operations' | 'stats' | 'history'>('operations');
  const [latestAlert, setLatestAlert] = useState<Violation | null>(null);
  const [currentVideoReports, setCurrentVideoReports] = useState<Violation[]>([]);

  const addReports = useCallback(
    (reports: Violation[]) => {
      setViolations((current) => [...reports, ...current]);
      const alert = reports.find((item) =>
        ['HIGH', 'CRITICAL'].includes(item.severity)
      );
      if (alert) setLatestAlert(alert);
      setCurrentVideoReports(reports);
      refresh();
    },
    [refresh, setViolations]
  );

  useWebSocket(
    useCallback(
      (alert: Violation) => {
        setLatestAlert(alert);
        setViolations((current) => [alert, ...current]);
      },
      [setViolations]
    )
  );

  async function handleSeedDemo() {
    const result = await seedDemo();
    addReports(result.reports);
  }

  function handleFilter(filters: ViolationFilters) {
    refresh(filters);
  }

  return (
    <main className="app-shell">
      <Navbar
        stats={stats}
        loading={loading}
        error={error}
        onSeedDemo={handleSeedDemo}
        onRefresh={() => refresh()}
      />

      <AlertNotification
        alert={latestAlert}
        onDismiss={() => setLatestAlert(null)}
      />

      <div className="content-area">
        <div className="view-actions" style={{ display: 'flex', justifyContent: 'flex-start', margin: '0 0 16px', gap: '8px' }}>
            <button 
                className={`button ${activeTab === 'operations' ? 'primary' : 'secondary'}`}
                onClick={() => setActiveTab('operations')}
            >
                <Activity size={16} /> Video Analysis
            </button>
            <button 
                className={`button ${activeTab === 'stats' ? 'primary' : 'secondary'}`}
                onClick={() => setActiveTab('stats')}
            >
                <Activity size={16} /> Stats
            </button>
            <button 
                className={`button ${activeTab === 'history' ? 'primary' : 'secondary'}`}
                onClick={() => setActiveTab('history')}
            >
                <History size={16} /> History
            </button>
        </div>

        {activeTab === 'operations' && (
            <div className="dashboard-grid">
                <div className="main-feed-column">
                    <LiveFeedMonitor onProcessed={addReports} />
                </div>
                <div className="sidebar-column">
                    <AlertTimeline violations={currentVideoReports} rules={rules} />
                </div>
            </div>
        )}
        
        {activeTab === 'stats' && (
          <div className="stats-tab-content">
            <h2>System Metrics</h2>
            <div className="topbar-metrics" style={{ marginTop: 24 }}>
              <div className="metric-pill total"><strong>{stats.total ?? 0}</strong><small>Total Detections</small></div>
              <div className="metric-pill low-m"><strong>{stats.by_severity?.LOW ?? 0}</strong><small>Low Severity</small></div>
              <div className="metric-pill med-m"><strong>{stats.by_severity?.MEDIUM ?? 0}</strong><small>Medium Severity</small></div>
              <div className="metric-pill high-m"><strong>{stats.by_severity?.HIGH ?? 0}</strong><small>High Severity</small></div>
              <div className="metric-pill crit-m"><strong>{stats.by_severity?.CRITICAL ?? 0}</strong><small>Critical Severity</small></div>
            </div>
            <h3 style={{ marginTop: 32 }}>Detections for Current Video</h3>
            <ul className="current-detections-list" style={{ marginTop: 12 }}>
              {currentVideoReports.reduce((map, report) => {
                // keep highest confidence per behavior class
                const existing = map.get(report.behavior_class);
                if (!existing || report.confidence > existing.confidence) {
                  map.set(report.behavior_class, report);
                }
                return map;
              }, new Map<string, typeof currentVideoReports[0]>())
                .values()
                .map((r) => (
                  <li key={r.event_id} style={{ marginBottom: 8 }}>
                    <strong>{r.behavior_class}</strong>: {Math.round(r.confidence * 100)}% confidence ({r.severity})
                  </li>
                ))}
            </ul>
          </div>
        )}

        {activeTab === 'history' && (
            <HistoricalLog violations={violations} onFilter={handleFilter} />
        )}
      </div>
    </main>
  );
}
