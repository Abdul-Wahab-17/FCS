import { useEffect, useState } from 'react';
import type { Violation } from '../types';
import { formatBehavior, formatDateTime, percent } from '../utils/formatters';

interface AlertTimelineProps {
  violations: Violation[];
  rules?: any[];
}

const SEVERITY_ICONS: Record<string, string> = {
  LOW:      '🟡',
  MEDIUM:   '🟠',
  HIGH:     '🔴',
  CRITICAL: '🚨',
};

const PolicyTraceDrawer = ({ violation }: { violation: Violation }) => {
  const [rule, setRule] = useState<any>(null);
  
  useEffect(() => {
    fetch(`/api/policy/rules/${violation.policy_rule_ref}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
         if (data) setRule(data);
      })
      .catch(console.error);
  }, [violation.policy_rule_ref]);
  
  return (
    <div className="policy-trace-drawer" style={{ marginTop: '12px', padding: '12px', background: 'var(--bg-panel-solid)', borderRadius: '8px', border: '1px solid var(--border)' }}>
      <h4 style={{ margin: '0 0 10px', fontSize: '13px', color: 'var(--accent-light)' }}>Policy Grounding — {violation.policy_rule_ref}</h4>
      <div style={{ marginBottom: '8px' }}>
        <label style={{ fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Unsafe Indicator</label>
        <p style={{ margin: '2px 0 0', fontSize: '12px' }}>{rule?.unsafe_indicator ?? '...'}</p>
      </div>
      <div style={{ marginBottom: '8px' }}>
        <label style={{ fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Policy Callout</label>
        <div>
            <span className={`badge ${rule?.policy_callout === 'CRITICAL SAFETY NOTICE' ? 'critical' : 'medium'}`} style={{ marginTop: '4px', display: 'inline-block' }}>
            {rule?.policy_callout ?? '...'}
            </span>
        </div>
      </div>
      <div>
        <label style={{ fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Hazard Description</label>
        <p style={{ margin: '2px 0 0', fontSize: '12px' }}>{rule?.hazard_description ?? '...'}</p>
      </div>
    </div>
  );
};

export default function AlertTimeline({ violations, rules = [] }: AlertTimelineProps) {
  const sorted = [...violations].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
  
  const [expandedTrace, setExpandedTrace] = useState<string | null>(null);

  const toggleTrace = (eventId: string) => {
      if (expandedTrace === eventId) {
          setExpandedTrace(null);
      } else {
          setExpandedTrace(eventId);
      }
  };

  return (
    <section className="panel full-panel">
      <div className="panel-header">
        <div>
          <h2>🔔 Incident Stream</h2>
          <p className="subtle">
            Chronological incident stream · {sorted.length} vector
            {sorted.length !== 1 ? 's' : ''} captured
          </p>
          <div style={{ marginTop: '8px', display: 'flex', gap: '12px', fontSize: '11px' }}>
            <span style={{color: 'var(--text-muted)'}}>Severity Legend:</span>
            <span>🟡 LOW</span>
            <span>🟠 MEDIUM</span>
            <span>🔴 HIGH</span>
            <span>🚨 CRITICAL</span>
          </div>
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
            <p style={{ fontWeight: 600, marginBottom: 4 }}>No incidents logged</p>
            <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              Optical sensors report optimal conditions.
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
                  <button 
                    className="badge" 
                    onClick={() => toggleTrace(violation.event_id)}
                    style={{ cursor: 'pointer', background: 'var(--bg-hover)', border: '1px solid var(--accent)', color: 'var(--accent-light)' }}
                  >
                    📜 {violation.policy_rule_ref} (Trace)
                  </button>
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
                
                {expandedTrace === violation.event_id && (
                    <PolicyTraceDrawer violation={violation} />
                )}
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
