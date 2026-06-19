import { useMemo, useState } from 'react';
import type { Violation, ViolationFilters } from '../types';
import { exportUrl } from '../utils/api';
import { formatBehavior, formatDateTime, percent } from '../utils/formatters';
import FilterBar from './FilterBar';

interface HistoricalLogProps {
  violations: Violation[];
  onFilter: (filters: ViolationFilters) => void;
}

const PAGE_SIZE = 10;

export default function HistoricalLog({ violations, onFilter }: HistoricalLogProps) {
  const [filters, setFilters] = useState<ViolationFilters>({});
  const [page, setPage] = useState(1);

  const pageCount = Math.max(1, Math.ceil(violations.length / PAGE_SIZE));
  const pageRows = useMemo(
    () => violations.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE),
    [violations, page]
  );

  function applyFilters() {
    setPage(1);
    onFilter(filters);
  }

  function resetFilters() {
    setPage(1);
    setFilters({});
    onFilter({});
  }

  return (
    <section className="panel full-panel">
      <div className="panel-header">
        <div>
          <h2>📋 Historical Log</h2>
          <p className="subtle">
            Searchable compliance records · {violations.length} total
          </p>
        </div>
        <div className="export-group">
          <a
            className="export-link"
            href={exportUrl('csv', filters)}
            download="compliance_export.csv"
            target="_blank"
            rel="noreferrer"
          >
            ↓ CSV
          </a>
          <a
            className="export-link"
            href={exportUrl('json', filters)}
            download="compliance_export.json"
            target="_blank"
            rel="noreferrer"
          >
            ↓ JSON
          </a>
        </div>
      </div>

      <FilterBar
        filters={filters}
        onChange={setFilters}
        onApply={applyFilters}
        onReset={resetFilters}
      />

      <div className="table-wrap">
        <table aria-label="Compliance violation log">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Behavior</th>
              <th>Severity</th>
              <th>Zone</th>
              <th>Confidence</th>
              <th>Policy Ref</th>
            </tr>
          </thead>
          <tbody>
            {pageRows.length === 0 ? (
              <tr>
                <td colSpan={6} className="empty-cell">
                  🔍 No matching records found.
                </td>
              </tr>
            ) : (
              pageRows.map((record) => (
                <tr key={record.event_id} title={record.event_description}>
                  <td style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 12, whiteSpace: 'nowrap' }}>
                    {formatDateTime(record.timestamp)}
                  </td>
                  <td style={{ fontWeight: 600 }}>
                    {formatBehavior(record.behavior_class)}
                  </td>
                  <td>
                    <span className={`severity-chip ${record.severity.toLowerCase()}`}>
                      {record.severity}
                    </span>
                  </td>
                  <td>{record.zone}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div className="confidence-bar" style={{ width: 50 }}>
                        <div
                          className="confidence-bar-fill"
                          style={{ width: `${record.confidence * 100}%` }}
                        />
                      </div>
                      <span style={{ fontSize: 12 }}>{percent(record.confidence)}</span>
                    </div>
                  </td>
                  <td>
                    <span className="badge">{record.policy_rule_ref}</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="pagination">
        <button
          className="button secondary"
          type="button"
          disabled={page === 1}
          onClick={() => setPage((v) => Math.max(1, v - 1))}
        >
          ← Prev
        </button>
        <span className="page-info">
          Page {page} / {pageCount}
        </span>
        <button
          className="button secondary"
          type="button"
          disabled={page === pageCount}
          onClick={() => setPage((v) => Math.min(pageCount, v + 1))}
        >
          Next →
        </button>
      </div>
    </section>
  );
}
