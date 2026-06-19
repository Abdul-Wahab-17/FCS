import { useCallback, useEffect, useState } from 'react';
import { fetchStats, fetchViolations, fetchPolicyRules } from '../utils/api';
import type { DashboardStats, Violation, ViolationFilters } from '../types';

export function useFetchData() {
  const [violations, setViolations] = useState<Violation[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    total: 0,
    by_severity: {},
    by_behavior: {}
  });
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async (filters: ViolationFilters = {}) => {
    setLoading(true);
    setError(null);
    try {
      const [nextViolations, nextStats, nextRules] = await Promise.all([
        fetchViolations(filters),
        fetchStats(),
        fetchPolicyRules().catch(() => ({ compliance_rules: [] })) // Fallback if API missing
      ]);
      setViolations(nextViolations);
      setStats(nextStats);
      if (nextRules && nextRules.compliance_rules) {
          setRules(nextRules.compliance_rules);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { violations, setViolations, stats, rules, loading, error, refresh };
}
