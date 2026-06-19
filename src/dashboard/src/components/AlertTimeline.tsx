import type { Violation } from '../types';
import { formatBehavior, formatDateTime, percent } from '../utils/formatters';

interface AlertTimelineProps {
  violations: Violation[];
}

const SEVERITY_ICONS: Record<string, string> = {
  LOW:      '🟡',
  MEDIUM:   '🟠',
  HIGH:     '🔴',
  CRITICAL: '🚨',
};

export default function AlertTimeline({ violations }: AlertTimelineProps) {
  const sorted = [...violations].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  return (
    <section className="panel full-panel">
      <div className="panel-header">
        <div>
          <h2>🔔 Alert Timeline</h2>
          <p className="subtle">
            Chronological violation stream · {sorted.length} event
            {sorted.length !== 1 ? 's' : ''} recorded
          </p>
        </div>
        {sorted.length > 0 && (
          <span className="status-pill online">
            {sorted.filter((v) => ['HIGH', 'CRITICAL'].includes(v.severity)).length} Active Alerts
          </span>
        )}
      </div>

      <div className="timeline">
        {sorted.length === 0 ? (
          <div className="empty-state">
            <p style={{ fontSize: 32, margin: '0 0 12px' }}>🛡️</p>
            <p style={{ fontWeight: 600, marginBottom: 4 }}>No violations recorded</p>
            <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              Process a video clip or seed demo data to see events here.
            </p>
          </div>
        ) : (
          sorted.map((violation) => (
            <article
              className={`timeline-item ${violation.severity.toLowerCase()}`}
              key={violation.event_id}
            >
              {/* Left: time + severity */}
              <div className="timeline-time">
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ fontSize: 16 }}>
                    {SEVERITY_ICONS[violation.severity] ?? '⚠️'}
                  </span>
                  <span
                    className={`severity-chip ${violation.severity.toLowerCase()}`}
                    style={{ fontSize: 10 }}
                  >
                    {violation.severity}
                  </span>
                </div>
                <small style={{ color: 'var(--text-secondary)', fontSize: 11, marginTop: 6, display: 'block' }}>
                  {formatDateTime(violation.timestamp)}
                </small>
                <small style={{ color: 'var(--text-muted)', fontSize: 10, fontFamily: 'JetBrains Mono, monospace' }}>
                  {violation.event_id.slice(0, 16)}…
                </small>
              </div>

              {/* Right: content */}
              <div>
                <h3>{formatBehavior(violation.behavior_class)}</h3>
                <p>{violation.event_description}</p>
                <div className="timeline-meta">
                  <span className="badge">📍 {violation.zone}</span>
                  <span className="badge">📜 {violation.policy_rule_ref}</span>
                  {violation.confidence != null && (
                    <span className="badge">
                      🎯 {percent(violation.confidence)} confidence
                    </span>
                  )}
                  {violation.clip_id && (
                    <span className="badge" style={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      🎬 {violation.clip_id}
                    </span>
                  )}
                </div>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
