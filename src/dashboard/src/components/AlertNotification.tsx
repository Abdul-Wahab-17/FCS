import type { Violation } from '../types';
import { formatBehavior, formatDateTime } from '../utils/formatters';

interface AlertNotificationProps {
  alert: Violation | null;
  onDismiss: () => void;
}

export default function AlertNotification({
  alert,
  onDismiss,
}: AlertNotificationProps) {
  if (!alert || !['HIGH', 'CRITICAL'].includes(alert.severity)) return null;

  const isCritical = alert.severity === 'CRITICAL';

  return (
    <div
      className={`alert-notification ${alert.severity.toLowerCase()}`}
      role="alert"
      aria-live="assertive"
    >
      <div className="alert-notification-body">
        <span className="alert-icon" aria-hidden="true">
          {isCritical ? '🚨' : '⚠️'}
        </span>
        <div className="alert-notification-text">
          <strong>
            {isCritical ? '🔴 CRITICAL SAFETY ALERT' : '🟠 HIGH SEVERITY ALERT'}
          </strong>
          <span>{formatBehavior(alert.behavior_class)}</span>
          <small>
            {alert.zone} · {formatDateTime(alert.timestamp)} · {alert.policy_rule_ref}
          </small>
        </div>
      </div>
      <button
        className="icon-button"
        onClick={onDismiss}
        type="button"
        aria-label="Dismiss alert"
      >
        ✕
      </button>
    </div>
  );
}
