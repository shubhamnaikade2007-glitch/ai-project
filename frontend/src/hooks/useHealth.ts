// HealthFit AI - useHealth Hook
import { useState, useEffect, useCallback } from 'react';
import HealthService from '../services/health.service';
import { HealthMetric, HealthSummary, OrganHealthScore } from '../types';

export const useHealth = (autoFetch = true) => {
  const [summary, setSummary]           = useState<HealthSummary | null>(null);
  const [latestMetrics, setLatest]      = useState<Record<string, HealthMetric>>({});
  const [organScores, setOrganScores]   = useState<OrganHealthScore[]>([]);
  const [loading, setLoading]           = useState(false);
  const [error, setError]               = useState<string | null>(null);

  const fetchSummary = useCallback(async (days = 7) => {
    setLoading(true); setError(null);
    try {
      const data = await HealthService.getHealthSummary(days);
      setSummary(data);
      setLatest(data.latest_metrics || {});
    } catch (e: any) {
      setError(e.response?.data?.error || 'Failed to load health data');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchOrganScores = useCallback(async () => {
    try {
      const { scores } = await HealthService.getOrganScores();
      setOrganScores(scores);
    } catch {}
  }, []);

  const addMetric = useCallback(async (
    metric_type: string, value: number, unit?: string, source = 'manual'
  ) => {
    const result = await HealthService.addMetric({ metric_type, value, unit, source });
    await fetchSummary();
    return result;
  }, [fetchSummary]);

  useEffect(() => {
    if (autoFetch) {
      fetchSummary();
      fetchOrganScores();
    }
  }, [autoFetch, fetchSummary, fetchOrganScores]);

  return { summary, latestMetrics, organScores, loading, error, fetchSummary, fetchOrganScores, addMetric };
};
