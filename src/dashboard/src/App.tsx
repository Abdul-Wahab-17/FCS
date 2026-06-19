import { useCallback, useState } from 'react';
import AlertNotification from './components/AlertNotification';
import AlertTimeline from './components/AlertTimeline';
import HistoricalLog from './components/HistoricalLog';
import LiveFeedMonitor from './components/LiveFeedMonitor';
import Navbar from './components/Navbar';
import { useFetchData } from './hooks/useFetchData';
import { useWebSocket } from './hooks/useWebSocket';
import type { Violation, ViolationFilters } from './types';
import { seedDemo } from './utils/api';

type Tab = 'live' | 'alerts' | 'history';

const TAB_CONFIG: { id: Tab; label: string; icon: string }[] = [
  { id: 'live',    label: 'Live Feed',   icon: '📹' },
  { id: 'alerts',  label: 'Alert Timeline', icon: '🔔' },
  { id: 'history', label: 'Historical Log', icon: '📋' },
];

export default function App() {
  const { violations, setViolations, stats, loading, error, refresh } = useFetchData();
  const [activeTab, setActiveTab] = useState<Tab>('live');
  const [latestAlert, setLatestAlert] = useState<Violation | null>(null);

  const addReports = useCallback(
    (reports: Violation[]) => {
      setViolations((current) => [...reports, ...current]);
      const alert = reports.find((item) =>
        ['HIGH', 'CRITICAL'].includes(item.severity)
      );
      if (alert) setLatestAlert(alert);
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

  const criticalCount = violations.filter((v) => v.severity === 'CRITICAL').length;
  const highCount     = violations.filter((v) => v.severity === 'HIGH').length;

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

      {/* Tabs */}
      <nav className="tabs" aria-label="Dashboard views">
        {TAB_CONFIG.map(({ id, label, icon }) => {
          const count =
            id === 'alerts'
              ? criticalCount + highCount
              : id === 'history'
              ? violations.length
              : null;

          return (
            <button
              key={id}
              className={activeTab === id ? 'active' : ''}
              onClick={() => setActiveTab(id)}
              type="button"
              aria-current={activeTab === id ? 'page' : undefined}
            >
              <span aria-hidden="true">{icon}</span>
              {label}
              {count != null && count > 0 && (
                <span className="tab-count">{count}</span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="content-area">
        {activeTab === 'live' && (
          <LiveFeedMonitor violations={violations} onProcessed={addReports} />
        )}
        {activeTab === 'alerts' && <AlertTimeline violations={violations} />}
        {activeTab === 'history' && (
          <HistoricalLog violations={violations} onFilter={handleFilter} />
        )}
      </div>
    </main>
  );
}
