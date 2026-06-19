import { useCallback, useEffect, useState } from 'react';
import { fetchStats, fetchViolations } from '../utils/api';
import type { DashboardStats, Violation, ViolationFilters } from '../types';

export function useFetchData() {
  const [violations, setViolations] = useState<Violation[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    total: 0,
    by_severity: {},
    by_behavior: {}
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async (filters: ViolationFilters = {}) => {
    setLoading(true);
    setError(null);
    try {
      const [nextViolations, nextStats] = await Promise.all([
        fetchViolations(filters),
        fetchStats()
      ]);
      setViolations(nextViolations);
      setStats(nextStats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { violations, setViolations, stats, loading, error, refresh };
}
