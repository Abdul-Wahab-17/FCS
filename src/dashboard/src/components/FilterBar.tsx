import type { ViolationFilters } from '../types';
import { BEHAVIOR_CLASSES, SEVERITY_ORDER } from '../utils/constants';
import { formatBehavior } from '../utils/formatters';

interface FilterBarProps {
  filters: ViolationFilters;
  onChange: (filters: ViolationFilters) => void;
  onApply: () => void;
  onReset: () => void;
}

export default function FilterBar({
  filters,
  onChange,
  onApply,
  onReset,
}: FilterBarProps) {
  const activeCount = [
    filters.severity,
    filters.behavior_class,
    filters.start_date,
    filters.end_date,
  ].filter(Boolean).length;

  return (
    <div className="filter-bar">
      <label className="field compact">
        <span>Severity</span>
        <select
          value={filters.severity || ''}
          onChange={(e) => onChange({ ...filters, severity: e.target.value })}
        >
          <option value="">All severities</option>
          {SEVERITY_ORDER.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>

      <label className="field compact">
        <span>Behavior</span>
        <select
          value={filters.behavior_class || ''}
          onChange={(e) =>
            onChange({ ...filters, behavior_class: e.target.value })
          }
        >
          <option value="">All behaviors</option>
          {BEHAVIOR_CLASSES.map((b) => (
            <option key={b} value={b}>
              {formatBehavior(b)}
            </option>
          ))}
        </select>
      </label>

      <label className="field compact">
        <span>From date</span>
        <input
          type="date"
          value={filters.start_date || ''}
          onChange={(e) => onChange({ ...filters, start_date: e.target.value })}
        />
      </label>

      <label className="field compact">
        <span>To date</span>
        <input
          type="date"
          value={filters.end_date || ''}
          onChange={(e) => onChange({ ...filters, end_date: e.target.value })}
        />
      </label>

      <button className="button primary" type="button" onClick={onApply}>
        {activeCount > 0 ? `Apply (${activeCount})` : 'Apply'}
      </button>
      <button className="button secondary" type="button" onClick={onReset} disabled={activeCount === 0}>
        Reset
      </button>
    </div>
  );
}
