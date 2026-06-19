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
  const [showArchive, setShowArchive] = useState(false);
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
        <div className="view-actions" style={{ display: 'flex', justifyContent: 'flex-end', margin: '0 0 16px', gap: '12px' }}>
            <button 
                className={`button ${!showArchive ? 'primary' : 'secondary'}`}
                onClick={() => setShowArchive(false)}
            >
                <Activity size={16} /> Operations Matrix
            </button>
            <button 
                className={`button ${showArchive ? 'primary' : 'secondary'}`}
                onClick={() => setShowArchive(true)}
            >
                <History size={16} /> Compliance Archive
            </button>
        </div>

        {!showArchive ? (
            <div className="dashboard-grid">
                <div className="main-feed-column">
                    <LiveFeedMonitor onProcessed={addReports} />
                </div>
                <div className="sidebar-column">
                    <AlertTimeline violations={violations} rules={rules} />
                </div>
            </div>
        ) : (
            <HistoricalLog violations={violations} onFilter={handleFilter} />
        )}
      </div>
    </main>
  );
}
